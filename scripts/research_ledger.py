#!/usr/bin/env python3
"""Shared primitives for the Research OS ledger — the single source of truth
the producer (``research_run``) and the gate (``check_research_evidence``)
agree on (hashing, chain, digests, predicate/outcome, claim binding/effect/n,
claims view, promotion-ack evidence), so the validator re-derives exactly what
the runner wrote. Records chain over their own subsequence of the shared JSONL.
Tamper-EVIDENT, NOT tamper-PROOF (adversarial anchoring is a follow-up).
Stdlib only."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import operator
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
LEDGER_REL = ".agents/runs/agent-runs.jsonl"
# Runner-generated artifacts; disposable, never a command_digest input.
RUNNER_OUTPUT_REL = "research/runs"

PREREGISTER = "experiment_preregister"
EXPLORATION = "experiment_exploration"
RESULT = "experiment_result"
CLAIM = "research_claim"
RESEARCH_TYPES = (PREREGISTER, EXPLORATION, RESULT, CLAIM)

COMPARATORS = ("<", "<=", ">", ">=", "==")
DIRECTIONS = ("improves", "degrades", "no-effect", "mixed")

class LedgerError(Exception):
    """Raised when the ledger cannot be parsed or a record is malformed."""

def canonical_json(obj: Any) -> str:
    """Deterministic JSON serialization (sorted keys, compact separators)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))

def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()

def compute_hash(record: dict[str, Any]) -> str:
    """Hash a record's canonical JSON with the ``chain.hash`` field absent."""
    payload = dict(record)
    chain = dict(payload.get("chain") or {})
    chain.pop("hash", None)
    payload["chain"] = chain
    return sha256_text(canonical_json(payload))

def stamp_utc() -> str:
    """Runner-stamped microsecond UTC timestamp (never caller-supplied)."""
    return dt.datetime.now(dt.timezone.utc).isoformat()

def load_research_records(ledger_path: Path) -> list[dict[str, Any]]:
    """Research records in file order; ``agent_run`` records are skipped."""
    records: list[dict[str, Any]] = []
    if not ledger_path.is_file():
        return records
    for line_no, raw in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise LedgerError(f"{ledger_path}:{line_no}: invalid JSON: {exc.msg}") from exc
        if isinstance(payload, dict) and payload.get("record_type") in RESEARCH_TYPES:
            records.append(payload)
    return records

def append_jsonl(ledger_path: Path, record: dict[str, Any]) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(record))
        handle.write("\n")

def chain_and_append(ledger_path: Path, record: dict[str, Any]) -> dict[str, Any]:
    """Link ``record`` onto the research chain and append it to the ledger."""
    existing = load_research_records(ledger_path)
    prev = existing[-1]["chain"]["hash"] if existing else None
    record["chain"] = {"prev": prev}
    record["chain"]["hash"] = compute_hash(record)
    append_jsonl(ledger_path, record)
    return record

def next_counter(records: list[dict[str, Any]], record_type: str, prefix: str) -> str:
    count = sum(1 for r in records if r.get("record_type") == record_type)
    return f"{prefix}-{count + 1:04d}"

def _find(records: list[dict[str, Any]], rtype: str, eid: str) -> dict[str, Any] | None:
    return next((r for r in records
                 if r.get("record_type") == rtype and r.get("experiment_id") == eid), None)

def find_preregister(records: list[dict[str, Any]], experiment_id: str) -> dict[str, Any] | None:
    return _find(records, PREREGISTER, experiment_id)

def find_result(records: list[dict[str, Any]], experiment_id: str) -> dict[str, Any] | None:
    return _find(records, RESULT, experiment_id)

def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)

def validate_predicate(disconfirm: Any) -> list[str]:
    """Well-formedness errors for a disconfirm predicate. R1: a non-finite
    threshold (NaN/±Inf) makes every comparison ill-defined, so it is refused
    at registration, re-flagged by the gate, and fails any claim citing it."""
    errors: list[str] = []
    if not isinstance(disconfirm, dict):
        return ["disconfirm must be an object"]
    if not isinstance(disconfirm.get("metric"), str) or not disconfirm.get("metric"):
        errors.append("disconfirm.metric must be a non-empty string")
    if disconfirm.get("comparator") not in COMPARATORS:
        errors.append(f"disconfirm.comparator must be one of {list(COMPARATORS)}")
    threshold = disconfirm.get("threshold")
    if not _is_number(threshold):
        errors.append("disconfirm.threshold must be a number")
    elif not math.isfinite(threshold):
        errors.append("disconfirm.threshold must be finite (not NaN/Inf)")
    return errors

_COMPARATOR_OPS = {
    "<": operator.lt, "<=": operator.le, ">": operator.gt,
    ">=": operator.ge, "==": operator.eq,
}

def apply_comparator(comparator: str, lhs: Any, rhs: Any) -> bool:
    try:
        return bool(_COMPARATOR_OPS[comparator](lhs, rhs))
    except KeyError as exc:
        raise LedgerError(f"unknown comparator: {comparator}") from exc

def derive_outcome(disconfirm: dict[str, Any], metrics: Any) -> str:
    """Disconfirm predicate: TRUE=disconfirmed; ``not-evaluable`` if the metric
    is missing/non-object, non-finite, or non-numeric under an order comparator."""
    metric = disconfirm.get("metric")
    if not isinstance(metrics, dict) or metric not in metrics:
        return "not-evaluable"
    comparator = disconfirm["comparator"]
    value = metrics[metric]
    if _is_number(value) and not math.isfinite(value):
        return "not-evaluable"
    if comparator in ("<", "<=", ">", ">=") and not _is_number(value):
        return "not-evaluable"
    disconfirmed = apply_comparator(comparator, value, disconfirm["threshold"])
    return "disconfirmed" if disconfirmed else "supported"

def command_digest(git_head: str, dirty_files: list[dict[str, str]], command: str) -> str:
    parts = [git_head]
    for entry in sorted(dirty_files, key=lambda e: (e["path"], e["sha256"])):
        parts.append(f"{entry['path']}\x00{entry['sha256']}")
    parts.append(command)
    return sha256_text("\n".join(parts))

def multiplicity(prior_records: list[dict[str, Any]], digest: str) -> int:
    """Count prior exploration + result records sharing a command digest."""
    return sum(1 for r in prior_records
               if r.get("record_type") in (EXPLORATION, RESULT) and r.get("command_digest") == digest)

def _axis_key_value(axis: Any) -> tuple[str, str] | None:
    """Parse ``variation_axis`` into ``(key, value)`` (split on first ``=``,
    both parts non-empty); absent/non-conforming axes return ``None``."""
    if not isinstance(axis, str) or "=" not in axis:
        return None
    key, value = axis.split("=", 1)
    if not key or not value:
        return None
    return key, value

AXIS_PLACEHOLDER = "\x00AXIS\x00"

def _axis_token_match(token: str, value: str) -> bool:
    """R3: ``value`` is a WHOLE token — its own argv token or the value side of a
    ``key=value`` token — never a bare substring (``seed=7`` !~ ``--seed 77``)."""
    return token == value or ("=" in token and token.split("=", 1)[1] == value)

def axis_value_in_command(value: str, command: str) -> bool:
    return any(_axis_token_match(tok, value) for tok in command.split())

def _templatize_command(command: str, value: str) -> str:
    """Blank whole-token occurrences of the axis value (keeping any ``key=``
    prefix) so commands differing ONLY in the axis value share a template (R3)."""
    def sub(tok: str) -> str:
        if tok == value:
            return AXIS_PLACEHOLDER
        if "=" in tok and tok.split("=", 1)[1] == value:
            return tok.split("=", 1)[0] + "=" + AXIS_PLACEHOLDER
        return tok
    return " ".join(sub(tok) for tok in command.split())

def claim_n_and_note(records: list[dict[str, Any]], evidence_ids: list[str]) -> tuple[int, str]:
    """Conservative multiplicity + note (R3): ``n>1`` needs cited evidence to
    share one axis KEY and, after blanking axis-value tokens, identical command
    templates over pairwise-distinct raw commands; any binding failure
    conservatively yields n=1 + note, never an error."""
    keys_seen: set[str] = set()
    entries: list[tuple[str, str]] = []  # (axis value, registered command)
    for eid in evidence_ids:
        prereg = find_preregister(records, eid)
        result = find_result(records, eid)
        if prereg is None or result is None:
            continue
        parsed = _axis_key_value(prereg.get("variation_axis"))
        if parsed is None:
            continue
        key, value = parsed
        keys_seen.add(key)
        entries.append((value, prereg.get("command", "")))
    if not keys_seen:
        return 1, "n=1: no conforming variation axis"
    if len(keys_seen) > 1:
        return 1, f"n=1: evidence mixes axis keys {sorted(keys_seen)}"
    (key,) = tuple(keys_seen)
    templates = {_templatize_command(cmd, val) for val, cmd in entries}
    raws = [cmd for _val, cmd in entries]
    if len(templates) != 1:
        return 1, f"n=1: axis {key!r} substitution leaves commands differing at a non-axis position"
    if len(set(raws)) != len(raws):
        return 1, f"n=1: cited commands on axis {key!r} are not pairwise distinct"
    return len(raws), f"n={len(raws)}: distinct values on axis key {key!r} over a common command template"

def claim_n(records: list[dict[str, Any]], evidence_ids: list[str]) -> int:
    """The integer multiplicity only; see ``claim_n_and_note`` for the basis."""
    return claim_n_and_note(records, evidence_ids)[0]

def evaluate_claim_binding(
    records: list[dict[str, Any]],
    metric: str,
    direction: str,
    evidence_ids: list[str],
    enforce_direction: bool = True,
) -> tuple[list[str], list[dict[str, str]]]:
    """Re-derive a claim's binding → ``(errors, outcome_basis)``: (a) claim
    metric == every cited prereg's metric with a valid predicate (R1); (b) each
    result is real evidence (exit 0, supported/disconfirmed); (c) direction
    agrees — improves/degrades all supported (F2: matching preregistered
    direction under ``enforce_direction``); no-effect all supported AND every
    reg flagged ``no_effect_predicate`` (R2b); disconfirmed → ``mixed`` only.
    Grandfathered evidence backs only ``mixed``; pre-F2 claims skip F2."""
    errors: list[str] = []
    basis: list[dict[str, str]] = []
    for eid in evidence_ids:
        prereg = find_preregister(records, eid)
        result = find_result(records, eid)
        if prereg is None or result is None:
            errors.append(f"{eid}: no completed experiment result")
            continue
        pre_metric = (prereg.get("disconfirm") or {}).get("metric")
        if pre_metric != metric:
            errors.append(f"{eid}: claim metric {metric!r} != preregistered {pre_metric!r}")
        if validate_predicate(prereg.get("disconfirm")):  # R1
            errors.append(f"{eid}: preregistration predicate is invalid")
        outcome = result.get("outcome")
        if result.get("exit_code") != 0:
            errors.append(f"{eid}: result exit_code {result.get('exit_code')!r} is not evidence")
        if outcome not in ("supported", "disconfirmed"):
            errors.append(f"{eid}: outcome {outcome!r} is not evidence")
        basis.append({"experiment_id": eid, "outcome": outcome})
    outcomes = [b["outcome"] for b in basis]
    if outcomes:
        if direction in ("improves", "degrades"):
            if not all(o == "supported" for o in outcomes):
                errors.append(f"direction {direction} requires all evidence outcomes supported")
            elif enforce_direction:
                for eid in evidence_ids:
                    pre_dir = (find_preregister(records, eid) or {}).get("direction_if_supported")
                    if pre_dir != direction:
                        errors.append(
                            f"{eid}: preregistered direction {pre_dir!r} != claim {direction!r}"
                            " (grandfathered evidence backs only no-effect/mixed)"
                        )
        elif direction == "no-effect":
            if not all(o == "supported" for o in outcomes):
                errors.append("direction no-effect requires all evidence outcomes supported")
            elif not all((find_preregister(records, e) or {}).get("no_effect_predicate") for e in evidence_ids):
                errors.append(
                    "direction no-effect requires every registration flagged --no-effect-predicate"
                    " (grandfathered/effect-testing evidence backs only mixed)"
                )
    return errors, basis

def derive_effect(
    records: list[dict[str, Any]], evidence_ids: list[str]
) -> tuple[list[str], str, list[dict[str, Any]]]:
    """R2a: a claim's effect is INHERITED from its cited registrations, which
    must agree (else error); an absent effect field yields an empty effect
    (grandfathered/effect-less) and the neutral render sentence."""
    basis = [{"experiment_id": eid, "effect": (find_preregister(records, eid) or {}).get("effect")}
             for eid in evidence_ids]
    values = {b["effect"] for b in basis}
    errors = ([] if len(values) <= 1
              else [f"cited registrations disagree on effect: {sorted(str(v) for v in values)}"])
    return errors, (next(iter(values)) if len(values) == 1 else None) or "", basis

def claims_view_path(repo_root: Path, ledger_path: Path) -> Path:
    """Canonical ledger → ``research/claims.md``; any other → adjacent ``claims.md``."""
    if ledger_path.resolve() == (repo_root / LEDGER_REL).resolve():
        return repo_root / "research" / "claims.md"
    return ledger_path.parent / "claims.md"

def render_claims(records: list[dict[str, Any]]) -> str:
    """Deterministic, template-generated claims view (no timestamps in body)."""
    head = records[-1]["chain"]["hash"] if records else "none"
    lines = ["# Research claims", "", f"ledger-head: {head}", ""]
    claims = sorted(
        (r for r in records if r.get("record_type") == CLAIM),
        key=lambda r: r["claim_id"],
    )
    for claim in claims:
        n = claim["n"]
        configs = ", ".join(claim["configurations"])
        # R2a: sentences use preregistered fields only; an effect-less claim
        # renders a neutral machine sentence.
        effect = claim.get("effect") or ""
        tail = (
            f"{effect} ({claim['metric']} {claim['direction']})" if effect
            else f"{claim['metric']} {claim['direction']} observed"
        )
        if n == 1:
            sentence = f"Observed once under configuration {configs}: {tail}."
        else:
            sentence = f"Observed across {n} distinct configurations: {tail}."
        lines.append(f"## {claim['claim_id']}")
        lines.append(sentence)
        lines.append(f"evidence: {', '.join(claim['evidence'])}")
        if claim.get("outcome_basis"):
            basis = ", ".join(f"{b['experiment_id']}={b['outcome']}" for b in claim["outcome_basis"])
            lines.append(f"outcome-basis: {basis}")
        if claim.get("direction_basis"):
            db = ", ".join(f"{b['experiment_id']}={b['direction_if_supported']}" for b in claim["direction_basis"])
            lines.append(f"direction-basis: {db}")
        if claim.get("n_basis"):
            lines.append(f"n-basis: {claim['n_basis']}")
        if claim.get("sources"):
            lines.append(f"sources: {', '.join(claim['sources'])}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"

# --- promotion-acknowledgment evidence (R4): bind an ack to agent_run records
# on the same JSONL so the gate re-derives coverage from recorded runs --------
AGENT_RUN = "agent_run"

def load_agent_runs(repo_root: Path) -> dict[str, dict[str, Any]]:
    """Canonical ``agent_run`` records indexed by run_id (empty if absent)."""
    path = repo_root / LEDGER_REL
    runs: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return runs
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(rec, dict) and rec.get("record_type") == AGENT_RUN and rec.get("run_id"):
            runs[rec["run_id"]] = rec
    return runs

def _run_validation_passed(run: dict[str, Any]) -> bool:
    """Accept either ``validation.passed`` or ``outcome.validation_passed``."""
    v, o = run.get("validation"), run.get("outcome")
    return (isinstance(v, dict) and v.get("passed") is True) or (
        isinstance(o, dict) and o.get("validation_passed") is True)

def ack_evidence_gaps(
    claim_ids: list[str], run_ids: list[str], valid_claims: set[str], runs: dict[str, dict[str, Any]]
) -> list[str]:
    """R4.1/R4.2: reasons an otherwise-structural acknowledgment fails to bind
    to ledger evidence (unresolved claim, unknown run, or failed-validation run)."""
    gaps = [f"claim {cid} does not resolve in the canonical ledger"
            for cid in claim_ids if cid not in valid_claims]
    for rid in run_ids:
        run = runs.get(rid)
        if run is None:
            gaps.append(f"unknown Delivery-run {rid}")
        elif not _run_validation_passed(run):
            gaps.append(f"Delivery-run {rid} did not pass validation")
    return gaps

def union_covers(path: str, union: set[str]) -> bool:
    """R4.3: is ``path`` in the union of cited runs' changed/allowed files? A
    listed dir (``dir/`` or ``dir/**``) covers its subtree; a trailing
    ``(via ... only)`` annotation is ignored."""
    for entry in union:
        base = entry.split(" ", 1)[0].rstrip("*")
        if base and (path == base or path.startswith(base if base.endswith("/") else base + "/")):
            return True
    return False
