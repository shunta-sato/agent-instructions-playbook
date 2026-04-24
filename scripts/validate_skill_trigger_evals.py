#!/usr/bin/env python3
"""Validate skill trigger eval seed files against the local skill catalog."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


NAME_RE = re.compile(r"^\s*name:\s*(.+)\s*$", re.M)
OPTIONAL_BEHAVIOR_FIELDS = (
    "expected_artifacts",
    "expected_decisions",
    "expected_evidence",
    "expected_output_contains",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate evals/skill-triggers/*.json schema and skill names."
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root (default: inferred from this script location).",
    )
    parser.add_argument(
        "--eval-dir",
        default="evals/skill-triggers",
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


def require_str(case: dict[str, Any], key: str, context: str, errors: list[str]) -> str:
    value = case.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{context}: missing non-empty string field: {key}")
        return ""
    return value


def require_name_list(
    case: dict[str, Any],
    key: str,
    context: str,
    skill_names: set[str],
    errors: list[str],
) -> list[str]:
    value = case.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{context}: field must be a list of skill names: {key}")
        return []

    unknown = sorted(set(value) - skill_names)
    if unknown:
        errors.append(f"{context}: {key} references unknown skills: {', '.join(unknown)}")
    return value


def require_optional_non_empty_str_list(
    case: dict[str, Any],
    key: str,
    context: str,
    errors: list[str],
) -> None:
    if key not in case:
        return

    value = case[key]
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        errors.append(f"{context}: {key} must be a non-empty list of non-empty strings")


def validate_file(path: Path, skill_names: set[str]) -> tuple[int, list[str]]:
    errors: list[str] = []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return 0, [f"{path}: invalid JSON: {exc}"]

    if not isinstance(payload, dict):
        return 0, [f"{path}: top-level value must be an object"]
    if payload.get("version") != 1:
        errors.append(f"{path}: version must be 1")

    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append(f"{path}: cases must be a non-empty list")
        return 0, errors

    seen_ids: set[str] = set()
    for index, case in enumerate(cases, start=1):
        context = f"{path}:{index}"
        if not isinstance(case, dict):
            errors.append(f"{context}: case must be an object")
            continue

        case_id = require_str(case, "id", context, errors)
        require_str(case, "prompt", context, errors)
        should_trigger = require_name_list(
            case, "should_trigger", context, skill_names, errors
        )
        should_not_trigger = require_name_list(
            case, "should_not_trigger", context, skill_names, errors
        )
        for key in OPTIONAL_BEHAVIOR_FIELDS:
            require_optional_non_empty_str_list(case, key, context, errors)

        if case_id in seen_ids:
            errors.append(f"{context}: duplicate case id: {case_id}")
        seen_ids.add(case_id)

        if not should_trigger and not should_not_trigger:
            errors.append(
                f"{context}: provide at least one should_trigger or should_not_trigger"
            )

        overlap = sorted(set(should_trigger) & set(should_not_trigger))
        if overlap:
            errors.append(f"{context}: skill appears in both lists: {', '.join(overlap)}")

    return len(cases), errors


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_args(args.repo_root)
    eval_dir = repo_root / args.eval_dir
    skill_names = load_skill_names(repo_root)

    errors: list[str] = []
    case_count = 0

    if not eval_dir.is_dir():
        errors.append(f"{eval_dir.relative_to(repo_root).as_posix()}: directory is missing")
    else:
        files = sorted(eval_dir.glob("*.json"))
        if not files:
            errors.append(f"{eval_dir.relative_to(repo_root).as_posix()}: no JSON eval files")
        for path in files:
            count, file_errors = validate_file(path, skill_names)
            case_count += count
            errors.extend(file_errors)

    if errors:
        print("Skill trigger eval validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Validated {case_count} skill trigger eval cases "
        f"against {len(skill_names)} skills."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
