"""Harness-specific validation helpers for model routing.

This module owns the policy, catalog-identity, and resolver smoke checks that
prove concrete model selection is bound to one active execution harness.
Generic task/profile/risk schema validation remains in
``validate_model_routing.py``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    from scripts.resolve_model_route import (
        ACTIVE_HARNESS_MISSING_REASON,
        CATALOG_HARNESS_MISMATCH_REASON,
        load_json_compatible_yaml,
        resolve_route,
    )
except ImportError:  # pragma: no cover - direct execution puts scripts/ on sys.path
    from resolve_model_route import (
        ACTIVE_HARNESS_MISSING_REASON,
        CATALOG_HARNESS_MISMATCH_REASON,
        load_json_compatible_yaml,
        resolve_route,
    )


REQUIRED_HARNESS_FALLBACKS = {
    "active_harness_missing",
    "catalog_harness_missing",
    "catalog_harness_mismatch",
}


def _require_string(value: Any, path: str, errors: list[str]) -> str:
    if not isinstance(value, str) or not value:
        errors.append(f"{path}: must be a non-empty string")
        return ""
    return value


def _require_bool(value: Any, path: str, errors: list[str]) -> bool:
    if not isinstance(value, bool):
        errors.append(f"{path}: must be a boolean")
        return False
    return value


def _require_string_list(value: Any, path: str, errors: list[str]) -> list[str]:
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


def validate_resolver_policy(policy: dict[str, Any], errors: list[str]) -> None:
    resolver = policy.get("resolver_policy")
    if not isinstance(resolver, dict):
        errors.append("resolver_policy: must be an object")
        return

    _require_string(
        resolver.get("catalog_format"),
        "resolver_policy.catalog_format",
        errors,
    )
    _require_bool(
        resolver.get("active_harness_required_for_catalog_selection"),
        "resolver_policy.active_harness_required_for_catalog_selection",
        errors,
    )
    cross_harness = _require_bool(
        resolver.get("cross_harness_fallback"),
        "resolver_policy.cross_harness_fallback",
        errors,
    )
    if cross_harness:
        errors.append("resolver_policy.cross_harness_fallback: must be false")

    selectable = set(
        _require_string_list(
            resolver.get("selectable_statuses"),
            "resolver_policy.selectable_statuses",
            errors,
        )
    )
    excluded = set(
        _require_string_list(
            resolver.get("excluded_statuses"),
            "resolver_policy.excluded_statuses",
            errors,
        )
    )
    if selectable & excluded:
        errors.append("resolver_policy: selectable and excluded statuses overlap")

    _require_string_list(
        resolver.get("candidate_required_fields"),
        "resolver_policy.candidate_required_fields",
        errors,
    )
    reasons = set(
        _require_string_list(
            resolver.get("fallback_reasons"),
            "resolver_policy.fallback_reasons",
            errors,
        )
    )
    missing = sorted(REQUIRED_HARNESS_FALLBACKS - reasons)
    if missing:
        errors.append(
            "resolver_policy.fallback_reasons: missing harness reasons: "
            + ", ".join(missing)
        )


def validate_repository_catalog(repo_root: Path, errors: list[str]) -> None:
    path = repo_root / ".agents/model-routing/model-catalog.json"
    try:
        catalog = load_json_compatible_yaml(path)
    except ValueError as exc:
        errors.append(str(exc))
        return
    _require_string(catalog.get("harness"), "model-catalog.harness", errors)


def validate_resolver_smoke(
    routing: dict[str, dict[str, Any]], errors: list[str]
) -> None:
    harness = "test-harness"
    catalog = {
        "schema_version": 1,
        "harness": harness,
        "models": [
            {
                "id": "candidate-unavailable",
                "profiles": ["focused_code_edit"],
                "status": "unavailable",
                "smoke_eval": "passed",
                "priority": 100,
            },
            {
                "id": "candidate-rumored",
                "profiles": ["focused_code_edit"],
                "status": "rumored",
                "smoke_eval": "passed",
                "priority": 90,
            },
            {
                "id": "candidate-smoke-missing",
                "profiles": ["focused_code_edit"],
                "status": "available",
                "smoke_eval": "not_run",
                "priority": 80,
            },
            {
                "id": "candidate-selectable",
                "profiles": ["focused_code_edit"],
                "status": "available",
                "smoke_eval": "passed",
                "priority": 1,
            },
        ],
    }
    result = resolve_route(
        "unit_test_single_case", routing, catalog, harness=harness
    )
    if result["selected_model"] != "candidate-selectable":
        errors.append(
            "resolver smoke: expected candidate-selectable after exclusions, got "
            f"{result['selected_model']}"
        )

    reasons = "\n".join(result["fallback_reasons"])
    for expected in (
        "candidate_status_excluded:candidate-unavailable",
        "candidate_status_excluded:candidate-rumored",
        "candidate_smoke_eval_not_passed:candidate-smoke-missing",
    ):
        if expected not in reasons:
            errors.append(f"resolver smoke: missing fallback reason {expected}")

    no_catalog = resolve_route(
        "unit_test_single_case", routing, None, harness=harness
    )
    if no_catalog["selected"]:
        errors.append("resolver smoke: route without catalog must not select")
    if "catalog_not_provided" not in no_catalog["fallback_reasons"]:
        errors.append("resolver smoke: missing catalog_not_provided reason")

    no_harness = resolve_route("unit_test_single_case", routing, catalog)
    if no_harness["selected"]:
        errors.append("resolver smoke: route without active harness must not select")
    if ACTIVE_HARNESS_MISSING_REASON not in no_harness["fallback_reasons"]:
        errors.append("resolver smoke: missing active_harness_missing reason")

    mismatch_harness = "other-harness"
    mismatch = resolve_route(
        "unit_test_single_case", routing, catalog, harness=mismatch_harness
    )
    expected_mismatch = (
        f"{CATALOG_HARNESS_MISMATCH_REASON}:{harness}:{mismatch_harness}"
    )
    if mismatch["selected"]:
        errors.append("resolver smoke: cross-harness catalog must not select")
    if expected_mismatch not in mismatch["fallback_reasons"]:
        errors.append(f"resolver smoke: missing fallback reason {expected_mismatch}")

    fallback_catalog = {
        "schema_version": 1,
        "harness": harness,
        "models": [
            {
                "id": "candidate-supervisor",
                "profiles": ["coding_supervisor"],
                "status": "available",
                "smoke_eval": "passed",
                "priority": 1,
            }
        ],
    }
    fallback_result = resolve_route(
        "unit_test_single_case", routing, fallback_catalog, harness=harness
    )
    if fallback_result["selected_model"] != "candidate-supervisor":
        errors.append(
            "resolver smoke: expected same-harness fallback candidate-supervisor, "
            f"got {fallback_result['selected_model']}"
        )
    if fallback_result["selection_profile"] != "coding_supervisor":
        errors.append(
            "resolver smoke: expected selection_profile coding_supervisor, got "
            f"{fallback_result['selection_profile']}"
        )
    if "profile_fallback_used:coding_supervisor" not in fallback_result["fallback_reasons"]:
        errors.append("resolver smoke: missing profile_fallback_used reason")
