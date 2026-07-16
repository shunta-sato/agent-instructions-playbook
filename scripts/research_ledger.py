#!/usr/bin/env python3
"""Shared Research OS ledger primitives — single source of truth for producer + checker (hashing, chain, predicate/outcome, claim binding/category/n, claims view)."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import operator
import re
import shlex
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
LEDGER_REL = ".agents/runs/agent-runs.jsonl"
RUNNER_OUTPUT_REL = "research/runs"  # runner-generated artifacts; disposable, never a command_digest input.

PREREGISTER = "experiment_preregister"
EXPLORATION = "experiment_exploration"
RESULT = "experiment_result"
CLAIM = "research_claim"
RESEARCH_TYPES = (PREREGISTER, EXPLORATION, RESULT, CLAIM)
COMPARATORS = ("<", "<=", ">", ">=", "==")

CATEGORY_SUPPORTED = "supported"  # B1: a claim's category is machine-derived, never caller-supplied.
CATEGORY_WITHIN_BOUNDS = "within-bounds"
CATEGORY_DISCONFIRMED = "disconfirmed"
CATEGORY_MIXED = "mixed"
PREDICATE_THRESHOLD = "threshold"  # R2b; legacy records with no ``type`` read as threshold.
PREDICATE_EQUIVALENCE = "equivalence"

class LedgerError(Exception):
    """Raised when the ledger cannot be parsed or a record is malformed."""

def canonical_json(obj: Any) -> str:
    """Deterministic JSON serialization (sorted keys, compact separators)."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))

def sha256_text(text: str) -> str: return hashlib.sha256(text.encode("utf-8")).hexdigest()

def sha256_file(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()

def compute_hash(record: dict[str, Any]) -> str:
    """Hash a record's canonical JSON with the ``chain.hash`` field absent."""
    chain = {k: v for k, v in (record.get("chain") or {}).items() if k != "hash"}
    return sha256_text(canonical_json({**record, "chain": chain}))

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
        handle.write(canonical_json(record) + "\n")

def chain_and_append(ledger_path: Path, record: dict[str, Any]) -> dict[str, Any]:
    """Link ``record`` onto the research chain and append it to the ledger."""
    existing = load_research_records(ledger_path)
    record["chain"] = {"prev": existing[-1]["chain"]["hash"] if existing else None}
    record["chain"]["hash"] = compute_hash(record)
    append_jsonl(ledger_path, record); return record

def next_counter(records: list[dict[str, Any]], record_type: str, prefix: str) -> str:
    return f"{prefix}-{sum(1 for r in records if r.get('record_type') == record_type) + 1:04d}"

def find_preregister(records: list[dict[str, Any]], experiment_id: str) -> dict[str, Any] | None:
    return next((r for r in records if r.get("record_type") == PREREGISTER and r.get("experiment_id") == experiment_id), None)

def find_result(records: list[dict[str, Any]], experiment_id: str) -> dict[str, Any] | None:
    return next((r for r in records if r.get("record_type") == RESULT and r.get("experiment_id") == experiment_id), None)

def _is_number(value: Any) -> bool: return isinstance(value, (int, float)) and not isinstance(value, bool)

def predicate_type(disconfirm: Any) -> str:
    """A disconfirm's predicate shape; legacy (no ``type``) records are ``threshold``."""
    valid = isinstance(disconfirm, dict) and disconfirm.get("type") == PREDICATE_EQUIVALENCE
    return PREDICATE_EQUIVALENCE if valid else PREDICATE_THRESHOLD

def validate_predicate(disconfirm: Any) -> list[str]:
    """Well-formedness errors for a disconfirm predicate (R1: non-finite refused; equivalence needs lower < upper)."""
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
        if _is_number(lower) and _is_number(upper) and math.isfinite(lower) and math.isfinite(upper) and not lower < upper:
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

_COMPARATOR_OPS = {"<": operator.lt, "<=": operator.le, ">": operator.gt, ">=": operator.ge, "==": operator.eq}

def apply_comparator(comparator: str, lhs: Any, rhs: Any) -> bool:
    try:
        return bool(_COMPARATOR_OPS[comparator](lhs, rhs))
    except KeyError as exc:
        raise LedgerError(f"unknown comparator: {comparator}") from exc

def derive_outcome(disconfirm: dict[str, Any], metrics: Any) -> str:
    """Disconfirm -> disconfirmed/supported/not-evaluable (threshold: comparator holds; equivalence: outside [lower,upper])."""
    metric = disconfirm.get("metric")
    if not isinstance(metrics, dict) or metric not in metrics:
        return "not-evaluable"
    value = metrics[metric]
    if _is_number(value) and not math.isfinite(value):
        return "not-evaluable"
    if predicate_type(disconfirm) == PREDICATE_EQUIVALENCE:
        if not _is_number(value):  # bounds are ordered comparisons
            return "not-evaluable"
        return "disconfirmed" if (value < disconfirm["lower"] or value > disconfirm["upper"]) else "supported"
    comparator = disconfirm["comparator"]
    if comparator in ("<", "<=", ">", ">=") and not _is_number(value):
        return "not-evaluable"
    return "disconfirmed" if apply_comparator(comparator, value, disconfirm["threshold"]) else "supported"

def command_digest(git_head: str, dirty_files: list[dict[str, str]], command: str) -> str:
    dirty = [f"{e['path']}\x00{e['sha256']}" for e in sorted(dirty_files, key=lambda e: (e["path"], e["sha256"]))]
    return sha256_text("\n".join([git_head] + dirty + [command]))

def multiplicity(prior_records: list[dict[str, Any]], digest: str) -> int:
    """Count prior exploration + result records sharing a command digest."""
    return sum(1 for r in prior_records if r.get("record_type") in (EXPLORATION, RESULT) and r.get("command_digest") == digest)

SHELL_METACHARACTERS = ";&|<>`$()\n"

def command_is_simple(command: str) -> bool:
    """No shell metacharacters: ``shlex.split`` tokens are then exactly the argv a ``shell=False`` process receives."""
    return not any(ch in command for ch in SHELL_METACHARACTERS)

def _axis_key_value(axis: Any) -> tuple[str, str] | None:
    """Parse ``variation_axis`` into ``(key, value)`` (split on first ``=``, both parts non-empty); else ``None``."""
    if not isinstance(axis, str) or "=" not in axis:
        return None
    key, value = axis.split("=", 1)
    return (key, value) if key and value else None

AXIS_PLACEHOLDER = "\x00AXIS\x00"

def _tokenize(command: str) -> list[str]:
    """shlex tokenization, falling back to whitespace split on an unbalanced quote."""
    try:
        return shlex.split(command)
    except ValueError:
        return command.split()

def _bound_value_positions(tokens: list[str], key: str, value: str) -> list[int]:
    """R3: indices where ``value`` is bound to option ``key`` (inline ``--key=value`` or ``--key value``)."""
    inline = {f"--{key}={value}", f"{key}={value}"}
    flags = {f"--{key}", f"-{key}"}
    positions: list[int] = []
    for index, token in enumerate(tokens):
        if token in inline:
            positions.append(index)
        elif token in flags and index + 1 < len(tokens) and tokens[index + 1] == value:
            positions.append(index + 1)
    return positions

def _templatize_command(command: str, key: str, value: str) -> str:
    """Blank ONLY key-bound occurrences of ``value`` so axis-value-only diffs share a template (R3)."""
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

_ENV_ASSIGNMENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")  # F4: structured axis-command contract
_SHORT_OPT_RE = re.compile(r"^-[A-Za-z]+$")
_WRAPPER_FLAG_CHARS = {"sh": "c", "bash": "c", "zsh": "c", "dash": "c", "ksh": "c",  # -c runs a script
                        "python": "ce", "python3": "ce", "perl": "ce", "ruby": "ce"}  # -c/-e do too

def parse_axis_command(command: str) -> tuple[list[tuple[str, str]], list[str]] | None:
    """Peel leading NAME=VALUE / transparent ``env`` tokens; the rest is the real exec argv."""
    tokens = _tokenize(command)
    index = 0
    while index < len(tokens) and (_ENV_ASSIGNMENT_RE.match(tokens[index]) or Path(tokens[index]).name == "env"):
        index += 1
    env_assignments = [tuple(t.split("=", 1)) for t in tokens[:index] if "=" in t]
    exec_argv = tokens[index:]
    return (env_assignments, exec_argv) if exec_argv else None

def axis_binding_errors(axis: str, command: str) -> list[str]:
    """F4: structural validity of ``variation_axis`` against ``command``'s REAL executable argv; shared by write-time validation + checker re-derivation."""
    parsed = _axis_key_value(axis)
    if parsed is None:
        return ["variation_axis must be key=value with non-empty key and value"]
    key, value = parsed
    if not command_is_simple(command):
        return ["axis-bearing experiments require a simple command; register without an axis or split it"]
    binding = parse_axis_command(command)
    if binding is None:
        return ["variation_axis command has no executable argv"]
    argv = binding[1]
    flags = _WRAPPER_FLAG_CHARS.get(Path(argv[0]).name, "") if argv else ""
    if flags and any(_SHORT_OPT_RE.match(t) and set(t[1:]) & set(flags) for t in argv[1:] if not t.startswith("--")):
        return [f"variation_axis cannot bind through wrapper {argv[0]!r} (-c/-e consumes argv)"]
    if sum(1 for t in argv if t in {f"--{key}", f"-{key}"} or t.startswith((f"--{key}=", f"{key}="))) > 1:
        return [f"variation_axis key {key!r} appears more than once; the axis value must be unambiguous"]
    positions = _bound_value_positions(argv, key, value)
    if not positions:
        return [f"variation_axis value {value!r} must be bound to option {key!r} in the command"]
    if "--" in argv and all(p > argv.index("--") for p in positions):
        return [f"variation_axis value {value!r} is stranded after a bare '--' terminator"]
    return []

AXIS_EFFECTIVE_KEY = "axis_effective"
def axis_effective_mismatch(metrics: Any, declared_value: str) -> bool:
    """B4: True when ``metrics["axis_effective"]`` disagrees with the declared axis value."""
    return isinstance(metrics, dict) and AXIS_EFFECTIVE_KEY in metrics and str(metrics[AXIS_EFFECTIVE_KEY]) != str(declared_value)

def final_outcome(prereg: dict[str, Any], metrics: Any) -> str:
    """B4 parity: derive_outcome + the SAME axis_effective override, shared by runner + checker."""
    axis = _axis_key_value(prereg.get("variation_axis"))
    if axis is not None and axis_effective_mismatch(metrics, axis[1]):
        return "not-evaluable"
    return derive_outcome(prereg["disconfirm"], metrics)

def axis_binding(records: list[dict[str, Any]], evidence_ids: list[str]) -> dict[str, Any]:
    """F3: ONE shared axis derivation (n, labels, note, valid) for writer/checker/renderer, so
    n and labels never disagree; invalid/legacy axis -> n=1, "unverified configuration" (grandfathered)."""
    def _bad(note: str) -> dict[str, Any]:
        return {"n": 1, "labels": ["unverified configuration"], "note": note, "valid": False}

    pairs: list[tuple[str, str, str]] = []  # (axis key, axis value, registered command)
    for eid in evidence_ids:
        prereg, result = find_preregister(records, eid), find_result(records, eid)
        if prereg is None or result is None:
            continue
        axis, cmd = prereg.get("variation_axis"), prereg.get("command", "")
        parsed = _axis_key_value(axis)
        if parsed is None:
            continue
        if not command_is_simple(cmd):  # forged-ledger defense: no exception, n=1
            return _bad("n=1: axis on non-simple command")
        if axis_binding_errors(axis, cmd):  # F4: structural re-derivation, not just text-matching
            return _bad(f"n=1: {eid} variation_axis is not structurally bound to the command")
        if axis_effective_mismatch(result.get("metrics"), parsed[1]):
            return _bad(f"n=1: {eid} axis_effective does not match declared axis value")
        pairs.append((parsed[0], parsed[1], cmd))
    if not pairs:
        return {"n": 1, "labels": ["single configuration"], "note": "n=1: no conforming variation axis", "valid": False}
    keys = {k for k, _v, _c in pairs}
    if len(keys) > 1:
        return _bad(f"n=1: evidence mixes axis keys {sorted(keys)}")
    (key,) = keys
    if len({_templatize_command(c, key, v) for _k, v, c in pairs}) != 1:
        return _bad(f"n=1: axis {key!r} substitution leaves commands differing at a non-axis position")
    values = sorted({v for _k, v, _c in pairs}); n = len(values)
    labels = [f"{key}={v}" for v in values] if n > 1 else ["single configuration"]
    return {"n": n, "labels": labels, "valid": True,
            "note": f"n={n}: distinct values on axis key {key!r} over a common command template"}

def claim_n_and_note(records: list[dict[str, Any]], evidence_ids: list[str]) -> tuple[int, str]:
    binding = axis_binding(records, evidence_ids)
    return binding["n"], binding["note"]

def claim_n(records: list[dict[str, Any]], evidence_ids: list[str]) -> int: return axis_binding(records, evidence_ids)["n"]

def normalized_predicate(disconfirm: dict[str, Any]) -> tuple[Any, ...]:
    """S5: normalize a VALID disconfirm for identity comparison. F1: no float() cast — two large ints differing by 1 never collapse via rounding."""
    ptype, metric = predicate_type(disconfirm), disconfirm.get("metric")
    if ptype == PREDICATE_EQUIVALENCE:
        return (ptype, metric, disconfirm.get("lower"), disconfirm.get("upper"))
    return (ptype, metric, disconfirm.get("comparator"), disconfirm.get("threshold"))

def predicate_identity_errors(records: list[dict[str, Any]], evidence_ids: list[str]) -> list[str]:
    """S5: a claim's cited registrations must share ONE normalized predicate (invalid ones skip; see validate_predicate)."""
    baseline, baseline_eid = None, ""
    errors: list[str] = []
    for eid in evidence_ids:
        disconfirm = (find_preregister(records, eid) or {}).get("disconfirm")
        if disconfirm is None or validate_predicate(disconfirm):
            continue
        normalized = normalized_predicate(disconfirm)
        if baseline is None:
            baseline, baseline_eid = normalized, eid
        elif normalized != baseline:
            errors.append(f"{eid}: predicate does not match {baseline_eid}")
    return errors

def evaluate_claim_binding(
    records: list[dict[str, Any]], metric: str, evidence_ids: list[str]
) -> tuple[list[str], list[dict[str, str]]]:
    """Re-derive binding -> (errors, outcome_basis): metric/predicate match + real evidence (R1)."""
    errors, basis = [], []
    for eid in evidence_ids:
        prereg, result = find_preregister(records, eid), find_result(records, eid)
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
    return errors, basis

def derive_claim_category(records: list[dict[str, Any]], evidence_ids: list[str]) -> str:
    """B1/B5: category from cited-evidence outcomes + predicate shapes only, never asserted."""
    outcomes, types = [], set()
    for eid in evidence_ids:
        prereg, result = find_preregister(records, eid), find_result(records, eid)
        if prereg is None or result is None:
            continue
        outcomes.append(result.get("outcome"))
        types.add(predicate_type(prereg.get("disconfirm")))
    if not outcomes or len(types) != 1:
        return CATEGORY_MIXED
    if all(o == "supported" for o in outcomes):
        return CATEGORY_SUPPORTED if types == {PREDICATE_THRESHOLD} else CATEGORY_WITHIN_BOUNDS
    return CATEGORY_DISCONFIRMED if all(o == "disconfirmed" for o in outcomes) else CATEGORY_MIXED

def claims_view_path(repo_root: Path, ledger_path: Path) -> Path:
    """Canonical ledger → ``research/claims.md``; any other → adjacent ``claims.md``."""
    if ledger_path.resolve() == (repo_root / LEDGER_REL).resolve():
        return repo_root / "research" / "claims.md"
    return ledger_path.parent / "claims.md"

def render_claims(records: list[dict[str, Any]]) -> str:
    """Deterministic claims view; category + configuration identity (``axis_binding``, F3) are ALWAYS re-derived; sources are never rendered (F2)."""
    head = records[-1]["chain"]["hash"] if records else "none"
    lines = ["# Research claims", "", f"ledger-head: {head}", ""]
    claims = sorted((r for r in records if r.get("record_type") == CLAIM), key=lambda r: r["claim_id"])
    for claim in claims:
        metric, evidence = claim["metric"], claim["evidence"]
        category = derive_claim_category(records, evidence)
        binding = axis_binding(records, evidence)
        n = binding["n"]
        axis_key = binding["labels"][0].split("=", 1)[0] if n > 1 else None  # n>1 => labels are key=value
        # (S5) guarantees every non-mixed citation shares ONE predicate, so evidence[0] stands in as the representative fact.
        disconfirm = (find_preregister(records, evidence[0]) or {}).get("disconfirm") or {}
        tail = ("observed in a single configuration" if n == 1 else
                f"observed across {n} distinct {axis_key or 'variation-axis'} configurations")
        if category == CATEGORY_MIXED:
            sentence = f"{metric} evidence is mixed — {tail}."
        elif category == CATEGORY_DISCONFIRMED:
            scope = "in the configuration" if n == 1 else f"in all {n} configurations"
            fact = (f"fell outside [{disconfirm.get('lower')}, {disconfirm.get('upper')}]"
                    if predicate_type(disconfirm) == PREDICATE_EQUIVALENCE else
                    f"met the disconfirm predicate {disconfirm.get('comparator')} {disconfirm.get('threshold')}")
            sentence = f"{metric} {fact} {scope}."
        elif category == CATEGORY_SUPPORTED:
            sentence = (f"{metric} stayed on the non-disconfirming side of "
                        f"{disconfirm.get('comparator')} {disconfirm.get('threshold')} — {tail}.")
        else:
            sentence = f"{metric} remained within [{disconfirm.get('lower')}, {disconfirm.get('upper')}] — {tail}."
        lines += [f"## {claim['claim_id']}", sentence,
                  f"configurations: {', '.join(binding['labels'])}", f"evidence: {', '.join(evidence)}"]
        if claim.get("outcome_basis"):
            basis = ", ".join(f"{b['experiment_id']}={b['outcome']}" for b in claim["outcome_basis"])
            lines.append(f"outcome-basis: {basis}")
        if claim.get("n_basis"):
            lines.append(f"n-basis: {claim['n_basis']}")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"
