#!/usr/bin/env python3
"""Shared primitives for the Research OS ledger.

Research records share the JSONL substrate with ``agent_run`` records; they
interleave freely and form a hash chain over their own subsequence. This is
the single source of truth every value the producer (``research_run.py``) and
the gate (``check_research_evidence``) must agree on — hashing, chain linkage,
command digests, predicate/outcome evaluation, claim binding, claim ``n``, and
the claims view — so the validator re-derives exactly what the runner wrote.

Threat model: the chain is tamper-EVIDENT for honest-but-buggy flows and
accidental corruption, NOT tamper-PROOF (an agent with write access to both
scripts and ledger can forge a self-consistent chain; adversarial anchoring is
a follow-up). Only Python stdlib is used.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import subprocess
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
LEDGER_REL = ".agents/runs/agent-runs.jsonl"
# Runner-generated artifacts (see research_run.make_run_dir). Disposable; the
# ledger is the record. Never an experiment input to command_digest.
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
    """Runner-stamped UTC timestamp (never caller-supplied); microsecond
    resolution keeps ``started_at`` strictly after ``registered_at`` even
    when register and execute land in the same second."""
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


def find_preregister(records: list[dict[str, Any]], experiment_id: str) -> dict[str, Any] | None:
    for record in records:
        if record.get("record_type") == PREREGISTER and record.get("experiment_id") == experiment_id:
            return record
    return None


def find_result(records: list[dict[str, Any]], experiment_id: str) -> dict[str, Any] | None:
    for record in records:
        if record.get("record_type") == RESULT and record.get("experiment_id") == experiment_id:
            return record
    return None


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validate_predicate(disconfirm: Any) -> list[str]:
    """Return a list of well-formedness errors for a disconfirm predicate."""
    errors: list[str] = []
    if not isinstance(disconfirm, dict):
        return ["disconfirm must be an object"]
    if not isinstance(disconfirm.get("metric"), str) or not disconfirm.get("metric"):
        errors.append("disconfirm.metric must be a non-empty string")
    if disconfirm.get("comparator") not in COMPARATORS:
        errors.append(f"disconfirm.comparator must be one of {list(COMPARATORS)}")
    if not _is_number(disconfirm.get("threshold")):
        errors.append("disconfirm.threshold must be a number")
    return errors


def apply_comparator(comparator: str, lhs: Any, rhs: Any) -> bool:
    if comparator == "<":
        return lhs < rhs
    if comparator == "<=":
        return lhs <= rhs
    if comparator == ">":
        return lhs > rhs
    if comparator == ">=":
        return lhs >= rhs
    if comparator == "==":
        return lhs == rhs
    raise LedgerError(f"unknown comparator: {comparator}")


def derive_outcome(disconfirm: dict[str, Any], metrics: Any) -> str:
    """Evaluate the disconfirm predicate: TRUE means disconfirmed.
    ``not-evaluable`` when the metric is missing/non-object; the value is a
    non-finite number (NaN/±Inf) under ANY comparator including ``==`` (junk
    is never evidence); or the value is non-numeric under an ordered
    comparator (``==`` still compares equality safely).
    """
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
    return sum(
        1
        for record in prior_records
        if record.get("record_type") in (EXPLORATION, RESULT)
        and record.get("command_digest") == digest
    )


def _axis_key_value(axis: Any) -> tuple[str, str] | None:
    """Parse ``variation_axis`` into ``(key, value)`` (split on first ``=``,
    both parts non-empty); absent/non-conforming axes return ``None``."""
    if not isinstance(axis, str) or "=" not in axis:
        return None
    key, value = axis.split("=", 1)
    if not key or not value:
        return None
    return key, value


def claim_n_and_note(records: list[dict[str, Any]], evidence_ids: list[str]) -> tuple[int, str]:
    """Conservative experimental multiplicity plus its derivation note. ``n``
    counts distinct axis VALUES among evidence sharing one axis KEY, with
    pairwise-distinct result digests (a same-digest replay is ignored). Mixed
    axis keys collapse to n=1 with a note; absent/non-conforming axes
    contribute nothing, so evidence with no conforming axis is n=1.
    """
    keys_seen: set[str] = set()
    seen_digests: set[Any] = set()
    values: set[str] = set()
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
        digest = result.get("command_digest")
        if digest in seen_digests:
            continue
        seen_digests.add(digest)
        values.add(value)
    if not keys_seen:
        return 1, "n=1: no conforming variation axis"
    if len(keys_seen) > 1:
        return 1, f"n=1: evidence mixes axis keys {sorted(keys_seen)}"
    (key,) = tuple(keys_seen)
    return len(values), f"n={len(values)}: distinct values on axis key {key!r}"


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
    """Re-derive a claim's binding to its evidence, returning ``(errors,
    outcome_basis)``. The basis (per-evidence ``[{experiment_id, outcome}]``)
    is stored on the claim so the gate re-derives without trusting the runner:
    (a) claim metric == every cited prereg's metric; (b) every cited result is
    real evidence (exit 0, supported/disconfirmed); (c) direction agrees —
    ``no-effect`` all disconfirmed, ``mixed`` any mixture, ``improves``/
    ``degrades`` all ``supported`` AND (when ``enforce_direction``, F2) every
    registration's preregistered ``direction_if_supported`` == the claim
    direction, so grandfathered evidence (field absent) backs only
    ``no-effect``/``mixed``. The gate disables ``enforce_direction`` only for
    claims predating the F2 basis field (field-presence grandfathering).
    """
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
        elif direction == "no-effect" and not all(o == "disconfirmed" for o in outcomes):
            errors.append("direction no-effect requires all evidence outcomes disconfirmed")
    return errors, basis


def _git(repo_root: Path, args: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return completed.stdout


def git_head(repo_root: Path) -> str:
    out = _git(repo_root, ["rev-parse", "HEAD"])
    return out.strip() if out else "no-git"


def _excluded_from_digest(rel_path: str, ledger_rel: str | None) -> bool:
    """Whether a dirty path must be kept out of ``command_digest``: the
    recording process's own outputs (not experiment inputs) — the ledger
    being written, the default ``LEDGER_REL`` (``register`` appends to it, so
    including it would make ``execute`` hash a different ledger and reject
    every first pair), and runner artifacts under ``RUNNER_OUTPUT_REL``."""
    if rel_path == LEDGER_REL or rel_path == ledger_rel:
        return True
    return rel_path == RUNNER_OUTPUT_REL or rel_path.startswith(RUNNER_OUTPUT_REL + "/")


def dirty_input_files(repo_root: Path, ledger_path: Path | None = None) -> list[dict[str, str]]:
    """Dirty files that count as ``command_digest`` inputs: tracked files
    modified vs ``HEAD`` AND untracked, non-ignored files. The untracked set
    is load-bearing — a disposable probe run WITHOUT ``git add`` is the normal
    case and would otherwise be editable between register and execute
    undetected. See ``_excluded_from_digest``."""
    tracked = _git(repo_root, ["diff", "--name-only", "HEAD", "--"]) or ""
    untracked = _git(repo_root, ["ls-files", "--others", "--exclude-standard"]) or ""
    ledger_rel: str | None = None
    if ledger_path is not None:
        try:
            ledger_rel = ledger_path.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            ledger_rel = None
    names = {line.strip() for line in tracked.splitlines() if line.strip()}
    names |= {line.strip() for line in untracked.splitlines() if line.strip()}
    entries: list[dict[str, str]] = []
    for name in sorted(names):
        if _excluded_from_digest(name, ledger_rel):
            continue
        path = repo_root / name
        if path.is_file():
            entries.append({"path": name, "sha256": sha256_file(path)})
    return entries


def claims_view_path(repo_root: Path, ledger_path: Path) -> Path:
    """The claims view for ``ledger_path``: the canonical ledger maps to
    ``research/claims.md``; any other ledger carries an adjacent ``claims.md``."""
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
        tail = f"{claim['effect']} ({claim['metric']} {claim['direction']})"
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
