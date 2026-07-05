#!/usr/bin/env python3
"""Run function-design behavioral fixture oracles."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run function-design fixture oracles.")
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root (default: inferred from this script location).",
    )
    return parser.parse_args()


def repo_root_from_args(explicit_root: str) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path(__file__).resolve().parents[3]


def run_oracle(oracle: Path, workspace: Path) -> tuple[bool, str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, str(oracle), str(workspace)],
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return completed.returncode == 0, completed.stdout.strip()


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_args(args.repo_root)
    root = repo_root / "evals" / "function-design"
    scenarios_path = root / "scenarios.json"
    payload = json.loads(scenarios_path.read_text(encoding="utf-8"))

    failures: list[str] = []
    scenario_count = 0
    bad_count = 0

    for scenario in payload.get("scenarios", []):
        scenario_count += 1
        scenario_id = scenario["id"]
        fixture = root / scenario["fixture"]
        oracle = fixture / "oracle.py"
        good = fixture / "expected" / "good"

        passed, output = run_oracle(oracle, good)
        print(f"[{scenario_id}] expected/good: {'PASS' if passed else 'FAIL'}")
        if output:
            print(output)
        if not passed:
            failures.append(f"{scenario_id}: expected/good failed")

        bad_root = fixture / "expected" / "bad"
        if not bad_root.is_dir():
            failures.append(f"{scenario_id}: missing expected/bad directory")
            continue
        bad_cases = sorted(path for path in bad_root.iterdir() if path.is_dir())
        if not bad_cases:
            failures.append(f"{scenario_id}: no expected/bad cases")
            continue

        for bad in bad_cases:
            bad_count += 1
            bad_passed, bad_output = run_oracle(oracle, bad)
            print(f"[{scenario_id}] expected/bad/{bad.name}: {'FAIL-EXPECTED' if not bad_passed else 'UNEXPECTED-PASS'}")
            if bad_output:
                print(bad_output)
            if bad_passed:
                failures.append(f"{scenario_id}: bad sample unexpectedly passed: {bad.name}")

    if failures:
        print("Function-design oracle validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"Validated {scenario_count} function-design scenarios and {bad_count} bad samples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
