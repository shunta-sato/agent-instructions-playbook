#!/usr/bin/env python3
"""Measure repo-local proxy adoption for selected skills."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class MetricResult:
    count: int
    paths: list[str]
    note: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan repository artifacts and emit proxy metrics for selected skill adoption."
        )
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root to scan (default: inferred from this script location)",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format. JSON is machine-readable and default.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (ignored in text mode)",
    )
    return parser.parse_args()


def repo_root_from_args(explicit_root: str) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path(__file__).resolve().parent.parent


def to_repo_relative(repo_root: Path, path: Path) -> str:
    return str(path.resolve().relative_to(repo_root))


def measure_execplan(repo_root: Path) -> MetricResult:
    plans_dir = repo_root / "plans"
    if not plans_dir.exists():
        return MetricResult(count=0, paths=[], note="plans/ directory is missing")

    artifacts: list[str] = []
    ignored = {"README.md", "_template_execplan.md"}
    for plan_file in sorted(plans_dir.glob("*.md")):
        if plan_file.name in ignored:
            continue
        artifacts.append(to_repo_relative(repo_root, plan_file))

    return MetricResult(
        count=len(artifacts),
        paths=artifacts,
        note="Counts plans/*.md excluding README.md and _template_execplan.md",
    )


def measure_bug_report(repo_root: Path) -> MetricResult:
    bug_dir = repo_root / "reports" / "bug-reports"
    artifacts = [
        to_repo_relative(repo_root, path)
        for path in sorted(bug_dir.glob("*.md"))
        if path.is_file()
    ]
    return MetricResult(
        count=len(artifacts),
        paths=artifacts,
        note="Counts reports/bug-reports/*.md",
    )


def measure_uiux_core(repo_root: Path) -> MetricResult:
    uiux_dir = repo_root / "uiux"
    required = (
        "ui_contract.yaml",
        "ui_spec.json",
        "auto_review.json",
        "diff_summary.md",
    )

    packs: list[str] = []
    if uiux_dir.exists():
        for child in sorted(uiux_dir.iterdir()):
            if not child.is_dir():
                continue
            if all((child / name).is_file() for name in required):
                packs.append(to_repo_relative(repo_root, child))

    return MetricResult(
        count=len(packs),
        paths=packs,
        note=(
            "Counts uiux/<pack>/ directories containing ui_contract.yaml, "
            "ui_spec.json, auto_review.json, and diff_summary.md"
        ),
    )


def measure_project_initialization(repo_root: Path) -> MetricResult:
    commands_md = repo_root / "COMMANDS.md"
    if not commands_md.exists():
        return MetricResult(count=0, paths=[], note="COMMANDS.md is missing")

    for line in commands_md.read_text(encoding="utf-8").splitlines():
        normalized = line.strip().lower()
        if normalized.startswith("- verified by agent:") and "yes" in normalized:
            return MetricResult(
                count=1,
                paths=[to_repo_relative(repo_root, commands_md)],
                note="1 when COMMANDS.md has '- verified by agent: yes (...)'; else 0",
            )

    return MetricResult(
        count=0,
        paths=[],
        note="0 when COMMANDS.md still has '<fill>' or a non-yes verification marker",
    )


def build_report(repo_root: Path) -> dict[str, object]:
    metrics = {
        "execution_plans": measure_execplan(repo_root),
        "bug_investigation_and_rca": measure_bug_report(repo_root),
        "uiux_core": measure_uiux_core(repo_root),
        "project_initialization": measure_project_initialization(repo_root),
    }

    counts = {key: metric.count for key, metric in metrics.items()}
    total = sum(counts.values())

    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "totals": {
            "proxy_artifact_count": total,
            "skills_measured": len(metrics),
        },
        "skills": {
            key: {
                "count": metric.count,
                "artifacts": metric.paths,
                "proxy_definition": metric.note,
            }
            for key, metric in metrics.items()
        },
    }


def render_text(report: dict[str, object]) -> str:
    lines = [
        "Skill adoption proxy measurement",
        f"generated_at_utc: {report['generated_at_utc']}",
        f"repo_root: {report['repo_root']}",
        "",
    ]

    skills = report["skills"]
    assert isinstance(skills, dict)
    for name, payload in skills.items():
        assert isinstance(payload, dict)
        lines.append(f"- {name}: {payload['count']}")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_args(args.repo_root)
    report = build_report(repo_root)

    if args.format == "text":
        print(render_text(report))
    else:
        if args.pretty:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(report, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
