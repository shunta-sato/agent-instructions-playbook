#!/usr/bin/env python3
"""`learning`-family artifact checks: dispatches between the two shapes the
`learning` checker name covers (`.agents/artifact-registry.json`): the
retrospective pack (`record.json` + `report.md`, `spec["detect_dir_glob"]`
present), checked in this module; and the LLM Wiki (`spec["detect_dir"] ==
".agent/wiki"`), checked in the sibling `artifact_checks_learning_wiki.py`
(split out only to fit the structure budget -- the shapes share no logic
beyond the pack-generic checks imported below).

Shared checker signature (pinned):
``run_checks(repo_root, artifact_path, spec, registry) -> list[str]``.

`required_files` / `forbid_fill_sentinel` / `forbid_symlinks` are reused by
IMPORTING the private functions from `artifact_checks_packs` (dual-path
import below), never copied.

STRUCTURE only: file/field presence, JSON parseability, enum membership, ID
uniqueness/cross-references, path safety, and whether a closure rule's
retention-action precondition is structurally met. Never causal, semantic,
or generalization correctness -- that stays with the owning skill.

Keys starting with `_` in `record.json` are documentation, never schema
fields.

## Finding-id scheme

Stable, line-number-independent `<namespace>:<check>:<detail...>` ids,
namespaced `retro:` (here) or `wiki:` (sibling); pack-generic ids are
re-prefixed.

Retrospective-pack ids: `retro:missing-file|fill-sentinel|symlink-in-pack:
<rel>` (re-prefixed pack-generic) -- `retro:json-parse:record.json` --
`retro:bad-shape:record.json` (parses but not an object) --
`retro:missing-field:<field>` (section 6 top-level field absent) --
`retro:missing-heading:<heading>` (`report.md` missing a section 6 heading;
extra coverage beyond section 8's literal bullets, justified by this task's
mandate to validate `report.md` "per spec section 6 schemas") --
`retro:enum:<field>` (top-level/`recurrence.status`) --
`retro:enum:<field>:<attempt_or_learning_id>` (`result`/`failure_class`/
`preventability` on attempts; `causal_confidence`/`scope`/`enforceability`/
`criticality`/`absorption_decision` on learnings) --
`retro:enum:retention_kind|retention_status:<learning_id>:<index>`
(retention actions carry no id, so indexed by position) --
`retro:duplicate-id:attempt|learning:<id>` --
`retro:empty-evidence-refs:trigger|attempt:<id>|learning:<id>` --
`retro:path:absolute|traversal:<field>:<learning_id>:<index>` (`field` in
`target`, `artifact_path`) -- `retro:id-mismatch:retrospective_id` (report
never mentions record's id) -- `retro:report-missing-id:attempt|learning:
<id>` -- closure rules: `retro:closure:5.1:<learning_id>` (deterministic
learning + a preventable attempt + no active lint/harness action; scoped to
the learning's optional `attempt_refs` when present, else record-level --
the section 6 schema has no attempt-to-learning link),
`retro:closure:5.2:<learning_id>` (repeated recurrence + a preventable
attempt + no active lint/harness/observe-first action),
`retro:closure:5.3:<learning_id>` (project-specific + required-before-
action/submit-blocking + no active project-instruction/local-lint/local-
harness action), `retro:closure:5.4:<learning_id>` (a `new-skill-candidate`
action without a structurally complete `existing_skill_absorption`; 5.6's
banned-vague-action check is a semantic text judgment, out of scope here),
`retro:closure:5.5:<learning_id>:<index>:<field>` (`observe-first` action
missing `signal`/`artifact_path`/`revisit_condition`/`tracking_ref`) --
`retro:action-target-missing:<learning_id>:<index>` (`implemented` action,
`target` absent or missing under `repo_root`) --
`retro:action-missing-tracking-ref:<learning_id>:<index>` (`planned`, no
`tracking_ref`) -- `retro:action-missing-verification:<learning_id>:<index>`
(lint/harness kind, no `verification_commands`).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

try:
    from scripts.artifact_checks_packs import (
        _check_forbid_fill_sentinel,
        _check_forbid_symlinks,
        _check_required_files,
    )
except ImportError:  # pragma: no cover - direct execution without repo root on sys.path
    from artifact_checks_packs import (  # type: ignore[no-redef]
        _check_forbid_fill_sentinel,
        _check_forbid_symlinks,
        _check_required_files,
    )

try:
    from scripts.artifact_checks_learning_wiki import run_checks as _wiki_run_checks
except ImportError:  # pragma: no cover - direct execution without repo root on sys.path
    from artifact_checks_learning_wiki import run_checks as _wiki_run_checks  # type: ignore[no-redef]

REQUIRED_TOP_LEVEL_FIELDS = [
    "schema_version", "retrospective_id", "title", "outcome", "current_work_disposition",
    "trigger", "attempts", "learnings", "recurrence"]
REPORT_REQUIRED_HEADINGS = [
    "Trigger and scope", "Evidence sources", "Attempt sequence",
    "Failed invariants and earliest signals", "Contrast with the final or current attempt",
    "Learning claims", "Promotion decisions", "Rejected non-lessons",
    "Remaining unknowns", "Closure"]

OUTCOME_ENUM = {"recovered", "rolled-back", "abandoned", "unresolved"}
DISPOSITION_ENUM = {"amend-current-work", "harden-repository", "no-durable-change", "insufficient-evidence"}
RECURRENCE_STATUS_ENUM = {"first-seen", "repeated"}
RESULT_ENUM = {"failed", "rejected", "abandoned", "succeeded", "inconclusive"}
FAILURE_CLASS_ENUM = {"assumption", "approach", "routing", "verification", "coordination", "environment"}
PREVENTABILITY_ENUM = {"preventable", "productive-exploration", "unknown"}
CAUSAL_CONFIDENCE_ENUM = {"confirmed", "plausible", "unknown"}
SCOPE_ENUM = {"task-only", "project-specific", "cross-project-reusable"}
ENFORCEABILITY_ENUM = {"explanatory", "model-evaluable", "deterministic"}
CRITICALITY_ENUM = {"advisory", "required-before-action", "submit-blocking"}
RETENTION_KIND_ENUM = {
    "retrospective-only", "llm-wiki", "project-instruction", "existing-skill", "new-skill-candidate",
    "local-lint", "local-harness", "reusable-lint", "reusable-harness", "observe-first", "tracked-follow-up",
}
RETENTION_STATUS_ENUM = {"implemented", "planned", "not-applicable"}
ABSORPTION_DECISION_ENUM = {"absorbed", "not-absorbed", "not-applicable"}

LINT_HARNESS_KINDS = {"local-lint", "local-harness", "reusable-lint", "reusable-harness"}
PROJECT_ENFORCEMENT_KINDS = {"project-instruction", "local-lint", "local-harness"}
ACTIVE_STATUSES = {"implemented", "planned"}
CRITICAL_LEVELS = {"required-before-action", "submit-blocking"}

HEADING_LINE_RE = re.compile(r"^#{1,6}[ \t]+(.*?)[ \t]*$", re.MULTILINE)

def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None

def _actions_of_kind_active(actions: list, kinds: set[str]) -> bool:
    return any(
        isinstance(a, dict) and a.get("kind") in kinds and a.get("status") in ACTIVE_STATUSES
        for a in actions
    )

def _has_absorption_rationale(learning: dict) -> bool:
    absorption = learning.get("existing_skill_absorption")
    if not isinstance(absorption, dict):
        return False
    skills = absorption.get("skills_considered")
    rationale = absorption.get("rationale")
    return bool(skills) and isinstance(rationale, str) and rationale.strip() != ""

try:
    from artifact_checks_learning_fields import (
        _check_object_required_fields,
        _check_ref_safety,
        resolve_attempt_scope,
    )
except ModuleNotFoundError:  # imported as scripts.artifact_checks_learning
    from scripts.artifact_checks_learning_fields import (
        _check_object_required_fields,
        _check_ref_safety,
        resolve_attempt_scope,
    )

def _check_record_top_level(record: dict) -> list[str]:
    findings = [
        f"retro:missing-field:{field}" for field in REQUIRED_TOP_LEVEL_FIELDS if field not in record
    ]
    outcome = record.get("outcome")
    if outcome is not None and outcome not in OUTCOME_ENUM:
        findings.append("retro:enum:outcome")
    disposition = record.get("current_work_disposition")
    if disposition is not None and disposition not in DISPOSITION_ENUM:
        findings.append("retro:enum:current_work_disposition")
    recurrence = record.get("recurrence")
    if isinstance(recurrence, dict):
        status = recurrence.get("status")
        if status is not None and status not in RECURRENCE_STATUS_ENUM:
            findings.append("retro:enum:recurrence.status")
    return findings

def _check_report_headings(report_text: str) -> list[str]:
    present = {m.strip() for m in HEADING_LINE_RE.findall(report_text)}
    return [
        f"retro:missing-heading:{heading}"
        for heading in REPORT_REQUIRED_HEADINGS
        if heading not in present
    ]

def _check_id_cross_checks(record: dict, report_text: str) -> list[str]:
    findings = []
    rid = record.get("retrospective_id")
    if isinstance(rid, str) and rid and rid not in report_text:
        findings.append("retro:id-mismatch:retrospective_id")
    for attempt in record.get("attempts") or []:
        aid = attempt.get("id") if isinstance(attempt, dict) else None
        if isinstance(aid, str) and aid and aid not in report_text:
            findings.append(f"retro:report-missing-id:attempt:{aid}")
    for learning in record.get("learnings") or []:
        lid = learning.get("id") if isinstance(learning, dict) else None
        if isinstance(lid, str) and lid and lid not in report_text:
            findings.append(f"retro:report-missing-id:learning:{lid}")
    return findings

def _check_trigger(record: dict) -> list[str]:
    trigger = record.get("trigger")
    if not isinstance(trigger, dict):
        return []
    refs = trigger.get("evidence_refs")
    return ["retro:empty-evidence-refs:trigger"] if isinstance(refs, list) and not refs else []

def _check_attempts(attempts: list) -> list[str]:
    findings: list[str] = []
    seen_ids: set[str] = set()
    for attempt in attempts:
        if not isinstance(attempt, dict):
            continue
        aid = attempt.get("id")
        if isinstance(aid, str) and aid:
            if aid in seen_ids:
                findings.append(f"retro:duplicate-id:attempt:{aid}")
            seen_ids.add(aid)
        for field, enum in (
            ("result", RESULT_ENUM),
            ("failure_class", FAILURE_CLASS_ENUM),
            ("preventability", PREVENTABILITY_ENUM),
        ):
            value = attempt.get(field)
            if value is not None and value not in enum:
                findings.append(f"retro:enum:{field}:{aid}")
        refs = attempt.get("evidence_refs")
        if isinstance(refs, list) and not refs:
            findings.append(f"retro:empty-evidence-refs:attempt:{aid}")
    return findings

def _check_path_safety(value, field: str, lid, idx: int) -> list[str]:
    if not isinstance(value, str) or not value:
        return []
    findings = []
    if value.startswith("/"):
        findings.append(f"retro:path:absolute:{field}:{lid}:{idx}")
    if any(seg == ".." for seg in value.split("/")):
        findings.append(f"retro:path:traversal:{field}:{lid}:{idx}")
    return findings

def _target_exists(repo_root: Path, target) -> bool:
    if not isinstance(target, str) or not target:
        return False
    if target.startswith("/") or any(seg == ".." for seg in target.split("/")):
        return False  # already reported by path safety; do not resolve outside repo
    return (repo_root / target).exists()

def _check_observe_first_fields(action: dict, lid, idx: int) -> list[str]:
    findings = []
    for field in ("missing_evidence", "signal", "artifact_path", "revisit_condition", "tracking_ref"):
        value = action.get(field)
        if not isinstance(value, str) or not value.strip():
            findings.append(f"retro:closure:5.5:{lid}:{idx}:{field}")
    return findings

def _check_retention_actions(repo_root: Path, actions: list, lid) -> list[str]:
    findings: list[str] = []
    for idx, action in enumerate(actions):
        if not isinstance(action, dict):
            continue
        kind = action.get("kind")
        if kind is not None and kind not in RETENTION_KIND_ENUM:
            findings.append(f"retro:enum:retention_kind:{lid}:{idx}")
        status = action.get("status")
        if status is not None and status not in RETENTION_STATUS_ENUM:
            findings.append(f"retro:enum:retention_status:{lid}:{idx}")
        findings += _check_path_safety(action.get("target"), "target", lid, idx)
        findings += _check_path_safety(action.get("artifact_path"), "artifact_path", lid, idx)
        if status == "implemented" and not _target_exists(repo_root, action.get("target")):
            findings.append(f"retro:action-target-missing:{lid}:{idx}")
        if status == "planned" and not action.get("tracking_ref"):
            findings.append(f"retro:action-missing-tracking-ref:{lid}:{idx}")
        if kind in LINT_HARNESS_KINDS and not action.get("verification_commands"):
            findings.append(f"retro:action-missing-verification:{lid}:{idx}")
        if kind == "observe-first":
            findings += _check_observe_first_fields(action, lid, idx)
    return findings

def _check_learning_enums(learning: dict, lid) -> list[str]:
    findings = []
    for field, enum in (
        ("causal_confidence", CAUSAL_CONFIDENCE_ENUM),
        ("scope", SCOPE_ENUM),
        ("enforceability", ENFORCEABILITY_ENUM),
        ("criticality", CRITICALITY_ENUM),
    ):
        value = learning.get(field)
        if value is not None and value not in enum:
            findings.append(f"retro:enum:{field}:{lid}")
    absorption = learning.get("existing_skill_absorption")
    if isinstance(absorption, dict):
        decision = absorption.get("decision")
        if decision is not None and decision not in ABSORPTION_DECISION_ENUM:
            findings.append(f"retro:enum:absorption_decision:{lid}")
    return findings

def _check_closure_rules(learning: dict, actions: list, any_preventable: bool, repeated: bool) -> list[str]:
    findings = []
    lid = learning.get("id")
    if learning.get("enforceability") == "deterministic" and any_preventable:
        if not _actions_of_kind_active(actions, LINT_HARNESS_KINDS):
            findings.append(f"retro:closure:5.1:{lid}")
    if repeated and any_preventable:
        if not _actions_of_kind_active(actions, LINT_HARNESS_KINDS | {"observe-first"}):
            findings.append(f"retro:closure:5.2:{lid}")
    if learning.get("scope") == "project-specific" and learning.get("criticality") in CRITICAL_LEVELS:
        if not _actions_of_kind_active(actions, PROJECT_ENFORCEMENT_KINDS):
            findings.append(f"retro:closure:5.3:{lid}")
    has_new_skill = any(isinstance(a, dict) and a.get("kind") == "new-skill-candidate" for a in actions)
    if has_new_skill and not _has_absorption_rationale(learning):
        findings.append(f"retro:closure:5.4:{lid}")
    return findings

def _check_learnings(repo_root: Path, learnings: list, attempts: list, record: dict) -> list[str]:
    findings: list[str] = []
    seen_ids: set[str] = set()
    any_preventable = any(isinstance(a, dict) and a.get("preventability") == "preventable" for a in attempts)
    recurrence = record.get("recurrence")
    repeated = isinstance(recurrence, dict) and recurrence.get("status") == "repeated"

    for learning in learnings:
        if not isinstance(learning, dict):
            continue
        lid = learning.get("id")
        if isinstance(lid, str) and lid:
            if lid in seen_ids:
                findings.append(f"retro:duplicate-id:learning:{lid}")
            seen_ids.add(lid)

        findings += _check_learning_enums(learning, lid)

        refs = learning.get("evidence_refs")
        if isinstance(refs, list) and not refs:
            findings.append(f"retro:empty-evidence-refs:learning:{lid}")

        actions = learning.get("retention_actions")
        actions = actions if isinstance(actions, list) else []
        findings += _check_retention_actions(repo_root, actions, lid)
        ref_findings, learning_preventable = resolve_attempt_scope(
            learning, attempts, any_preventable
        )
        findings += ref_findings
        findings += _check_closure_rules(learning, actions, learning_preventable, repeated)

    return findings

def _run_retrospective_checks(repo_root: Path, artifact_path: Path, spec: dict) -> list[str]:
    findings: list[str] = []
    findings += [f"retro:{f}" for f in _check_required_files(artifact_path, spec)]
    findings += [f"retro:{f}" for f in _check_forbid_fill_sentinel(artifact_path, spec)]
    findings += [f"retro:{f}" for f in _check_forbid_symlinks(artifact_path, spec)]

    record_path = artifact_path / "record.json"
    report_path = artifact_path / "report.md"
    if not record_path.is_file() or not report_path.is_file():
        return findings  # already reported by required_files above

    text = _read_text(record_path)
    try:
        record = json.loads(text if text is not None else "")
    except json.JSONDecodeError:
        findings.append("retro:json-parse:record.json")
        return findings
    if not isinstance(record, dict):
        findings.append("retro:bad-shape:record.json")
        return findings

    report_text = _read_text(report_path) or ""

    findings += _check_record_top_level(record)
    findings += _check_object_required_fields(record)
    findings += _check_ref_safety(record)
    findings += _check_report_headings(report_text)
    findings += _check_id_cross_checks(record, report_text)
    findings += _check_trigger(record)

    attempts = record.get("attempts")
    attempts = attempts if isinstance(attempts, list) else []
    learnings = record.get("learnings")
    learnings = learnings if isinstance(learnings, list) else []

    findings += _check_attempts(attempts)
    findings += _check_learnings(repo_root, learnings, attempts, record)

    return findings

def run_checks(repo_root: Path, artifact_path: Path, spec: dict, registry: dict) -> list[str]:
    """Dispatch by artifact shape; see module docstring for the two shapes
    and the full finding-id scheme."""
    if "detect_dir_glob" in spec:
        return _run_retrospective_checks(repo_root, artifact_path, spec)
    if spec.get("detect_dir") == ".agent/wiki":
        return _wiki_run_checks(repo_root, artifact_path, spec, registry)
    raise SystemExit(
        "artifact-lint(learning): spec matches neither the retrospective pack "
        "shape ('detect_dir_glob' key) nor the llm-wiki shape "
        f"('detect_dir' == '.agent/wiki'): {spec!r}"
    )
