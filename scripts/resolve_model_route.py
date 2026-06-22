#!/usr/bin/env python3
"""Resolve model-routing task classes without storing concrete model IDs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_MODEL_ROUTING_DIR = ".agents/model-routing"
EXCLUDED_STATUS_REASON = "candidate_status_excluded"
MISSING_FIELD_REASON = "candidate_missing_required_field"
SMOKE_EVAL_REASON = "candidate_smoke_eval_not_passed"


def repo_root_from_args(explicit_root: str) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path(__file__).resolve().parent.parent


def load_json_compatible_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"{path}: missing")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{path}: expected JSON-compatible YAML object: {exc}"
        ) from exc

    if not isinstance(payload, dict):
        raise ValueError(f"{path}: top-level value must be an object")
    return payload


def load_model_routing(repo_root: Path) -> dict[str, dict[str, Any]]:
    base = repo_root / DEFAULT_MODEL_ROUTING_DIR
    return {
        "task_classes": load_json_compatible_yaml(base / "task-classes.yml"),
        "capability_profiles": load_json_compatible_yaml(base / "capability-profiles.yml"),
        "resolver_policy": load_json_compatible_yaml(base / "resolver-policy.yml"),
        "risk_gates": load_json_compatible_yaml(base / "risk-gates.yml"),
    }


def normalize_catalog(payload: dict[str, Any]) -> list[dict[str, Any]]:
    models = payload.get("models", [])
    if not isinstance(models, list):
        raise ValueError("catalog: models must be a list")
    normalized: list[dict[str, Any]] = []
    for index, model in enumerate(models, start=1):
        if not isinstance(model, dict):
            raise ValueError(f"catalog: models[{index}] must be an object")
        normalized.append(model)
    return normalized


def candidate_profiles(candidate: dict[str, Any]) -> list[str]:
    profiles = candidate.get("profiles", [])
    if isinstance(profiles, str):
        return [profiles]
    if isinstance(profiles, list):
        return [profile for profile in profiles if isinstance(profile, str)]
    return []


def candidate_label(candidate: dict[str, Any]) -> str:
    return str(candidate.get("id", "<missing-id>"))


def candidate_priority(candidate: dict[str, Any]) -> int:
    try:
        return int(candidate.get("priority", 0))
    except (TypeError, ValueError):
        return 0


def candidate_exclusion_reason(
    candidate: dict[str, Any],
    profile_name: str,
    policy: dict[str, Any],
) -> str | None:
    resolver_policy = policy["resolver_policy"]
    required_fields = resolver_policy["candidate_required_fields"]
    selectable_statuses = set(resolver_policy["selectable_statuses"])
    excluded_statuses = set(resolver_policy["excluded_statuses"])
    smoke_eval_values = set(resolver_policy["smoke_eval_selectable_values"])

    for field in ("id", "profiles"):
        if not candidate.get(field):
            return MISSING_FIELD_REASON

    if profile_name not in candidate_profiles(candidate):
        return None

    for field in required_fields:
        if field in {"id", "profiles"}:
            continue
        if not candidate.get(field):
            return MISSING_FIELD_REASON

    status = candidate.get("status")
    if status in excluded_statuses or status not in selectable_statuses:
        return EXCLUDED_STATUS_REASON

    if candidate.get("smoke_eval") not in smoke_eval_values:
        return SMOKE_EVAL_REASON

    return None


def select_candidate(
    profile_name: str,
    catalog: dict[str, Any],
    policy: dict[str, Any],
) -> tuple[dict[str, Any] | None, list[str]]:
    candidates = normalize_catalog(catalog)
    fallback_reasons: list[str] = []
    selectable: list[dict[str, Any]] = []
    profile_candidates = 0

    for candidate in candidates:
        if profile_name in candidate_profiles(candidate):
            profile_candidates += 1
        reason = candidate_exclusion_reason(candidate, profile_name, policy)
        if reason:
            fallback_reasons.append(f"{reason}:{candidate_label(candidate)}")
            continue
        if profile_name not in candidate_profiles(candidate):
            continue
        selectable.append(candidate)

    if profile_candidates == 0:
        fallback_reasons.append(f"no_candidate_for_profile:{profile_name}")

    if not selectable:
        fallback_reasons.append(f"no_selectable_candidate:{profile_name}")
        return None, fallback_reasons

    selectable.sort(
        key=lambda item: (
            candidate_priority(item),
            str(item.get("id", "")),
        ),
        reverse=True,
    )
    return selectable[0], fallback_reasons


def profile_fallback_chain(
    profile_name: str,
    profiles: dict[str, Any],
) -> list[str]:
    chain: list[str] = []
    seen = {profile_name}
    pending = list(profiles[profile_name].get("fallback_profiles", []))

    while pending:
        fallback = pending.pop(0)
        if fallback in seen or fallback not in profiles:
            continue
        seen.add(fallback)
        chain.append(fallback)
        pending.extend(profiles[fallback].get("fallback_profiles", []))

    return chain


def resolve_route(
    task_class_name: str,
    routing: dict[str, dict[str, Any]],
    catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    task_classes = routing["task_classes"]["task_classes"]
    profiles = routing["capability_profiles"]["capability_profiles"]
    policy = routing["resolver_policy"]
    risk_gates = routing["risk_gates"]["risk_gates"]

    if task_class_name not in task_classes:
        raise ValueError(f"unknown task class: {task_class_name}")

    task_class = task_classes[task_class_name]
    profile_name = task_class["profile"]
    if profile_name not in profiles:
        raise ValueError(
            f"task class {task_class_name} references unknown profile {profile_name}"
        )

    risk_gate = task_class["risk_gate"]
    if risk_gate not in risk_gates:
        raise ValueError(
            f"task class {task_class_name} references unknown risk gate {risk_gate}"
        )

    fallback_reasons: list[str] = []
    selected_model = None
    selection_profile = profile_name
    if catalog is None:
        fallback_reasons.append("catalog_not_provided")
    else:
        for candidate_profile in [profile_name, *profile_fallback_chain(profile_name, profiles)]:
            selected, attempt_reasons = select_candidate(candidate_profile, catalog, policy)
            fallback_reasons.extend(attempt_reasons)
            if selected is None:
                continue
            selected_model = selected.get("id")
            selection_profile = candidate_profile
            if candidate_profile != profile_name:
                fallback_reasons.append(f"profile_fallback_used:{candidate_profile}")
            break

    return {
        "schema_version": 1,
        "task_class": task_class_name,
        "capability_profile": profile_name,
        "selection_profile": selection_profile,
        "prompt_detail": task_class["prompt_detail"],
        "risk_gate": risk_gate,
        "default_effort": task_class.get("default_effort"),
        "selected": selected_model is not None,
        "selected_model": selected_model,
        "fallback_reasons": fallback_reasons,
        "success_criteria": task_class.get("success_criteria", {}),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve a task class into a capability profile and optional model candidate."
    )
    parser.add_argument("task_class", help="Task class name to resolve.")
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root (default: inferred from this script location).",
    )
    parser.add_argument(
        "--catalog",
        default="",
        help="Optional external generated model catalog JSON file.",
    )
    parser.add_argument(
        "--format",
        choices=("json", "text"),
        default="json",
        help="Output format.",
    )
    return parser.parse_args()


def render_text(result: dict[str, Any]) -> str:
    lines = [
        f"task_class: {result['task_class']}",
        f"capability_profile: {result['capability_profile']}",
        f"selection_profile: {result['selection_profile']}",
        f"prompt_detail: {result['prompt_detail']}",
        f"risk_gate: {result['risk_gate']}",
        f"selected: {str(result['selected']).lower()}",
    ]
    if result["selected_model"]:
        lines.append(f"selected_model: {result['selected_model']}")
    if result["fallback_reasons"]:
        lines.append("fallback_reasons:")
        lines.extend(f"- {reason}" for reason in result["fallback_reasons"])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    try:
        repo_root = repo_root_from_args(args.repo_root)
        routing = load_model_routing(repo_root)
        catalog = None
        if args.catalog:
            catalog = load_json_compatible_yaml(Path(args.catalog).resolve())
        result = resolve_route(args.task_class, routing, catalog)
    except ValueError as exc:
        print(f"Model route resolution failed: {exc}")
        return 1

    if args.format == "json":
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
