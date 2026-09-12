#!/usr/bin/env python3
"""Prepare or execute matched evaluations using an explicitly supplied sandbox adapter."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ("minimal", "specialists", "baseline")


def tree_digest(root: Path) -> str:
    h = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if any(part in {".git", "__pycache__"} for part in path.relative_to(root).parts) or path.suffix in {".pyc", ".pyo"}:
            continue
        if path.is_symlink():
            raise ValueError("evaluation snapshots must not contain symlinks")
        if path.is_file():
            h.update(path.relative_to(root).as_posix().encode() + b"\0")
            h.update(hashlib.sha256(path.read_bytes()).digest())
    return h.hexdigest()


def copy_overlay(source: Path, dest: Path) -> None:
    # Preflight collisions; a baseline must not replace product fixture files.
    tree_digest(source)
    for item in source.iterdir():
        if item.name in {".git", "__pycache__"} or item.suffix in {".pyc", ".pyo"}:
            continue
        if (dest / item.name).exists() or (dest / item.name).is_symlink():
            raise ValueError(f"baseline overlay collides with fixture: {item.name}")
    shutil.copytree(source, dest, dirs_exist_ok=True, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))


def prepare(root: Path, case: dict[str, Any], workspace: Path, variant: str,
            baseline: Path | None) -> str:
    if variant not in VARIANTS:
        raise ValueError("unknown variant")
    workspace.mkdir(parents=True, exist_ok=False)
    if case.get("fixture"):
        shutil.copytree(root / "evals/fixtures" / case["fixture"], workspace, dirs_exist_ok=True)
    if variant == "baseline":
        if baseline is None or not (baseline / "AGENTS.md").is_file():
            raise ValueError("baseline needs an explicit, prepared instruction overlay with AGENTS.md")
        copy_overlay(baseline, workspace)
    else:
        shutil.copyfile(root / "templates/AGENTS.md", workspace / "AGENTS.md")
        if variant == "specialists":
            for name in case["skills"]:
                source = root / "skills" / name
                tree_digest(source)
                shutil.copytree(source, workspace / ".agents/skills" / name, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", "*.pyo"))
    return tree_digest(workspace)


def run_case(root: Path, case: dict[str, Any], workspace: Path, receipt: Path,
             adapter: list[str], model: str, variant: str, timeout: float,
             before: str) -> dict[str, Any]:
    request = {"protocol": 1, "phase": "agent", "task": case["prompt"], "workspace": str(workspace.resolve()),
               "model": model, "variant": variant}
    started = time.monotonic()
    response: dict[str, Any] = {}
    error = None
    stdout = stderr = ""
    try:
        proc = subprocess.run(adapter, input=json.dumps(request), text=True,
                              capture_output=True, timeout=timeout)
        stdout, stderr = proc.stdout, proc.stderr
        if proc.returncode:
            error = f"adapter exited {proc.returncode}"
        else:
            decoded = json.loads(stdout)
            if not isinstance(decoded, dict) or not isinstance(decoded.get("model"), str) or not decoded["model"].strip():
                raise ValueError("adapter must report the actual resolved model")
            if decoded.get("status") != "completed":
                raise ValueError("adapter did not report completion of the agent turn")
            response = decoded
    except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
        error = str(exc)
    elapsed = time.monotonic() - started
    checks: list[dict[str, Any]] = []
    if error is None and case.get("oracle"):
        try:
            # Generated application code is untrusted. Verification must also run
            # through the caller's sandbox, never by importing it on this host.
            oracle_request = {"protocol": 1, "phase": "oracle",
                              "workspace": str(workspace.resolve()),
                              "oracle": str((root / "evals/oracles" / case["oracle"]).resolve())}
            proc = subprocess.run(adapter, input=json.dumps(oracle_request), text=True,
                                  capture_output=True, timeout=timeout)
            decoded = json.loads(proc.stdout) if proc.returncode == 0 else None
            if not isinstance(decoded, dict) or decoded.get("status") != "completed" or type(decoded.get("exit_code")) is not int:
                raise ValueError("oracle adapter must report an actual sandboxed exit_code")
            checks.append({"exit_code": decoded["exit_code"], "stdout": decoded.get("stdout", ""),
                           "stderr": decoded.get("stderr", "")})
        except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
            checks.append({"exit_code": None, "error": str(exc)})
    result = {
        "case": case["id"], "variant": variant, "requested_model": model,
        "reported_model": response.get("model"), "adapter_error": error,
        "wall_seconds": elapsed, "initial_tree_sha256": before,
        "oracle_pass": all(c.get("exit_code") == 0 for c in checks) if checks else None,
        "checks": checks, "review_status": "pending" if case["review_checks"] else "not-required",
        "review_checks": case["review_checks"], "usage": response.get("usage"),
        "agent_report": response.get("report"),
    }
    receipt.mkdir(parents=True, exist_ok=False)
    (receipt / "adapter.stdout").write_text(stdout)
    (receipt / "adapter.stderr").write_text(stderr)
    (receipt / "result.json").write_text(json.dumps(result, indent=2))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=VARIANTS, action="append")
    parser.add_argument("--case", action="append")
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--adapter-json", help="JSON argv array for a caller-supplied sandbox adapter")
    parser.add_argument("--model")
    parser.add_argument("--timeout-seconds", type=float)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        cases = json.loads((ROOT / "evals/cases.json").read_text())["cases"]
        if args.case:
            missing = set(args.case) - {c["id"] for c in cases}
            if missing:
                raise ValueError(f"unknown cases: {sorted(missing)}")
            cases = [c for c in cases if c["id"] in args.case]
        variants = args.variant or ["minimal", "specialists"]
        if len(set(variants)) != len(variants) or args.repetitions < 1:
            raise ValueError("variants must be distinct and repetitions positive")
        if not args.execute:
            print(json.dumps({"execute": False, "cases": [c["id"] for c in cases],
                              "variants": variants, "repetitions": args.repetitions}, indent=2))
            return 0
        if not args.model or not args.output or not args.adapter_json or not args.timeout_seconds or args.timeout_seconds <= 0 or not math.isfinite(args.timeout_seconds):
            raise ValueError("execution requires --model, --output, --adapter-json and a positive --timeout-seconds")
        adapter = json.loads(args.adapter_json)
        if not isinstance(adapter, list) or not adapter or not all(isinstance(x, str) and x for x in adapter):
            raise ValueError("adapter must be a non-empty JSON argv array")
        if "baseline" in variants and args.baseline is None:
            raise ValueError("baseline variant requires --baseline")
        args.output.mkdir(parents=True, exist_ok=False)
        results = []
        for repeat in range(args.repetitions):
            # Rotate order so one variant is not always run first.
            order = variants[repeat % len(variants):] + variants[:repeat % len(variants)]
            for case in cases:
                for variant in order:
                    dest = args.output / f'{case["id"]}-{repeat + 1}-{variant}'
                    before = prepare(ROOT, case, dest / "workspace", variant, args.baseline)
                    results.append(run_case(ROOT, case, dest / "workspace", dest / "receipt",
                                            adapter, args.model, variant, args.timeout_seconds, before))
        (args.output / "results.json").write_text(json.dumps(results, indent=2))
        models = {r["reported_model"] for r in results if r["reported_model"]}
        if len(models) > 1:
            print("error: resolved models differ; comparison is not matched", file=sys.stderr)
            return 1
        if any(r["adapter_error"] or r["oracle_pass"] is False for r in results):
            return 1
        return 2 if any(r["review_status"] == "pending" for r in results) else 0
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
