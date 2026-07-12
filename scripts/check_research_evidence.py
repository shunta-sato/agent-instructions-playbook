#!/usr/bin/env python3
"""Mechanical gate for the Research OS ledger.

Two modes:

``--check-ledger`` (CI-safe): re-derives the entire research chain and
fails on any inconsistency — broken hash links, results without a matching
preregistration, HARKing (registered_at not before started_at), digest
drift, malformed predicates, outcomes that do not re-derive, invalid or
miscounted claim evidence, multiplicity drift, or a stale claims view.
Empty/absent research records pass.

``--diff-range A..B --policy <file>`` (R5): promotion, symlink-boundary,
and safety-review findings over a changed-path set, with a default-deny
(unmatched = delivery) path model.

The boundary gate binds to a DECLARED mode, not to what the diff happens to
touch. ``--mode research`` means "this session declared research work": any
delivery-path change then needs promotion. ``--mode delivery`` means "this
session declared delivery work": editing a research-only path is legitimate
(delivery gates are stricter, and claims discipline is mode-independent), so
it emits only a non-blocking ``NOTE mode:`` line and never changes the exit
code. When ``--mode`` is omitted — the CI case, where per-session
declarations are not knowable — the gate falls back to a mixing rule: a
single diff that touches BOTH research-mode and delivery-mode paths requires
promotion. Safety-path review is evaluated in every case.

Promotion acknowledgment: when the diff both produces ``promotion-required``
findings and adds/modifies an acknowledgment file under ``.agents/promotions/``
(any ``*.md`` except ``README.md``), every ``promotion-required`` finding is
downgraded to a non-blocking ``NOTE promotion acknowledged:`` line and the gate
exits 0 — that file is the committed, reviewable record of the research→delivery
crossing (research-synthesis's promote contract). ``safety-review-required`` is
never downgraded. Residual risk, documented not hidden: a CI diff touching only
delivery paths, or only research paths, cannot be distinguished from a
correctly-declared session, so CI catches mixing but not a mis-declared
single-mode session; the session-side ``--mode`` binding closes that gap.

Threat model (scope, stated plainly). ``--check-ledger`` is
tamper-EVIDENT for honest-but-buggy flows and accidental corruption — it
catches mutated records, broken chain links, un-re-derivable outcomes,
stale claims views, and forged/inconsistent claim records. It is NOT
tamper-PROOF: an agent with write access to both the scripts and the ledger
can forge a fully self-consistent chain that this gate accepts.
Adversarial-grade anchoring (an externally published chain head, or a
protected append-only writer outside the deriving party's control) is a
documented follow-up, not a property this gate currently provides.

Output follows ``check_structure.py`` / ``check_api_removal.py``: FINDING
lines, a summary line, exit codes 0 (clean) / 1 (findings) / 2 (usage).
Only Python stdlib is used.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

try:  # direct execution: scripts/ is on sys.path[0]
    import research_ledger as rl
except ModuleNotFoundError:  # imported as scripts.check_research_evidence (tests, -m)
    from scripts import research_ledger as rl


# --- ledger mode -------------------------------------------------------------


def _check_chain(records: list[dict[str, Any]], findings: list[str]) -> None:
    for index, record in enumerate(records):
        chain = record.get("chain")
        rid = record.get("experiment_id") or record.get("exploration_id") or record.get("claim_id") or f"#{index}"
        if not isinstance(chain, dict):
            findings.append(f"chain-missing: {rid}")
            continue
        expected_prev = None if index == 0 else records[index - 1]["chain"].get("hash")
        if chain.get("prev") != expected_prev:
            findings.append(f"chain-prev-mismatch: {rid}")
        if chain.get("hash") != rl.compute_hash(record):
            findings.append(f"chain-hash-mismatch: {rid}")


def _check_predicate(record: dict[str, Any], findings: list[str]) -> list[str]:
    errors = rl.validate_predicate(record.get("disconfirm"))
    for error in errors:
        findings.append(f"malformed-predicate: {record.get('experiment_id')}: {error}")
    return errors


def _check_results(records: list[dict[str, Any]], findings: list[str]) -> None:
    for record in records:
        if record.get("record_type") == rl.PREREGISTER:
            _check_predicate(record, findings)

    for index, record in enumerate(records):
        if record.get("record_type") != rl.RESULT:
            continue
        eid = record.get("experiment_id")
        prereg = rl.find_preregister(records, eid)
        if prereg is None:
            findings.append(f"missing-preregistration: {eid}")
        else:
            if not (prereg["registered_at"] < record["started_at"]):
                findings.append(f"harking: {eid}: registered_at not before started_at")
            if prereg["command_digest"] != record["command_digest"]:
                findings.append(f"digest-mismatch: {eid}")
            if not _check_predicate(prereg, findings):
                expected = rl.derive_outcome(prereg["disconfirm"], record.get("metrics"))
                if expected != record.get("outcome"):
                    findings.append(f"outcome-mismatch: {eid}: expected {expected}")

        prior = records[:index]
        expected_mult = rl.multiplicity(prior, record["command_digest"])
        if record.get("exploration_multiplicity") != expected_mult:
            findings.append(f"multiplicity-mismatch: {eid}: expected {expected_mult}")
        if record.get("derived_from_exploration") != (expected_mult > 0):
            findings.append(f"derived-flag-mismatch: {eid}")


def _check_claims(records: list[dict[str, Any]], findings: list[str]) -> None:
    for record in records:
        if record.get("record_type") != rl.CLAIM:
            continue
        cid = record.get("claim_id")
        evidence = record.get("evidence", [])
        for eid in evidence:
            prereg = rl.find_preregister(records, eid)
            result = rl.find_result(records, eid)
            if prereg is None or result is None:
                findings.append(f"claim-evidence-invalid: {cid}: {eid}")
            elif not (prereg["registered_at"] < result["started_at"]):
                findings.append(f"claim-evidence-harking: {cid}: {eid}")

        # Semantic binding (S3), re-derived from the ledger so a hand-forged
        # claim record cannot assert an inconsistent metric/direction pairing.
        binding_errors, derived_basis = rl.evaluate_claim_binding(
            records, record.get("metric"), record.get("direction"), evidence
        )
        for error in binding_errors:
            findings.append(f"claim-binding: {cid}: {error}")

        # Grandfathering: records written before outcome_basis existed
        # (schema field absent) skip the basis comparison but still face every
        # re-derived check above and the n check below. New records carry the
        # basis and must match what the ledger re-derives.
        if "outcome_basis" in record and record.get("outcome_basis") != derived_basis:
            findings.append(f"claim-basis-mismatch: {cid}")

        expected_n = rl.claim_n(records, evidence)
        if record.get("n") != expected_n:
            findings.append(f"claim-n-mismatch: {cid}: expected {expected_n}")


def _check_claims_view(
    records: list[dict[str, Any]],
    repo_root: Path,
    ledger_path: Path | None,
    findings: list[str],
) -> None:
    # The view belongs to the ledger being checked: research/claims.md for the
    # canonical ledger, an adjacent claims.md for any other --ledger. When no
    # ledger_path is supplied (legacy callers/tests), fall back to the
    # canonical view. Freshness is only asserted if the view file exists.
    if ledger_path is None:
        view = repo_root / "research" / "claims.md"
    else:
        view = rl.claims_view_path(repo_root, ledger_path)
    if not view.is_file():
        return
    if view.read_text(encoding="utf-8") != rl.render_claims(records):
        rel = relative_display_path(view, repo_root)
        findings.append(f"stale-claims-view: {rel}")


def relative_display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def check_ledger(
    records: list[dict[str, Any]], repo_root: Path, ledger_path: Path | None = None
) -> list[str]:
    findings: list[str] = []
    _check_chain(records, findings)
    _check_results(records, findings)
    _check_claims(records, findings)
    _check_claims_view(records, repo_root, ledger_path, findings)
    return findings


def run_ledger_mode(ledger_path: Path, repo_root: Path) -> int:
    try:
        records = rl.load_research_records(ledger_path)
    except rl.LedgerError as exc:
        print(f"FINDING ledger-parse: {exc}")
        print("research-evidence: 1 finding(s)")
        return 1
    if not records:
        print("research-evidence: pass (no research records)")
        return 0
    findings = check_ledger(records, repo_root, ledger_path)
    if findings:
        for finding in findings:
            print(f"FINDING {finding}")
        print(f"research-evidence: {len(findings)} finding(s)")
        return 1
    print(f"research-evidence: pass ({len(records)} research record(s) verified)")
    return 0


# --- diff mode ---------------------------------------------------------------


def load_policy(policy_path: Path) -> dict[str, Any]:
    if not policy_path.is_file():
        raise FileNotFoundError(f"policy file is missing: {policy_path}")
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("policy top-level value must be an object")
    return payload


def resolve_mode(path: str, path_modes: dict[str, str]) -> str:
    """Longest-prefix match; unmatched paths default to delivery (default-deny)."""
    best_prefix = ""
    best_mode = "delivery"
    for prefix, mode in path_modes.items():
        if path == prefix or path.startswith(prefix):
            if len(prefix) >= len(best_prefix):
                best_prefix = prefix
                best_mode = mode
    return best_mode


def _matches_safety(path: str, safety_paths: list[str]) -> bool:
    return any(path == prefix or path.startswith(prefix) for prefix in safety_paths)


PROMOTIONS_DIR = ".agents/promotions/"


def _is_acknowledgment(path: str) -> bool:
    """A committed promotion-acknowledgment record: any ``*.md`` under
    ``.agents/promotions/`` other than the directory's ``README.md``."""
    return (
        path.startswith(PROMOTIONS_DIR)
        and path.endswith(".md")
        and Path(path).name != "README.md"
    )


def evaluate_diff(
    changed_paths: list[str],
    repo_root: Path,
    policy: dict[str, Any],
    mode: str | None = None,
) -> tuple[list[str], list[str]]:
    """Boundary findings and notes for a changed-path set under a ``mode``.

    Returns ``(findings, notes)``. Findings are blocking (exit 1); notes are
    non-blocking (exit 0). ``mode`` binds the gate to what the session
    declared rather than to what the diff infers:

    * ``"research"``: any delivery-path change → ``promotion-required``.
    * ``"delivery"``: a change under a research-only path is legitimate and
      emits a non-blocking ``mode`` note (claims discipline still applies).
    * ``None`` (CI, declarations unknowable): the mixing rule — promotion is
      required only when the diff touches BOTH research and delivery paths.

    Promotion acknowledgment: if the diff carries an acknowledgment file (see
    ``_is_acknowledgment``), every ``promotion-required`` finding is emitted
    as a ``promotion acknowledged`` note instead. ``safety-review-required``
    is never downgraded. Symlink-boundary and safety findings are evaluated in
    every case.
    """
    path_modes = policy.get("path_modes", {}) or {}
    safety_paths = policy.get("safety_paths", []) or []
    modes = {path: resolve_mode(path, path_modes) for path in changed_paths}
    has_research = any(m == "research" for m in modes.values())
    has_delivery = any(m == "delivery" for m in modes.values())

    if mode == "research":
        promote_delivery = True
    elif mode == "delivery":
        promote_delivery = False
    else:  # CI: no session declaration — flag only genuine mixing.
        promote_delivery = has_research and has_delivery

    ack_files = sorted(path for path in changed_paths if _is_acknowledgment(path))

    findings: list[str] = []
    notes: list[str] = []
    for path in sorted(changed_paths):
        if promote_delivery and modes[path] == "delivery":
            if ack_files:
                notes.append(f"promotion acknowledged: {ack_files[0]} covers {path}")
            else:
                findings.append(f"promotion-required: {path}")
        if mode == "delivery" and modes[path] == "research":
            notes.append(
                f"mode: delivery-mode change under research path {path}"
                " — claims discipline still applies"
            )

        absolute = repo_root / path
        if absolute.is_symlink():
            target = os.path.realpath(absolute)
            try:
                target_rel = Path(target).resolve().relative_to(repo_root.resolve()).as_posix()
                target_mode = resolve_mode(target_rel, path_modes)
            except ValueError:
                target_mode = "delivery"
            if modes[path] == "research" or target_mode != modes[path]:
                findings.append(f"symlink-boundary: {path}")

        if _matches_safety(path, safety_paths):
            findings.append(f"safety-review-required: {path}")
    return findings, notes


def changed_paths_from_range(repo_root: Path, diff_range: str) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--name-only", diff_range],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def run_diff_mode(
    diff_range: str, policy_path: Path, repo_root: Path, mode: str | None = None
) -> int:
    try:
        policy = load_policy(policy_path)
    except FileNotFoundError as exc:
        print(f"research-evidence: error: {exc}", file=sys.stderr)
        return 2
    changed_paths = changed_paths_from_range(repo_root, diff_range)
    findings, notes = evaluate_diff(changed_paths, repo_root, policy, mode)
    for note in notes:
        print(f"NOTE {note}")
    if findings:
        for finding in findings:
            print(f"FINDING {finding}")
        print(f"research-evidence: {len(findings)} finding(s)")
        return 1
    print(f"research-evidence: pass ({len(changed_paths)} changed path(s))")
    return 0


# --- CLI ---------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mechanical gate for the Research OS ledger.")
    parser.add_argument("--repo-root", default="", help="Repository root override.")
    parser.add_argument("--ledger", default="", help="Ledger path override.")
    parser.add_argument("--check-ledger", action="store_true", help="Verify the research chain.")
    parser.add_argument("--diff-range", default="", help="Git range A..B for promotion checks.")
    parser.add_argument("--policy", default="", help="Policy file for diff-range mode.")
    parser.add_argument(
        "--mode",
        choices=("research", "delivery"),
        default="",
        help="Declared session mode for diff-range binding; omit for CI mixing checks.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parent.parent

    if args.diff_range:
        if not args.policy:
            print("research-evidence: error: --diff-range requires --policy", file=sys.stderr)
            return 2
        policy_path = Path(args.policy)
        if not policy_path.is_absolute():
            policy_path = repo_root / policy_path
        return run_diff_mode(args.diff_range, policy_path, repo_root, args.mode or None)

    if args.check_ledger:
        ledger_path = Path(args.ledger).resolve() if args.ledger else (repo_root / rl.LEDGER_REL).resolve()
        return run_ledger_mode(ledger_path, repo_root)

    print("research-evidence: error: choose --check-ledger or --diff-range", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
