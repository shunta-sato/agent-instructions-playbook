#!/usr/bin/env python3
"""Summarize lightweight delegated agent run ledger records."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from agent_run import (
    evaluate_run_record,
    ledger_path_from_args,
    load_agent_run_records,
    repo_root_from_args,
)


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_task_class: Counter[str] = Counter()
    telemetry_status: Counter[str] = Counter()
    accepted = 0
    validation_passed = 0
    agent_completed = 0
    scope_violations = 0

    for record in records:
        judgment = evaluate_run_record(record)
        by_task_class[str(record.get("task_class", "<missing>"))] += 1
        telemetry_status[judgment["telemetry_status"]] += 1
        accepted += int(judgment["accepted"])
        validation_passed += int(judgment["validation_passed"])
        agent_completed += int(judgment["agent_completed"])
        scope_violations += int(not judgment["scope_compliant"])

    total = len(records)
    return {
        "schema_version": 1,
        "total_runs": total,
        "accepted": accepted,
        "rejected": total - accepted,
        "agent_completed": agent_completed,
        "validation_passed": validation_passed,
        "scope_violations": scope_violations,
        "by_task_class": dict(sorted(by_task_class.items())),
        "telemetry_status": dict(sorted(telemetry_status.items())),
    }


def render_text(summary: dict[str, Any]) -> str:
    lines = [
        f"total_runs: {summary['total_runs']}",
        f"accepted: {summary['accepted']}",
        f"rejected: {summary['rejected']}",
        f"agent_completed: {summary['agent_completed']}",
        f"validation_passed: {summary['validation_passed']}",
        f"scope_violations: {summary['scope_violations']}",
        "by_task_class:",
    ]
    lines.extend(f"- {name}: {count}" for name, count in summary["by_task_class"].items())
    lines.append("telemetry_status:")
    lines.extend(f"- {name}: {count}" for name, count in summary["telemetry_status"].items())
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize agent run ledger records.")
    parser.add_argument("--repo-root", default="", help="Repository root.")
    parser.add_argument("--ledger", default="", help="Ledger path; defaults to .agents/runs/agent-runs.jsonl.")
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="text",
        help="Output format.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        repo_root = repo_root_from_args(args.repo_root)
        ledger_path = ledger_path_from_args(repo_root, args.ledger)
        records = load_agent_run_records(Path(ledger_path))
        summary = summarize(records)
    except ValueError as exc:
        print(f"Agent run summary failed: {exc}")
        return 1

    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_text(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
