#!/usr/bin/env python3
"""Report deterministic inventory and trigger-risk data for local Agent Skills.

``--check`` also enforces a warning ratchet: a warning identifier not present
in the committed baseline (``scripts/skill_inventory_baseline.json`` by
default) is an error, so new skills cannot silently accrue warnings that
existing skills were grandfathered into. ``--write-baseline`` regenerates
that baseline from the current tree.

SKILL.md data collection (frontmatter parsing, counts, broad-trigger risk
flags, eval-coverage loading) lives in ``skill_inventory_collection``.
Warning-ID derivation, quality-bar minimums, visibility parsing, and the
baseline load/compare/write logic live in ``skill_inventory_checks`` (both
400-line overflow splits); this module keeps argument parsing, report
assembly, and rendering.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from scripts.skill_inventory_checks import (
    to_repo_relative,
        DEFAULT_BASELINE_RELPATH,
        baseline_path_from_args,
        build_warning_id_map,
        build_warnings,
        load_baseline,
        ratchet_findings,
        write_baseline,
    )
    from scripts.skill_inventory_collection import (
        SkillInventory,
        apply_eval_coverage,
        load_eval_coverage,
        load_skill_inventories,
    )
except ImportError:  # pragma: no cover - direct execution puts scripts/ on sys.path
    from skill_inventory_checks import (
    to_repo_relative,
        DEFAULT_BASELINE_RELPATH,
        baseline_path_from_args,
        build_warning_id_map,
        build_warnings,
        load_baseline,
        ratchet_findings,
        write_baseline,
    )
    from skill_inventory_collection import (
        SkillInventory,
        apply_eval_coverage,
        load_eval_coverage,
        load_skill_inventories,
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Report .agents/skills inventory, trigger eval coverage, and "
            "broad-trigger risk flags."
        )
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root to scan (default: inferred from this script location).",
    )
    parser.add_argument(
        "--skills-dir",
        default=".agents/skills",
        help="Skills directory relative to repo root.",
    )
    parser.add_argument(
        "--eval-dir",
        default="evals/skill-triggers",
        help="Skill trigger eval directory relative to repo root.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output (ignored in text mode).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero on CI-relevant inventory errors or unbaselined warnings.",
    )
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help=(
            "Write the current warning-id baseline to --baseline-path (default "
            f"{DEFAULT_BASELINE_RELPATH}) and exit; does not run --check."
        ),
    )
    parser.add_argument(
        "--baseline-path",
        default="",
        help=(
            "Path to the warning-id baseline JSON "
            f"(default: {DEFAULT_BASELINE_RELPATH} under repo root)."
        ),
    )
    return parser.parse_args(argv)


def repo_root_from_args(explicit_root: str) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path(__file__).resolve().parent.parent



def skill_to_json(repo_root: Path, skill: SkillInventory) -> dict[str, object]:
    return {
        "name": skill.name,
        "directory": skill.directory,
        "path": to_repo_relative(repo_root, skill.path),
        "description_length": skill.description_length,
        "skill_md_line_count": skill.line_count,
        "reference_count": skill.reference_count,
        "template_count": skill.template_count,
        "script_count": skill.script_count,
        "asset_count": skill.asset_count,
        "example_count": skill.example_count,
        "eval_coverage_count": skill.eval_coverage_count,
        "eval_should_trigger_count": skill.eval_should_trigger_count,
        "eval_should_not_trigger_count": skill.eval_should_not_trigger_count,
        "description_trigger_only_flags": skill.description_trigger_only_flags,
        "broad_trigger_risk_flags": skill.broad_trigger_risk_flags,
        "visibility": skill.visibility,
    }


def build_report(
    repo_root: Path,
    skills_dir_name: str,
    eval_dir_name: str,
    baseline: dict[str, list[str]] | None = None,
) -> dict[str, object]:
    skills_dir = repo_root / skills_dir_name
    eval_dir = repo_root / eval_dir_name

    skills, _name_counts, skill_errors = load_skill_inventories(repo_root, skills_dir)
    known_skill_names = {skill.name for skill in skills}
    coverage = load_eval_coverage(repo_root, eval_dir, known_skill_names)
    skills = apply_eval_coverage(skills, coverage)

    errors = skill_errors + coverage.errors
    warnings = build_warnings(repo_root, skills)
    warning_id_map = build_warning_id_map(skills)

    report: dict[str, object] = {
        "schema_version": 1,
        "repo_root": str(repo_root),
        "skills_dir": skills_dir_name,
        "eval_dir": eval_dir_name,
        "totals": {
            "skills": len(skills),
            "eval_files": len(coverage.eval_files),
            "eval_references": sum(
                skill.eval_coverage_count for skill in skills
            ),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "skills": [skill_to_json(repo_root, skill) for skill in skills],
        "errors": errors,
        "warnings": warnings,
        "skill_warning_ids": warning_id_map,
    }

    if baseline is not None:
        report["ratchet"] = ratchet_findings(warning_id_map, baseline)

    return report


def render_text(report: dict[str, object]) -> str:
    totals = report["totals"]
    assert isinstance(totals, dict)
    skills = report["skills"]
    assert isinstance(skills, list)

    lines = [
        "Skill inventory report",
        f"repo_root: {report['repo_root']}",
        f"skills_dir: {report['skills_dir']}",
        f"eval_dir: {report['eval_dir']}",
        (
            "totals: "
            f"skills={totals['skills']} "
            f"eval_files={totals['eval_files']} "
            f"eval_references={totals['eval_references']} "
            f"errors={totals['errors']} "
            f"warnings={totals['warnings']}"
        ),
        "",
        (
            "name | desc_chars | lines | refs | templates | scripts | assets | "
            "examples | evals | description_flags | risk_flags"
        ),
        "--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---",
    ]

    for item in skills:
        assert isinstance(item, dict)
        risk_flags = item["broad_trigger_risk_flags"]
        assert isinstance(risk_flags, list)
        description_flags = item["description_trigger_only_flags"]
        assert isinstance(description_flags, list)
        lines.append(
            f"{item['name']} | "
            f"{item['description_length']} | "
            f"{item['skill_md_line_count']} | "
            f"{item['reference_count']} | "
            f"{item['template_count']} | "
            f"{item['script_count']} | "
            f"{item['asset_count']} | "
            f"{item['example_count']} | "
            f"{item['eval_coverage_count']} | "
            f"{', '.join(str(flag) for flag in description_flags) if description_flags else '-'} | "
            f"{', '.join(str(flag) for flag in risk_flags) if risk_flags else '-'}"
        )

    errors = report["errors"]
    assert isinstance(errors, list)
    if errors:
        lines.extend(["", "Errors:"])
        lines.extend(f"- {error}" for error in errors)

    warnings = report["warnings"]
    assert isinstance(warnings, list)
    if warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in warnings)

    ratchet = report.get("ratchet")
    if isinstance(ratchet, dict):
        new_warnings = ratchet.get("new_warnings", [])
        stale_baseline = ratchet.get("stale_baseline", [])
        assert isinstance(new_warnings, list)
        assert isinstance(stale_baseline, list)
        lines.extend(
            [
                "",
                (
                    "Ratchet: "
                    f"new_warnings={len(new_warnings)} "
                    f"stale_baseline={len(stale_baseline)}"
                ),
            ]
        )
        if new_warnings:
            lines.extend(["", "New (unbaselined) warnings — fix or add to baseline:"])
            lines.extend(f"- {warning}" for warning in new_warnings)
        if stale_baseline:
            lines.extend(["", "stale-baseline (informational; warning no longer fires):"])
            lines.extend(f"- {warning}" for warning in stale_baseline)

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = repo_root_from_args(args.repo_root)
    baseline_path = baseline_path_from_args(repo_root, args.baseline_path)

    if args.write_baseline:
        report = build_report(repo_root, args.skills_dir, args.eval_dir)
        warning_id_map = report["skill_warning_ids"]
        assert isinstance(warning_id_map, dict)
        write_baseline(baseline_path, warning_id_map)
        total_ids = sum(len(ids) for ids in warning_id_map.values())
        rel = to_repo_relative(repo_root, baseline_path)
        print(
            f"skill_inventory_baseline: wrote {len(warning_id_map)} skill(s), "
            f"{total_ids} warning id(s) -> {rel}"
        )
        return 0

    baseline = load_baseline(baseline_path)
    report = build_report(repo_root, args.skills_dir, args.eval_dir, baseline=baseline)

    if args.format == "json":
        if args.pretty:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print(json.dumps(report, ensure_ascii=False))
    else:
        print(render_text(report))

    errors = report["errors"]
    assert isinstance(errors, list)
    ratchet = report["ratchet"]
    assert isinstance(ratchet, dict)
    new_warnings = ratchet["new_warnings"]
    assert isinstance(new_warnings, list)
    if args.check and (errors or new_warnings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
