#!/usr/bin/env python3
"""Mechanical gate for the Research OS ledger — CLI entry points plus the
ledger-chain half. ``--check-ledger`` re-derives the whole research chain and
fails on any inconsistency (chain, missing preregistration, HARKing,
digest/outcome/n drift, invalid predicate, invalid claim evidence, stale view).
The boundary-gate half (``--diff-range A..B`` / ``--working-tree`` promotion,
symlink, safety, and acknowledgment-evidence evaluation) lives in
``research_gate`` and is dispatched from here; both halves were split so each
file stays within the structure budget. Tamper-EVIDENT, not tamper-PROOF.
FINDING lines + summary, exit 0/1/2. Stdlib only."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:  # direct execution: scripts/ is on sys.path[0]
    import research_ledger as rl
    import research_gate as rg
except ModuleNotFoundError:  # imported as scripts.check_research_evidence (tests, -m)
    from scripts import research_ledger as rl
    from scripts import research_gate as rg

# Re-export the boundary-gate API so existing callers/tests keep the ``cre.``
# names after the split (the CLI, the Makefile, and CI invoke the same flags).
evaluate_diff = rg.evaluate_diff
run_diff_mode = rg.run_diff_mode
run_working_tree_mode = rg.run_working_tree_mode
changed_paths_from_range = rg.changed_paths_from_range
changed_paths_from_working_tree = rg.changed_paths_from_working_tree

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
        findings.append(f"predicate-invalid: {record.get('experiment_id')}: {error}")
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

        # S3/F2/R2b binding, re-derived so a forged claim cannot assert an
        # inconsistent metric/direction/no-effect predicate. The direction rule
        # fires only for claims carrying the basis field (field-presence
        # grandfathering).
        enforce_direction = "direction_basis" in record
        binding_errors, derived_basis = rl.evaluate_claim_binding(
            records, record.get("metric"), record.get("direction"), evidence,
            enforce_direction=enforce_direction,
        )
        for error in binding_errors:
            findings.append(f"claim-binding: {cid}: {error}")

        # A record predating a basis field skips only that field's comparison.
        if "outcome_basis" in record and record.get("outcome_basis") != derived_basis:
            findings.append(f"claim-basis-mismatch: {cid}")

        expected_n, expected_n_basis = rl.claim_n_and_note(records, evidence)
        if record.get("n") != expected_n:
            findings.append(f"claim-n-mismatch: {cid}: expected {expected_n}")
        if "n_basis" in record and record.get("n_basis") != expected_n_basis:  # F3
            findings.append(f"claim-n-basis-mismatch: {cid}")

def _check_claims_view(
    records: list[dict[str, Any]],
    repo_root: Path,
    ledger_path: Path | None,
    findings: list[str],
) -> None:
    # Canonical → research/claims.md, else adjacent claims.md; check freshness only if present.
    view = rl.claims_view_path(repo_root, ledger_path) if ledger_path else repo_root / "research" / "claims.md"
    if view.is_file() and view.read_text(encoding="utf-8") != rl.render_claims(records):
        findings.append(f"stale-claims-view: {relative_display_path(view, repo_root)}")

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
        return rg._emit([f"ledger-parse: {exc}"], "")
    if not records:
        return rg._emit([], "no research records")
    return rg._emit(check_ledger(records, repo_root, ledger_path), f"{len(records)} research record(s) verified")

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mechanical gate for the Research OS ledger.")
    parser.add_argument("--repo-root", default="", help="Repository root override.")
    parser.add_argument("--ledger", default="", help="Ledger path override.")
    parser.add_argument("--check-ledger", action="store_true", help="Verify the research chain.")
    parser.add_argument("--diff-range", default="", help="Git range A..B for promotion checks.")
    parser.add_argument("--working-tree", action="store_true", help="F1: promotion checks over git status --porcelain.")
    parser.add_argument("--policy", default="", help="Bootstrap-fallback (diff-range) or checked-out (working-tree) policy.")
    parser.add_argument("--mode", choices=("research", "delivery"), default="", help="Declared session mode; omit for CI mixing checks.")
    return parser.parse_args(argv)

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parent.parent

    if args.diff_range and args.working_tree:
        return rg._usage("choose only one of --diff-range or --working-tree")

    if args.diff_range or args.working_tree:
        if not args.policy:
            return rg._usage("--diff-range/--working-tree requires --policy")
        policy_path = Path(args.policy)
        if not policy_path.is_absolute():
            policy_path = repo_root / policy_path
        if args.working_tree:
            return rg.run_working_tree_mode(policy_path, repo_root, args.mode or None)
        return rg.run_diff_mode(args.diff_range, policy_path, repo_root, args.mode or None)

    if args.check_ledger:
        ledger_path = Path(args.ledger).resolve() if args.ledger else (repo_root / rl.LEDGER_REL).resolve()
        return run_ledger_mode(ledger_path, repo_root)

    return rg._usage("choose --check-ledger, --diff-range, or --working-tree")

if __name__ == "__main__":
    raise SystemExit(main())
