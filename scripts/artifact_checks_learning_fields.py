#!/usr/bin/env python3
"""Record-shape checks for the failure-retrospective pack, split from
``scripts/artifact_checks_learning.py`` (structure budget): per-object
required fields (review fix F1) and evidence-ref path-shape safety (F6).
Finding-id scheme and the structural-only mandate are documented in the
main module."""

from __future__ import annotations

ATTEMPT_REQUIRED_FIELDS = (
    "id", "hypothesis_or_approach", "evidence_sought", "evidence_refs",
    "result", "failure_class", "preventability", "changed_next",
)
LEARNING_REQUIRED_FIELDS = (
    "id", "claim", "evidence_refs", "causal_confidence", "scope",
    "enforceability", "criticality", "existing_skill_absorption",
    "retention_actions",
)
DURABLE_DISPOSITIONS = {"harden-repository", "amend-current-work"}


def _check_object_required_fields(record: dict) -> list[str]:
    """F1: the closure rules read per-object fields, so their absence must be
    a finding — an omitted enforceability or preventability would otherwise
    silently disable rules 5.1-5.3."""
    findings: list[str] = []
    for attempt in record.get("attempts") or []:
        if not isinstance(attempt, dict):
            continue
        aid = attempt.get("id") or "<unnamed>"
        for field in ATTEMPT_REQUIRED_FIELDS:
            if field not in attempt:
                findings.append(f"retro:missing-field:attempt:{aid}:{field}")
    for learning in record.get("learnings") or []:
        if not isinstance(learning, dict):
            continue
        lid = learning.get("id") or "<unnamed>"
        for field in LEARNING_REQUIRED_FIELDS:
            if field not in learning:
                findings.append(f"retro:missing-field:learning:{lid}:{field}")
    disposition = record.get("current_work_disposition")
    if disposition in DURABLE_DISPOSITIONS and not (record.get("learnings") or []):
        findings.append(f"retro:empty-learnings:{disposition}")
    return findings


def _check_ref_safety(record: dict) -> list[str]:
    """F6: evidence_refs / prior_records never resolve to files, but a rooted
    or traversal-shaped ref must still fail — the record would otherwise
    carry pointers outside the repo."""
    findings: list[str] = []

    def sweep(values, where: str) -> None:
        for i, v in enumerate(values or []):
            if not isinstance(v, str):
                continue
            if v.startswith("/"):
                findings.append(f"retro:path:absolute:{where}:{i}")
            if any(seg == ".." for seg in v.split("/")):
                findings.append(f"retro:path:traversal:{where}:{i}")

    trigger = record.get("trigger")
    if isinstance(trigger, dict):
        sweep(trigger.get("evidence_refs"), "trigger.evidence_refs")
    for attempt in record.get("attempts") or []:
        if isinstance(attempt, dict):
            sweep(attempt.get("evidence_refs"), f"attempt:{attempt.get('id') or '<unnamed>'}")
    for learning in record.get("learnings") or []:
        if isinstance(learning, dict):
            sweep(learning.get("evidence_refs"), f"learning:{learning.get('id') or '<unnamed>'}")
    recurrence = record.get("recurrence")
    if isinstance(recurrence, dict):
        sweep(recurrence.get("prior_records"), "recurrence.prior_records")
    return findings




def resolve_attempt_scope(
    learning: dict, attempts: list, any_preventable: bool
) -> tuple[list[str], bool]:
    """Closure rules 5.1/5.2 use the learning's optional ``attempt_refs``
    scope when it resolves; an unresolvable ref is a finding, and a wholly
    unresolvable list falls back to the record-level correlation — a broken
    reference must fail closed, never silence the rules (review F16)."""
    refs = learning.get("attempt_refs")
    if not (isinstance(refs, list) and refs):
        return [], any_preventable
    by_id = {a.get("id"): a for a in attempts if isinstance(a, dict)}
    lid = learning.get("id") or "<unnamed>"
    findings = [f"retro:unknown-attempt-ref:{lid}:{r}" for r in refs if r not in by_id]
    scoped = [by_id[r] for r in refs if r in by_id]
    if scoped:
        return findings, any(a.get("preventability") == "preventable" for a in scoped)
    return findings, any_preventable
