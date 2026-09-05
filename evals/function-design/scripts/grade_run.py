#!/usr/bin/env python3
"""Grade a supplied workspace with existing oracles; never invoke a model.

Run generated code only inside the operator's disposable sandbox. A subprocess
and timeout are not a security boundary. Metadata identifies a run; it does not
prove which model authored the candidate or measure agent execution cost.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time


REQUIRED_LABELS = (
    "run_id", "model", "harness", "effort", "environment", "playbook_commit",
    "instructions_sha256",
)


def validate_metadata(metadata: dict) -> None:
    if not isinstance(metadata, dict):
        raise ValueError("run metadata must be an object")
    for key in REQUIRED_LABELS:
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            raise ValueError(f"run metadata requires a nonempty {key}")
    if metadata.get("kind") not in {"agent-run", "calibration"}:
        raise ValueError("kind must be agent-run or calibration")
    if metadata.get("variant") not in {"minimal", "core", "full"}:
        raise ValueError("variant must be minimal, core, or full")
    if type(metadata.get("trial")) is not int or metadata["trial"] < 1:
        raise ValueError("trial must be a positive integer")
    for key, size in (("playbook_commit", 40), ("instructions_sha256", 64)):
        if not re.fullmatch(rf"[0-9a-f]{{{size}}}", metadata[key]):
            raise ValueError(f"{key} must be a {size}-character lowercase hex digest")


def snapshot(root: Path) -> dict[str, bytes]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError(f"expected a real directory: {root}")
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symlinks are not accepted in graded inputs: {path}")
        if path.is_file() and "__pycache__" not in path.parts:
            files[path.relative_to(root).as_posix()] = path.read_bytes()
    return files


def digest(files: dict[str, bytes]) -> str:
    manifest = {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}
    return hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()


def write_snapshot(root: Path, files: dict[str, bytes]) -> None:
    for name, data in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def source_delta(before: dict[str, bytes], after: dict[str, bytes]) -> dict:
    changed = [name for name in sorted(before.keys() | after.keys())
               if before.get(name) != after.get(name)]
    added = removed = 0
    for name in changed:
        old = before.get(name, b"").decode("utf-8", errors="replace").splitlines()
        new = after.get(name, b"").decode("utf-8", errors="replace").splitlines()
        for line in difflib.ndiff(old, new):
            added += line.startswith("+ ")
            removed += line.startswith("- ")
    return {"changed_files": changed, "lines_added": added, "lines_removed": removed}


def run_oracle(oracle: Path, workspace: Path, timeout: float) -> tuple[bool, str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("PYTHONPATH", None)
    env.pop("PYTHONHOME", None)
    env["PYTHONNOUSERSITE"] = "1"
    try:
        result = subprocess.run(
            [sys.executable, str(oracle), str(workspace)], cwd=workspace,
            env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            timeout=timeout, check=False,
        )
    except subprocess.TimeoutExpired:
        return False, "FAIL: oracle timed out; the sandbox must enforce process-tree limits"
    nonempty_suite = re.search(r"\bRan [1-9][0-9]* tests?\b", result.stdout)
    passed = result.returncode == 0 and nonempty_suite is not None
    output = result.stdout
    if not nonempty_suite:
        output += "\nFAIL: no nonempty unittest execution evidence"
    return passed, output


def grade_run(repo_root: Path, scenario_id: str, workspace: Path,
              metadata: dict, timeout: float = 60) -> dict:
    validate_metadata(metadata)
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("oracle timeout must be positive and finite")
    root = repo_root.resolve() / "evals/function-design"
    scenarios = json.loads((root / "scenarios.json").read_text())["scenarios"]
    matches = [case for case in scenarios if case["id"] == scenario_id]
    if len(matches) != 1:
        raise ValueError(f"expected exactly one known scenario: {scenario_id}")
    fixture = (root / matches[0]["fixture"]).resolve()
    if not fixture.is_relative_to(root):
        raise ValueError("fixture escapes the trusted corpus")
    workspace = workspace.resolve()
    source = snapshot(workspace / "src")
    if not source:
        raise ValueError("candidate source is empty")
    baseline = snapshot(fixture / "src")
    tests = snapshot(fixture / "expected/good/tests")
    if not any(Path(name).match("test*.py") for name in tests):
        raise ValueError("trusted acceptance tests are missing")
    oracle = fixture / "oracle.py"
    oracle_bytes = oracle.read_bytes()
    helpers_sha256 = digest(snapshot(root / "scripts"))
    task_sha256 = hashlib.sha256((fixture / "task.md").read_bytes()).hexdigest()
    judged = {f"src/{name}": data for name, data in source.items()}
    judged.update({f"tests/{name}": data for name, data in tests.items()})
    ledger = workspace / ".agents/design-ledger/function-boundaries.md"
    if any(path.is_symlink() for path in (ledger, ledger.parent, ledger.parent.parent)):
        raise ValueError("candidate ledger must not traverse symlinks")
    if ledger.is_file():
        judged[".agents/design-ledger/function-boundaries.md"] = ledger.read_bytes()
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="playbook-grade-") as directory:
        frozen = Path(directory)
        write_snapshot(frozen, judged)
        passed, output = run_oracle(oracle, frozen, timeout)
    return {
        "version": 1,
        "scenario": scenario_id,
        "metadata": metadata,
        "metadata_provenance": "supplied by caller; not model-authorship attestation",
        "source_sha256": digest(source),
        "judged_inputs_sha256": digest(judged),
        "baseline_sha256": digest(baseline),
        "trusted_tests_sha256": digest(tests),
        "oracle_sha256": hashlib.sha256(oracle_bytes).hexdigest(),
        "oracle_helpers_sha256": helpers_sha256,
        "task_sha256": task_sha256,
        "python_version": sys.version,
        "source_delta": source_delta(baseline, source),
        "oracle_result": "pass" if passed else "fail",
        "oracle_wall_seconds": round(time.monotonic() - started, 4),
        "oracle_output": output,
        "claim_limit": "candidate outcome only; no agent latency/cost or general quality claim",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--run-metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=60,
                        help="Oracle timeout, not a development-work budget")
    args = parser.parse_args(argv)
    try:
        out = args.out.resolve()
        corpus = args.repo_root.resolve() / "evals/function-design"
        if out.is_relative_to(args.workspace.resolve()) or out.is_relative_to(corpus):
            raise ValueError("report must be outside the candidate and trusted corpus")
        if out.exists():
            raise ValueError("report already exists; use a new run output path")
        metadata = json.loads(args.run_metadata.read_text(encoding="utf-8"))
        report = grade_run(args.repo_root, args.scenario, args.workspace, metadata, args.timeout)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"grade-run: {exc}", file=sys.stderr)
        return 2
    print(f"grade-run: {report['oracle_result']} -> {out}")
    return 0 if report["oracle_result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
