#!/usr/bin/env python3
"""Validate skill behavior eval seed files against the local skill catalog."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


NAME_RE = re.compile(r"^\s*name:\s*(.+)\s*$", re.M)
EXPECTED_QUALITY_GATE_DECISIONS = {"submit", "no-submit"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate evals/skill-behavior/*.json schema and skill names."
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root (default: inferred from this script location).",
    )
    parser.add_argument(
        "--eval-dir",
        default="evals/skill-behavior",
        help="Eval directory relative to repo root.",
    )
    return parser.parse_args()


def repo_root_from_args(explicit_root: str) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path(__file__).resolve().parent.parent


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1].strip()
    return value


def load_skill_names(repo_root: Path) -> set[str]:
    names: set[str] = set()
    for skill_md in sorted((repo_root / ".agents" / "skills").glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        match = NAME_RE.search(text)
        if match:
            names.add(strip_quotes(match.group(1)))
    return names


def require_str(payload: dict[str, Any], key: str, context: str, errors: list[str]) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context}: missing non-empty string field: {key}")
        return ""
    return value


def require_str_list(
    payload: dict[str, Any],
    key: str,
    context: str,
    errors: list[str],
    *,
    allow_empty: bool = False,
) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list):
        errors.append(f"{context}: {key} must be a list of strings")
        return []
    if not allow_empty and not value:
        errors.append(f"{context}: {key} must be non-empty")
        return []
    if not all(isinstance(item, str) and item.strip() for item in value):
        errors.append(f"{context}: {key} must contain only non-empty strings")
        return []
    return value


def validate_quality_gate_decision(
    skill_name: str,
    decision: str,
    context: str,
    errors: list[str],
) -> None:
    if skill_name != "quality-gate" or not decision:
        return
    if decision not in EXPECTED_QUALITY_GATE_DECISIONS:
        allowed = ", ".join(sorted(EXPECTED_QUALITY_GATE_DECISIONS))
        errors.append(f"{context}: expected_decision must be one of: {allowed}")


def validate_case(
    case: Any,
    context: str,
    skill_name: str,
    seen_ids: set[str],
    errors: list[str],
) -> None:
    if not isinstance(case, dict):
        errors.append(f"{context}: case must be an object")
        return

    case_id = require_str(case, "id", context, errors)
    require_str(case, "prompt", context, errors)
    require_str_list(case, "given", context, errors)
    decision = require_str(case, "expected_decision", context, errors)
    require_str_list(case, "expected_findings", context, errors, allow_empty=True)
    require_str_list(case, "expected_output_contains", context, errors)
    validate_quality_gate_decision(skill_name, decision, context, errors)

    if case_id in seen_ids:
        errors.append(f"{context}: duplicate case id: {case_id}")
    seen_ids.add(case_id)


def validate_file(path: Path, repo_root: Path, skill_names: set[str]) -> tuple[int, list[str]]:
    errors: list[str] = []
    relpath = path.relative_to(repo_root).as_posix()
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return 0, [f"{relpath}: invalid JSON: {exc}"]

    if not isinstance(payload, dict):
        return 0, [f"{relpath}: top-level value must be an object"]
    if payload.get("version") != 1:
        errors.append(f"{relpath}: version must be 1")

    skill_name = require_str(payload, "skill", relpath, errors)
    if skill_name and skill_name not in skill_names:
        errors.append(f"{relpath}: skill references unknown skill: {skill_name}")

    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append(f"{relpath}: cases must be a non-empty list")
        return 0, errors

    seen_ids: set[str] = set()
    for index, case in enumerate(cases, start=1):
        validate_case(case, f"{relpath}:{index}", skill_name, seen_ids, errors)

    return len(cases), errors


def validate_skill_behavior_evals(repo_root: Path, eval_dir_name: str) -> tuple[int, list[str]]:
    eval_dir = repo_root / eval_dir_name
    skill_names = load_skill_names(repo_root)
    errors: list[str] = []
    case_count = 0

    if not eval_dir.is_dir():
        errors.append(f"{eval_dir.relative_to(repo_root).as_posix()}: directory is missing")
        return 0, errors

    files = sorted(eval_dir.glob("*.json"))
    if not files:
        errors.append(f"{eval_dir.relative_to(repo_root).as_posix()}: no JSON eval files")
        return 0, errors

    for path in files:
        count, file_errors = validate_file(path, repo_root, skill_names)
        case_count += count
        errors.extend(file_errors)
    return case_count, errors


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_args(args.repo_root)
    case_count, errors = validate_skill_behavior_evals(repo_root, args.eval_dir)
    if errors:
        print("Skill behavior eval validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {case_count} skill behavior eval cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
