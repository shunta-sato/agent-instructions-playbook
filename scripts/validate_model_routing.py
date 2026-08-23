#!/usr/bin/env python3
"""Validate model-routing artifacts and resolver invariants."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    from scripts.model_routing_harness_validation import (
        validate_repository_catalog,
        validate_resolver_policy,
        validate_resolver_smoke,
    )
    from scripts.resolve_model_route import load_model_routing
except ImportError:  # pragma: no cover - direct execution puts scripts/ on sys.path
    from model_routing_harness_validation import (
        validate_repository_catalog,
        validate_resolver_policy,
        validate_resolver_smoke,
    )
    from resolve_model_route import load_model_routing


FORBIDDEN_MODEL_KEYS = {
    "model",
    "model_id",
    "model_name",
    "requested_model",
    "resolved_model",
    "concrete_model",
}
EXPECTED_PROMPT_DETAIL_LEVELS = {"compact", "normal", "strict"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate .agents/model-routing configuration."
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root (default: inferred from this script location).",
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


def require_string_list(value: Any, path: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{path}: must be a list")
        return []
    strings: list[str] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, str) or not item:
            errors.append(f"{path}[{index}]: must be a non-empty string")
            continue
        strings.append(item)
    return strings


def detect_forbidden_model_keys(value: Any, path: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key in FORBIDDEN_MODEL_KEYS:
                errors.append(
                    f"{child_path}: concrete model fields do not belong in routing config"
                )
            detect_forbidden_model_keys(child, child_path, errors)
    elif isinstance(value, list):
        for index, item in enumerate(value, start=1):
            detect_forbidden_model_keys(item, f"{path}[{index}]", errors)


def validate_prompt_detail_doc(repo_root: Path, errors: list[str]) -> None:
    path = repo_root / ".agents/model-routing/prompt-detail-levels.md"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    if not text:
        errors.append(".agents/model-routing/prompt-detail-levels.md: missing")
        return
    for level in EXPECTED_PROMPT_DETAIL_LEVELS:
        if f"## {level}" not in text:
            errors.append(
                ".agents/model-routing/prompt-detail-levels.md: "
                f"missing section for {level}"
            )


def validate_profiles(
    profiles: dict[str, Any],
    errors: list[str],
) -> set[str]:
    profile_names = set(profiles)
    for name, raw_profile in profiles.items():
        profile = require_object(raw_profile, f"profile {name}", errors)
        require_string(profile.get("description"), f"profile {name}.description", errors)
        require_string_list(profile.get("requires"), f"profile {name}.requires", errors)
        fallbacks = require_string_list(
            profile.get("fallback_profiles", []),
            f"profile {name}.fallback_profiles",
            errors,
        )
        for fallback in fallbacks:
            if fallback not in profile_names:
                errors.append(
                    f"profile {name}: fallback profile {fallback} is not defined"
                )
    return profile_names


def validate_risk_gates(risk_gates: dict[str, Any], errors: list[str]) -> set[str]:
    gate_names = set(risk_gates)
    for name, raw_gate in risk_gates.items():
        gate = require_object(raw_gate, f"risk gate {name}", errors)
        require_string(gate.get("description"), f"risk gate {name}.description", errors)
        require_string_list(
            gate.get("minimum_verification"),
            f"risk gate {name}.minimum_verification",
            errors,
        )
        require_string_list(
            gate.get("escalate_when"),
            f"risk gate {name}.escalate_when",
            errors,
        )
    return gate_names


def validate_task_classes(
    task_classes: dict[str, Any],
    profile_names: set[str],
    gate_names: set[str],
    errors: list[str],
) -> None:
    for name, raw_task in task_classes.items():
        task = require_object(raw_task, f"task class {name}", errors)
        require_string(task.get("description"), f"task class {name}.description", errors)
        profile = require_string(task.get("profile"), f"task class {name}.profile", errors)
        if profile and profile not in profile_names:
            errors.append(f"task class {name}: profile {profile} is not defined")

        prompt_detail = require_string(
            task.get("prompt_detail"),
            f"task class {name}.prompt_detail",
            errors,
        )
        if prompt_detail and prompt_detail not in EXPECTED_PROMPT_DETAIL_LEVELS:
            errors.append(
                f"task class {name}: prompt detail {prompt_detail} is not defined"
            )

        risk_gate = require_string(
            task.get("risk_gate"),
            f"task class {name}.risk_gate",
            errors,
        )
        if risk_gate and risk_gate not in gate_names:
            errors.append(f"task class {name}: risk gate {risk_gate} is not defined")

        escalation_profile = task.get("escalation_profile")
        if escalation_profile is not None and escalation_profile not in profile_names:
            errors.append(
                f"task class {name}: escalation profile {escalation_profile} "
                "is not defined"
            )

        success = require_object(
            task.get("success_criteria"),
            f"task class {name}.success_criteria",
            errors,
        )
        require_string_list(
            success.get("required"),
            f"task class {name}.success_criteria.required",
            errors,
        )


def validate_model_routing(repo_root: Path) -> list[str]:
    errors: list[str] = []
    try:
        routing = load_model_routing(repo_root)
    except ValueError as exc:
        return [str(exc)]

    detect_forbidden_model_keys(routing, "model-routing", errors)
    validate_prompt_detail_doc(repo_root, errors)
    validate_repository_catalog(repo_root, errors)

    task_classes = require_object(
        routing["task_classes"].get("task_classes"),
        "task_classes",
        errors,
    )
    profiles = require_object(
        routing["capability_profiles"].get("capability_profiles"),
        "capability_profiles",
        errors,
    )
    risk_gates = require_object(
        routing["risk_gates"].get("risk_gates"),
        "risk_gates",
        errors,
    )

    profile_names = validate_profiles(profiles, errors)
    gate_names = validate_risk_gates(risk_gates, errors)
    validate_task_classes(task_classes, profile_names, gate_names, errors)
    validate_resolver_policy(routing["resolver_policy"], errors)
    if not errors:
        validate_resolver_smoke(routing, errors)
    return errors


def main() -> int:
    args = parse_args()
    repo_root = repo_root_from_args(args.repo_root)
    errors = validate_model_routing(repo_root)
    if errors:
        print("Model routing validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    routing = load_model_routing(repo_root)
    task_count = len(routing["task_classes"]["task_classes"])
    profile_count = len(routing["capability_profiles"]["capability_profiles"])
    print(
        f"Validated harness-aware model routing: "
        f"{task_count} task classes, {profile_count} profiles."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
