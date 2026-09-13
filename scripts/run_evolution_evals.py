#!/usr/bin/env python3
"""Run sequential maintenance trials. Use: python -m scripts.run_evolution_evals.

The operator must supply a sandboxed protocol-2 adapter. This runner is NOT a sandbox.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

from scripts.run_task_evals import ARMS, ROOT, prepare, run_process

SCENARIOS = ROOT / "evals/evolution"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def save(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def git(workspace: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(workspace), *args], text=True
    ).strip()


def load_scenario(name: str) -> dict:
    if not NAME.fullmatch(name):
        raise ValueError("Invalid scenario name")
    path = SCENARIOS / f"{name}.json"
    scenario = json.loads(path.read_text())
    if scenario.get("id") != name or not scenario.get("stages"):
        raise ValueError("Scenario ID/stages missing")
    seen = set()
    for stage in scenario["stages"]:
        stage_id = stage.get("id", "")
        if not NAME.fullmatch(stage_id) or stage_id in seen or not stage.get("prompt"):
            raise ValueError("Invalid or duplicate stage")
        seen.add(stage_id)
    for skill in scenario["skills"]:
        if not NAME.fullmatch(skill) or not (ROOT / ".agents/skills" / skill / "SKILL.md").is_file():
            raise ValueError(f"Unknown skill: {skill}")
    oracle = scenario["oracle"]
    if Path(oracle).name != oracle or not (SCENARIOS / oracle).is_file():
        raise ValueError("Invalid oracle")
    seed = scenario["seed"]
    if not NAME.fullmatch(seed):
        raise ValueError("Invalid seed name")
    source = SCENARIOS / "seeds" / seed
    files = {}
    for item in sorted(source.rglob("*")):
        if item.is_symlink():
            raise ValueError("Fixture symlinks are not supported")
        if item.is_file():
            files[item.relative_to(source).as_posix()] = item.read_text()
    if not files:
        raise ValueError("Empty or missing seed")
    scenario["files"] = files
    return scenario


def validate_metadata(directory: Path, model: str, harness: str,
                      team: list, conversations: set[str]) -> dict:
    metadata = json.loads((directory / "metadata.json").read_text())
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be an object")
    if (metadata.get("resolved_model") != model or metadata.get("harness") != harness
            or not metadata.get("harness_version") or metadata.get("team") != team):
        raise ValueError("Model/harness/team mismatch")
    conversation = metadata.get("conversation_id")
    if (not isinstance(conversation, str) or not conversation
            or conversation in conversations or metadata.get("context_mode") != "fresh"):
        raise ValueError("Fresh, distinct conversations are required")
    trace = (directory / "trace.jsonl").read_bytes()
    lines = trace.decode().splitlines()
    if not lines or not all(isinstance(json.loads(line), dict) for line in lines):
        raise ValueError("Missing or invalid trace")
    conversations.add(conversation)
    return {"adapter_metadata": metadata, "trace_sha256": digest(trace)}


def run_sequence(scenario: dict, arm: str, destination: Path, adapter: list[str],
                 model: str, harness: str, team: list, baseline: Path | None,
                 timeout: float) -> dict:
    """Retain candidate files, reset conversations, and stop on a failed checkpoint."""
    destination = destination.resolve()
    if destination.exists():
        raise ValueError("Trial output must be new; never overwrite evidence")
    destination.mkdir(parents=True)
    workspace = destination / "workspace"
    prepare(scenario, arm, workspace, baseline)
    contract = (workspace / "AGENTS.md").read_bytes()
    commands = (workspace / "COMMANDS.md").read_bytes()
    oracle = SCENARIOS / scenario["oracle"]
    result = {
        "schema_version": 1, "scenario": scenario["id"], "arm": arm,
        "scenario_sha256": digest(json.dumps(scenario, sort_keys=True).encode()),
        "oracle_sha256": digest(oracle.read_bytes()),
        "runner_sha256": digest(Path(__file__).read_bytes()),
        "requested_model": model, "requested_harness": harness, "requested_team": team,
        "initial_commit": git(workspace, "rev-parse", "HEAD"),
        "behavior_review": "pending", "status": "incomplete", "stages": [],
    }
    requirements = []
    conversations: set[str] = set()
    for stage in scenario["stages"]:
        directory = destination / stage["id"]
        directory.mkdir()
        previous = "\n\n".join(requirements)
        task = ("Retain the current repository; this is a new conversation, not a fresh codebase.\n"
                f"Previously accepted requirements (new changes below supersede conflicts):\n{previous}\n\n"
                f"Current task:\n{stage['prompt']}")
        payload = {
            "protocol": 2, "workspace": str(workspace), "task": task,
            "stage_id": stage["id"], "fresh_conversation": True,
            "requested_model": model, "requested_harness": harness, "requested_team": team,
            "trace_path": str(directory / "trace.jsonl"),
            "metadata_path": str(directory / "metadata.json"),
        }
        checkpoint = {"id": stage["id"], "functional": "not-evaluated",
                      "status": "incomplete", "before": git(workspace, "rev-parse", "HEAD")}
        result["stages"].append(checkpoint)
        try:
            invocation = run_process(adapter, workspace, payload, timeout)
            save(directory / "adapter.json", invocation)
            checkpoint["seconds"] = invocation["seconds"]
            if invocation["status"] != "exited" or invocation["exit_code"] != 0:
                raise ValueError("Agent invocation failed or timed out")
            checkpoint.update(validate_metadata(directory, model, harness, team, conversations))
            if ((workspace / "AGENTS.md").read_bytes() != contract
                    or (workspace / "COMMANDS.md").read_bytes() != commands):
                raise ValueError("The trial's governing contract was modified")
            proof = run_process([sys.executable, "-S", str(oracle), str(workspace), stage["id"]],
                                directory, None, timeout)
            save(directory / "oracle.json", proof)
            checkpoint["functional"] = (
                "pass" if proof["status"] == "exited" and proof["exit_code"] == 0 else "fail"
            )
            git(workspace, "add", "-A")
            (directory / "change.patch").write_text(git(workspace, "diff", "--cached", "HEAD"))
            git(workspace, "-c", "user.name=Evolution Eval", "-c", "user.email=eval@example.invalid",
                "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", stage["id"])
            checkpoint["after"] = git(workspace, "rev-parse", "HEAD")
            checkpoint["tree"] = git(workspace, "rev-parse", "HEAD^{tree}")
            checkpoint["status"] = ("needs-behavior-review" if checkpoint["functional"] == "pass"
                                    else "functional-failure")
        except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
            checkpoint["limit"] = str(exc)
        save(directory / "result.json", checkpoint)
        save(destination / "result.json", result)
        if checkpoint["status"] != "needs-behavior-review":
            break
        requirements.append(stage["prompt"])
    if (len(result["stages"]) == len(scenario["stages"])
            and all(s["status"] == "needs-behavior-review" for s in result["stages"])):
        result["status"] = "needs-behavior-review"
    save(destination / "result.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--adapter-json", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--harness", required=True)
    parser.add_argument("--team-json", default="[]", help="Exact ordered worker role/model declarations")
    parser.add_argument("--arm", choices=ARMS, default="selective")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout", type=float, default=600)
    parser.add_argument("--sandbox-confirmed", action="store_true")
    args = parser.parse_args()
    try:
        if not args.sandbox_confirmed:
            raise ValueError("Authorize and provide a sandboxed adapter; this runner is not a sandbox")
        adapter, team = json.loads(args.adapter_json), json.loads(args.team_json)
        if not isinstance(adapter, list) or not adapter or not all(isinstance(a, str) and a for a in adapter):
            raise ValueError("adapter-json must be a nonempty argv list")
        if not isinstance(team, list) or any(
            not isinstance(t, dict) or set(t) != {"role", "model"}
            or not all(isinstance(v, str) and v for v in t.values()) for t in team
        ):
            raise ValueError("team-json must contain role/model objects")
        if not math.isfinite(args.timeout) or args.timeout <= 0:
            raise ValueError("timeout must be finite and positive")
        result = run_sequence(load_scenario(args.scenario), args.arm, args.output, adapter,
                              args.model, args.harness, team, args.baseline, args.timeout)
        print(json.dumps({"status": result["status"], "behavior_review": "pending"}))
        return 0 if result["status"] == "needs-behavior-review" else 1
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f"evolution-evals: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
