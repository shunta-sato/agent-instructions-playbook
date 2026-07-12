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
        for eid in record.get("evidence", []):
            prereg = rl.find_preregister(records, eid)
            result = rl.find_result(records, eid)
            if prereg is None or result is None:
                findings.append(f"claim-evidence-invalid: {cid}: {eid}")
            elif not (prereg["registered_at"] < result["started_at"]):
                findings.append(f"claim-evidence-harking: {cid}: {eid}")
        expected_n = rl.claim_n(records, record.get("evidence", []))
        if record.get("n") != expected_n:
            findings.append(f"claim-n-mismatch: {cid}: expected {expected_n}")


def _check_claims_view(records: list[dict[str, Any]], repo_root: Path, findings: list[str]) -> None:
    view = repo_root / "research" / "claims.md"
    if not view.is_file():
        return
    if view.read_text(encoding="utf-8") != rl.render_claims(records):
        findings.append("stale-claims-view: research/claims.md")


def check_ledger(records: list[dict[str, Any]], repo_root: Path) -> list[str]:
    findings: list[str] = []
    _check_chain(records, findings)
    _check_results(records, findings)
    _check_claims(records, findings)
    _check_claims_view(records, repo_root, findings)
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
    findings = check_ledger(records, repo_root)
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


def evaluate_diff(changed_paths: list[str], repo_root: Path, policy: dict[str, Any]) -> list[str]:
    path_modes = policy.get("path_modes", {}) or {}
    safety_paths = policy.get("safety_paths", []) or []
    modes = {path: resolve_mode(path, path_modes) for path in changed_paths}
    research_declared = any(mode == "research" for mode in modes.values())

    findings: list[str] = []
    for path in sorted(changed_paths):
        if research_declared and modes[path] == "delivery":
            findings.append(f"promotion-required: {path}")

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
    return findings


def changed_paths_from_range(repo_root: Path, diff_range: str) -> list[str]:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "diff", "--name-only", diff_range],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def run_diff_mode(diff_range: str, policy_path: Path, repo_root: Path) -> int:
    try:
        policy = load_policy(policy_path)
    except FileNotFoundError as exc:
        print(f"research-evidence: error: {exc}", file=sys.stderr)
        return 2
    changed_paths = changed_paths_from_range(repo_root, diff_range)
    findings = evaluate_diff(changed_paths, repo_root, policy)
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
        return run_diff_mode(args.diff_range, policy_path, repo_root)

    if args.check_ledger:
        ledger_path = Path(args.ledger).resolve() if args.ledger else (repo_root / rl.LEDGER_REL).resolve()
        return run_ledger_mode(ledger_path, repo_root)

    print("research-evidence: error: choose --check-ledger or --diff-range", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
