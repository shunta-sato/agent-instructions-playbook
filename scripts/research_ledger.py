#!/usr/bin/env python3
"""Shared primitives for the Research OS ledger — the single source of truth
the producer (``research_run``) and the checker (``check_research_evidence`` +
``research_gate``) agree on (hashing, chain, digests, threshold/equivalence
predicate + outcome, claim binding/direction/n, axis-key binding, claims view),
so the validator re-derives exactly what the runner wrote. Records chain over
their own subsequence of the shared JSONL. Tamper-EVIDENT, NOT tamper-PROOF
(adversarial anchoring is a follow-up). Stdlib only."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import operator
import shlex
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

# Disconfirm-predicate shapes (R2b). Legacy records carry no ``type`` and are
# read as ``threshold``; ``equivalence`` is the structured no-effect predicate.
PREDICATE_THRESHOLD = "threshold"
PREDICATE_EQUIVALENCE = "equivalence"

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

def predicate_type(disconfirm: Any) -> str:
    """A disconfirm's predicate shape. Records without a ``type`` are legacy
    threshold predicates; only ``type == "equivalence"`` selects the bounds shape."""
    if isinstance(disconfirm, dict) and disconfirm.get("type") == PREDICATE_EQUIVALENCE:
        return PREDICATE_EQUIVALENCE
    return PREDICATE_THRESHOLD

def validate_predicate(disconfirm: Any) -> list[str]:
    """Well-formedness errors for a disconfirm predicate (threshold or
    equivalence). R1: a non-finite bound (NaN/±Inf) is ill-defined, so it is
    refused at registration, re-flagged by the gate, and fails any citing claim;
    an equivalence predicate also needs lower < upper for a real interval."""
    errors: list[str] = []
    if not isinstance(disconfirm, dict):
        return ["disconfirm must be an object"]
    if not isinstance(disconfirm.get("metric"), str) or not disconfirm.get("metric"):
        errors.append("disconfirm.metric must be a non-empty string")
    if predicate_type(disconfirm) == PREDICATE_EQUIVALENCE:
        lower, upper = disconfirm.get("lower"), disconfirm.get("upper")
        for name, value in (("lower", lower), ("upper", upper)):
            if not _is_number(value):
                errors.append(f"disconfirm.{name} must be a number")
            elif not math.isfinite(value):
                errors.append(f"disconfirm.{name} must be finite (not NaN/Inf)")
        if _is_number(lower) and _is_number(upper) and math.isfinite(lower) \
                and math.isfinite(upper) and not lower < upper:
            errors.append("disconfirm.lower must be < disconfirm.upper")
        return errors
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
    """Disconfirm predicate → disconfirmed/supported/not-evaluable. Threshold:
    the comparator holds. Equivalence: value OUTSIDE ``[lower, upper]`` (supported
    == within bounds == no effect). ``not-evaluable`` if metric missing/non-finite/non-numeric."""
    metric = disconfirm.get("metric")
    if not isinstance(metrics, dict) or metric not in metrics:
        return "not-evaluable"
    value = metrics[metric]
    if _is_number(value) and not math.isfinite(value):
        return "not-evaluable"
    if predicate_type(disconfirm) == PREDICATE_EQUIVALENCE:
        if not _is_number(value):  # bounds are ordered comparisons
            return "not-evaluable"
        disconfirmed = value < disconfirm["lower"] or value > disconfirm["upper"]
        return "disconfirmed" if disconfirmed else "supported"
    comparator = disconfirm["comparator"]
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

def _tokenize(command: str) -> list[str]:
    """shlex tokenization, falling back to whitespace split on an unbalanced
    quote so a malformed command still yields a stable token list."""
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()

def _bound_value_positions(tokens: list[str], key: str, value: str) -> list[int]:
    """R3: token indices where ``value`` is bound to option ``key`` — an inline
    ``--key=value``/``key=value`` token, or a ``--key``/``-key`` flag followed by
    ``value``. A bare ``value`` under a different option (the ``1`` in
    ``--output=1`` for key ``seed``) is NOT a position."""
    inline = {f"--{key}={value}", f"{key}={value}"}
    flags = {f"--{key}", f"-{key}"}
    positions: list[int] = []
    for index, token in enumerate(tokens):
        if token in inline:
            positions.append(index)
        elif token in flags and index + 1 < len(tokens) and tokens[index + 1] == value:
            positions.append(index + 1)
    return positions

def axis_key_bound_in_command(key: str, value: str, command: str) -> bool:
    """True when ``value`` is bound to option ``key`` at least once (a real knob)."""
    return bool(_bound_value_positions(_tokenize(command), key, value))

def _templatize_command(command: str, key: str, value: str) -> str:
    """Blank ONLY the key-bound occurrences of ``value`` (keeping any ``--key=``
    prefix) so commands differing solely in the axis value share a template; a
    same-valued token under a different option is left intact (R3)."""
    tokens = _tokenize(command)
    positions = set(_bound_value_positions(tokens, key, value))
    out: list[str] = []
    for index, token in enumerate(tokens):
        if index not in positions:
            out.append(token)
        elif token.endswith("=" + value):  # inline --key=value / key=value
            out.append(token[: -len(value)] + AXIS_PLACEHOLDER)
        else:  # standalone value token following the flag
            out.append(AXIS_PLACEHOLDER)
    return " ".join(out)

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
    templates = {_templatize_command(cmd, key, val) for val, cmd in entries}
    raws = [cmd for _val, cmd in entries]
    if len(templates) != 1:
        return 1, f"n=1: axis {key!r} substitution leaves commands differing at a non-axis position"
    if len(set(raws)) != len(raws):
        return 1, f"n=1: cited commands on axis {key!r} are not pairwise distinct"
    return len(raws), f"n={len(raws)}: distinct values on axis key {key!r} over a common command template"

def claim_n(records: list[dict[str, Any]], evidence_ids: list[str]) -> int:
    """The integer multiplicity only; see ``claim_n_and_note`` for the basis."""
    return claim_n_and_note(records, evidence_ids)[0]

def claim_axis_key(records: list[dict[str, Any]], evidence_ids: list[str]) -> str | None:
    """The single variation-axis KEY shared by the cited evidence, or ``None``
    when the evidence declares no axis or mixes keys (used by the claims view)."""
    keys: set[str] = set()
    for eid in evidence_ids:
        prereg = find_preregister(records, eid)
        parsed = _axis_key_value(prereg.get("variation_axis")) if prereg else None
        if parsed is not None:
            keys.add(parsed[0])
    return next(iter(keys)) if len(keys) == 1 else None

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
    cited registration using an equivalence-bounds predicate (R2b); disconfirmed
    → ``mixed`` only. Grandfathered/threshold evidence backs only ``mixed``;
    pre-F2 claims skip F2."""
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
            elif not all(
                predicate_type((find_preregister(records, e) or {}).get("disconfirm")) == PREDICATE_EQUIVALENCE
                for e in evidence_ids
            ):
                errors.append(
                    "direction no-effect requires every registration to use an"
                    " --equivalence-bounds predicate (grandfathered/threshold evidence backs only mixed)"
                )
    return errors, basis

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
        # R2a: the claim sentence is built EXCLUSIVELY from structured fields
        # (metric/direction/n/axis-key); a grandfathered ``effect`` is ignored.
        metric, direction = claim["metric"], claim["direction"]
        if n == 1:
            sentence = f"{metric} {direction} — observed in a single configuration."
        else:
            axis_key = claim_axis_key(records, claim["evidence"]) or "variation-axis"
            sentence = f"{metric} {direction} — observed across {n} distinct {axis_key} configurations."
        lines.append(f"## {claim['claim_id']}")
        lines.append(sentence)
        if claim.get("configurations"):
            lines.append(f"configurations: {', '.join(claim['configurations'])}")
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
