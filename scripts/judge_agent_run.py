#!/usr/bin/env python3
"""Judge one delegated agent run from the lightweight run ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from agent_run import (
    evaluate_run_record,
    ledger_path_from_args,
    load_agent_run_records,
    repo_root_from_args,
)


def select_record(records: list[dict[str, Any]], run_id: str) -> dict[str, Any]:
    if not records:
        raise ValueError("ledger has no agent_run records")
    if not run_id:
        return records[-1]

    for record in reversed(records):
        if record.get("run_id") == run_id:
            return record
    raise ValueError(f"run_id not found: {run_id}")


def render_text(record: dict[str, Any], judgment: dict[str, Any]) -> str:
    lines = [
        f"run_id: {record.get('run_id')}",
        f"accepted: {str(judgment['accepted']).lower()}",
        f"agent_completed: {str(judgment['agent_completed']).lower()}",
        f"validation_passed: {str(judgment['validation_passed']).lower()}",
        f"scope_compliant: {str(judgment['scope_compliant']).lower()}",
        f"quality_gate: {judgment['quality_gate']}",
        f"telemetry_status: {judgment['telemetry_status']}",
    ]
    if judgment["outside_allowed_files"]:
        lines.append("outside_allowed_files:")
        lines.extend(f"- {path}" for path in judgment["outside_allowed_files"])
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Judge one agent run ledger record.")
    parser.add_argument("--repo-root", default="", help="Repository root.")
    parser.add_argument("--ledger", default="", help="Ledger path; defaults to .agents/runs/agent-runs.jsonl.")
    parser.add_argument("--run-id", default="", help="Run ID to judge; defaults to latest agent_run record.")
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--require-accepted",
        action="store_true",
        help="Exit nonzero when the selected run is not accepted.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        repo_root = repo_root_from_args(args.repo_root)
        ledger_path = ledger_path_from_args(repo_root, args.ledger)
        records = load_agent_run_records(Path(ledger_path))
        record = select_record(records, args.run_id)
        judgment = evaluate_run_record(record)
    except ValueError as exc:
        print(f"Agent run judgment failed: {exc}")
        return 1

    if args.format == "json":
        print(
            json.dumps(
                {
                    "run_id": record.get("run_id"),
                    "judgment": judgment,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(render_text(record, judgment))

    if args.require_accepted and not judgment["accepted"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
