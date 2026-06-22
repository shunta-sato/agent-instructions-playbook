#!/usr/bin/env python3
"""Validate model-routing smoke eval seed files against the local resolver."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from resolve_model_route import load_model_routing, resolve_route


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate evals/model-routing/*.json schema and resolver expectations."
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root (default: inferred from this script location).",
    )
    parser.add_argument(
        "--eval-dir",
        default="evals/model-routing",
        help="Eval directory relative to repo root.",
    )
    return parser.parse_args()


def repo_root_from_args(explicit_root: str) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path(__file__).resolve().parent.parent


def require_object(value: Any, path: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{path}: must be an object")
        return {}
    return value


def require_string(value: Any, path: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value:
        errors.append(f"{path}: must be a non-empty string")
        return ""
    return value


def require_bool(value: Any, path: str, errors: list[str]) -> bool:
    if not isinstance(value, bool):
        errors.append(f"{path}: must be a boolean")
        return False
    return value


def require_string_list(value: Any, path: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not value:
        errors.append(f"{path}: must be a non-empty list")
        return []
    strings: list[str] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, str) or not item:
            errors.append(f"{path}[{index}]: must be a non-empty string")
            continue
        strings.append(item)
    return strings


def catalog_profiles(value: Any, path: str, errors: list[str]) -> list[str]:
    if isinstance(value, str) and value:
        return [value]
    return require_string_list(value, path, errors)


def validate_catalog(
    catalog: dict[str, Any],
    path: str,
    profile_names: set[str],
    known_statuses: set[str],
    errors: list[str],
) -> None:
    if catalog.get("schema_version") != 1:
        errors.append(f"{path}.schema_version: must be 1")

    models = catalog.get("models")
    if not isinstance(models, list) or not models:
        errors.append(f"{path}.models: must be a non-empty list")
        return

    for index, raw_model in enumerate(models, start=1):
        model_path = f"{path}.models[{index}]"
        model = require_object(raw_model, model_path, errors)
        if not model:
            continue

        require_string(model.get("id"), f"{model_path}.id", errors)
        for profile in catalog_profiles(model.get("profiles"), f"{model_path}.profiles", errors):
            if profile not in profile_names:
                errors.append(f"{model_path}.profiles: unknown profile {profile}")

        status = require_string(model.get("status"), f"{model_path}.status", errors)
        if status and status not in known_statuses:
            errors.append(f"{model_path}.status: unknown resolver status {status}")

        require_string(model.get("smoke_eval"), f"{model_path}.smoke_eval", errors)


def validate_expected_result(
    expected: dict[str, Any],
    result: dict[str, Any],
    path: str,
    errors: list[str],
) -> None:
    selected = require_bool(expected.get("selected"), f"{path}.selected", errors)
    if result.get("selected") != selected:
        errors.append(
            f"{path}.selected: expected {selected}, got {result.get('selected')}"
        )

    selection_profile = expected.get("selection_profile")
    if selection_profile is not None:
        selection_profile = require_string(
            selection_profile, f"{path}.selection_profile", errors
        )
        if selection_profile and result.get("selection_profile") != selection_profile:
            errors.append(
                f"{path}.selection_profile: expected {selection_profile}, "
                f"got {result.get('selection_profile')}"
            )

    selected_model = expected.get("selected_model")
    if selected_model is not None:
        selected_model = require_string(selected_model, f"{path}.selected_model", errors)
        if selected_model and result.get("selected_model") != selected_model:
            errors.append(
                f"{path}.selected_model: expected {selected_model}, "
                f"got {result.get('selected_model')}"
            )
    elif selected is False and result.get("selected_model") is not None:
        errors.append(
            f"{path}.selected_model: expected no selected model, "
            f"got {result.get('selected_model')}"
        )

    expected_reasons = require_string_list(
        expected.get("fallback_reasons_contains", []),
        f"{path}.fallback_reasons_contains",
        errors,
    )
    actual_reasons = set(result.get("fallback_reasons", []))
    for reason in expected_reasons:
        if reason not in actual_reasons:
            errors.append(f"{path}: missing fallback reason {reason}")


def validate_case(
    case: Any,
    path: str,
    routing: dict[str, dict[str, Any]],
    seen_ids: set[str],
    errors: list[str],
) -> None:
    if not isinstance(case, dict):
        errors.append(f"{path}: case must be an object")
        return

    task_classes = routing["task_classes"]["task_classes"]
    profile_names = set(routing["capability_profiles"]["capability_profiles"])
    resolver = routing["resolver_policy"]["resolver_policy"]
    known_statuses = set(resolver["selectable_statuses"]) | set(resolver["excluded_statuses"])

    case_id = require_string(case.get("id"), f"{path}.id", errors)
    if case_id in seen_ids:
        errors.append(f"{path}.id: duplicate case id: {case_id}")
    seen_ids.add(case_id)

    task_class = require_string(case.get("task_class"), f"{path}.task_class", errors)
    if task_class and task_class not in task_classes:
        errors.append(f"{path}.task_class: unknown task class {task_class}")

    expected_profile = require_string(
        case.get("expected_capability_profile"),
        f"{path}.expected_capability_profile",
        errors,
    )
    if task_class in task_classes and expected_profile:
        actual_profile = task_classes[task_class]["profile"]
        if expected_profile != actual_profile:
            errors.append(
                f"{path}.expected_capability_profile: expected {actual_profile} "
                f"for task class {task_class}, got {expected_profile}"
            )

    require_string_list(case.get("checks"), f"{path}.checks", errors)
    catalog = require_object(case.get("catalog"), f"{path}.catalog", errors)
    expected = require_object(case.get("expected"), f"{path}.expected", errors)
    if catalog:
        validate_catalog(
            catalog,
            f"{path}.catalog",
            profile_names,
            known_statuses,
            errors,
        )

    if task_class in task_classes and catalog and expected:
        try:
            result = resolve_route(task_class, routing, catalog)
        except ValueError as exc:
            errors.append(f"{path}: resolver failed: {exc}")
        else:
            if result.get("capability_profile") != expected_profile:
                errors.append(
                    f"{path}: resolver capability_profile expected {expected_profile}, "
                    f"got {result.get('capability_profile')}"
                )
            validate_expected_result(expected, result, f"{path}.expected", errors)


def validate_file(
    path: Path,
    repo_root: Path,
    routing: dict[str, dict[str, Any]],
) -> tuple[int, list[str]]:
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

    cases = payload.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append(f"{relpath}: cases must be a non-empty list")
        return 0, errors

    seen_ids: set[str] = set()
    for index, case in enumerate(cases, start=1):
        validate_case(case, f"{relpath}:{index}", routing, seen_ids, errors)
    return len(cases), errors


def validate_model_routing_evals(
    repo_root: Path,
    eval_dir_name: str,
) -> tuple[int, list[str]]:
    try:
        routing = load_model_routing(repo_root)
    except ValueError as exc:
        return 0, [str(exc)]

    eval_dir = repo_root / eval_dir_name
    if not eval_dir.is_dir():
        return 0, [f"{eval_dir.relative_to(repo_root).as_posix()}: directory is missing"]

    files = sorted(eval_dir.glob("*.json"))
    if not files:
        return 0, [f"{eval_dir.relative_to(repo_root).as_posix()}: no JSON eval files"]

    errors: list[str] = []
    case_count = 0
    for path in files:
        count, file_errors = validate_file(path, repo_root, routing)
        case_count += count
        errors.extend(file_errors)
    return case_count, errors


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_args(args.repo_root)
    case_count, errors = validate_model_routing_evals(repo_root, args.eval_dir)
    if errors:
        print("Model routing eval validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {case_count} model routing eval cases.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
