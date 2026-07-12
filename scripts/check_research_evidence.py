#!/usr/bin/env python3
"""Mechanical gate for the Research OS ledger. ``--check-ledger`` re-derives
the whole research chain and fails on any inconsistency (chain, missing
preregistration, HARKing, digest/outcome/n drift, invalid predicate, invalid
claim evidence, stale view). ``--diff-range A..B`` / ``--working-tree`` (F1)
with ``--policy`` emit promotion, symlink-boundary, and safety findings over a
changed-path set (default-deny: unmatched = delivery) under a declared
``--mode``; base-policy binding (F6) and evidence-bound acknowledgment
downgrade (F7/R4) live in ``run_diff_mode`` / ``evaluate_diff`` /
``_parse_acknowledgment``. Tamper-EVIDENT, not tamper-PROOF. FINDING lines +
summary, exit 0/1/2. Stdlib only."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:  # direct execution: scripts/ is on sys.path[0]
    import research_ledger as rl
except ModuleNotFoundError:  # imported as scripts.check_research_evidence (tests, -m)
    from scripts import research_ledger as rl

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

        # S3/F2/R2a binding, re-derived so a forged claim cannot assert an
        # inconsistent metric/direction/effect. The direction and effect rules
        # fire only for claims carrying the basis field (field-presence grandfathering).
        enforce_direction = "direction_basis" in record
        binding_errors, derived_basis = rl.evaluate_claim_binding(
            records, record.get("metric"), record.get("direction"), evidence,
            enforce_direction=enforce_direction,
        )
        for error in binding_errors:
            findings.append(f"claim-binding: {cid}: {error}")
        if "effect_basis" in record:  # R2a: re-derive the inherited effect
            eff_err, eff, _ = rl.derive_effect(records, evidence)
            if eff_err or record.get("effect") != eff:
                findings.append(f"claim-effect-mismatch: {cid}")

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

def _emit(findings: list[str], pass_detail: str) -> int:
    """Print FINDING lines + summary; exit 1 on findings, 0 (``pass``) clean."""
    for finding in findings:
        print(f"FINDING {finding}")
    if findings:
        print(f"research-evidence: {len(findings)} finding(s)")
        return 1
    print(f"research-evidence: pass ({pass_detail})")
    return 0

def _usage(msg: str) -> int:
    print(f"research-evidence: error: {msg}", file=sys.stderr)
    return 2

def run_ledger_mode(ledger_path: Path, repo_root: Path) -> int:
    try:
        records = rl.load_research_records(ledger_path)
    except rl.LedgerError as exc:
        return _emit([f"ledger-parse: {exc}"], "")
    if not records:
        return _emit([], "no research records")
    return _emit(check_ledger(records, repo_root, ledger_path), f"{len(records)} research record(s) verified")

POLICY_REL = ".agents/project-policy.yml"

def _parse_policy(text: str) -> dict[str, Any]:
    payload = json.loads(text)
    if not isinstance(payload, dict):
        raise ValueError("policy top-level value must be an object")
    return payload

def load_policy(policy_path: Path) -> dict[str, Any]:
    if not policy_path.is_file():
        raise FileNotFoundError(f"policy file is missing: {policy_path}")
    return _parse_policy(policy_path.read_text(encoding="utf-8"))

def base_ref_of_range(diff_range: str) -> str:
    """Left ref of ``A..B``/``A...B`` with trailing dots stripped (F6 base)."""
    return diff_range.split("..", 1)[0].rstrip(".")

def load_base_policy(repo_root: Path, base_ref: str) -> dict[str, Any] | None:
    """The policy committed at ``base_ref``; ``None`` when absent there."""
    completed = subprocess.run(["git", "-C", str(repo_root), "show", f"{base_ref}:{POLICY_REL}"], capture_output=True, text=True)
    return _parse_policy(completed.stdout) if completed.returncode == 0 else None

def resolve_mode(path: str, path_modes: dict[str, str]) -> str:
    """Longest-prefix match; unmatched paths default to delivery (default-deny)."""
    best_prefix, best_mode = "", "delivery"
    for prefix, mode in path_modes.items():
        if (path == prefix or path.startswith(prefix)) and len(prefix) >= len(best_prefix):
            best_prefix, best_mode = prefix, mode
    return best_mode

PROMOTIONS_DIR = ".agents/promotions/"  # an acknowledgment is any *.md here except README.md

def _parse_acknowledgment(text: str) -> tuple[list[str], list[str], list[str], list[str]]:
    """Structural parse → ``(covers, run_ids, claim_ids, missing)`` (F7/R4).
    Requires a ``Scope:`` line, a ``C-<n>`` ref OR ``no research claims
    promoted``, a ``Covers:`` section of ``- `` prefixes, and >=1
    ``Delivery-run:`` run_id. Any structural gap → empty covers/run_ids
    (downgrades nothing) plus the names of what is absent."""
    lines = text.splitlines()
    has_scope = any(ln.strip().lower().startswith("scope:") for ln in lines)
    claim_ids = re.findall(r"C-\d+", text)
    has_claim = bool(claim_ids) or "no research claims promoted" in text.lower()
    covers: list[str] = []
    run_ids: list[str] = []
    in_covers = False
    for ln in lines:
        stripped = ln.strip()
        low = stripped.lower()
        if low.startswith("delivery-run:"):  # R4: cited agent_run evidence
            run_ids += [t for t in re.split(r"[\s,]+", stripped.split(":", 1)[1]) if t]
            in_covers = False
        elif low.startswith("covers:"):
            in_covers = True
        elif in_covers and stripped.startswith("- ") and stripped[2:].strip():
            covers.append(stripped[2:].strip())
        elif in_covers and stripped:
            in_covers = False  # a non-blank, non-list line closes the Covers section
    missing = [label for ok, label in (
        (has_scope, "Scope:"),
        (has_claim, "claim ref or 'no research claims promoted'"),
        (bool(covers), "Covers: prefixes"),
        (bool(run_ids), "Delivery-run: run_ids"),
    ) if not ok]
    return (covers, run_ids, sorted(set(claim_ids)), []) if not missing else ([], [], [], missing)

def _valid_canonical_claim_ids(repo_root: Path) -> set[str]:
    """Claim IDs in the canonical ledger that pass re-derivation (R4.1)."""
    ledger = repo_root / rl.LEDGER_REL
    records = rl.load_research_records(ledger)
    if not records:
        return set()
    findings = check_ledger(records, repo_root, ledger)
    ids = {r["claim_id"] for r in records if r.get("record_type") == rl.CLAIM and r.get("claim_id")}
    return {cid for cid in ids if not any(cid in f for f in findings)}

def evaluate_diff(changed_paths: list[str], repo_root: Path, policy: dict[str, Any], mode: str | None = None) -> tuple[list[str], list[str]]:
    """Boundary findings (blocking) and notes (non-blocking) for a changed-path
    set under ``mode`` (see the module docstring). A ``promotion-required`` path
    downgrades to a note only under a VALID acknowledgment that both Covers it
    and cites run evidence whose files span it (F7/R4); safety and symlink-
    boundary findings are evaluated in every case."""
    path_modes = policy.get("path_modes", {}) or {}
    safety_paths = policy.get("safety_paths", []) or []
    modes = {path: resolve_mode(path, path_modes) for path in changed_paths}

    if mode == "research":
        promote_delivery = True
    elif mode == "delivery":
        promote_delivery = False
    else:  # CI: no session declaration — flag only genuine mixing.
        promote_delivery = "research" in modes.values() and "delivery" in modes.values()

    findings: list[str] = []
    notes: list[str] = []
    # F7/R4: a downgrade needs a structurally-valid ack whose cited claims and
    # Delivery-runs resolve to real, green ledger evidence; a path downgrades
    # only when BOTH under a Covers prefix AND spanned by the cited runs' files.
    acks = [p for p in changed_paths if p.startswith(PROMOTIONS_DIR) and p.endswith(".md") and Path(p).name != "README.md"]
    agent_runs = rl.load_agent_runs(repo_root) if acks else {}
    valid_claims = _valid_canonical_claim_ids(repo_root) if acks else set()
    valid_acks: list[tuple[str, list[str], set[str]]] = []  # (ack, covers, run-file union)
    for ack in sorted(acks):
        ack_abs = repo_root / ack
        text = ack_abs.read_text(encoding="utf-8") if ack_abs.is_file() else ""
        covers, run_ids, claim_ids, missing = _parse_acknowledgment(text)
        reasons = missing or rl.ack_evidence_gaps(claim_ids, run_ids, valid_claims, agent_runs)
        if reasons:
            notes.append(f"invalid-acknowledgment: {ack} ({', '.join(reasons)})")
            continue
        union: set[str] = set()
        for rid in run_ids:
            run = agent_runs[rid]
            union |= set(run.get("changed_files", [])) | set(run.get("allowed_files", []))
        valid_acks.append((ack, covers, union))

    for path in sorted(changed_paths):
        if promote_delivery and modes[path] == "delivery":
            cover = next(
                (a for a, covers, union in valid_acks
                 if any(path.startswith(p) for p in covers) and rl.union_covers(path, union)),
                None,
            )
            if cover:
                notes.append(f"promotion acknowledged: {cover} covers {path}")
            else:
                findings.append(f"promotion-required: {path}")
        if mode == "delivery" and modes[path] == "research":
            notes.append(f"mode: delivery-mode change under research path {path} — claims discipline still applies")

        absolute = repo_root / path
        if absolute.is_symlink():
            try:
                target_rel = Path(os.path.realpath(absolute)).resolve().relative_to(repo_root.resolve()).as_posix()
                target_mode = resolve_mode(target_rel, path_modes)
            except ValueError:
                target_mode = "delivery"
            if modes[path] == "research" or target_mode != modes[path]:
                findings.append(f"symlink-boundary: {path}")

        if any(path == prefix or path.startswith(prefix) for prefix in safety_paths):
            findings.append(f"safety-review-required: {path}")
    return findings, notes

def _git_output(repo_root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo_root), *args], check=True, capture_output=True, text=True
    ).stdout

def changed_paths_from_range(repo_root: Path, diff_range: str) -> list[str]:
    out = _git_output(repo_root, "diff", "--name-only", diff_range)
    return [line.strip() for line in out.splitlines() if line.strip()]

def changed_paths_from_working_tree(repo_root: Path) -> list[str]:
    """F1: staged + unstaged + untracked paths (git excludes ignored by default),
    so a skill can invoke the gate with a declared mode before committing."""
    paths: list[str] = []
    for line in _git_output(repo_root, "status", "--porcelain").splitlines():
        if not line.strip():
            continue
        entry = line[3:]  # strip the "XY " status prefix
        if " -> " in entry:  # rename/copy: report the resulting path
            entry = entry.split(" -> ", 1)[1]
        paths.append(entry.strip())
    return paths

def _finish(changed_paths: list[str], repo_root: Path, policy: dict[str, Any], mode: str | None, pre_notes: list[str]) -> int:
    findings, notes = evaluate_diff(changed_paths, repo_root, policy, mode)
    for note in pre_notes + notes:
        print(f"NOTE {note}")
    return _emit(findings, f"{len(changed_paths)} changed path(s)")

def run_diff_mode(diff_range: str, policy_path: Path, repo_root: Path, mode: str | None = None) -> int:
    # F6: judge under the BASE policy so a head-side edit cannot weaken its own gate.
    changed_paths = changed_paths_from_range(repo_root, diff_range)
    pre_notes: list[str] = []
    try:
        policy = load_base_policy(repo_root, base_ref_of_range(diff_range))
    except (ValueError, json.JSONDecodeError) as exc:
        return _usage(str(exc))
    if policy is None:
        try:
            policy = load_policy(policy_path)
        except FileNotFoundError as exc:
            return _usage(str(exc))
        pre_notes.append("policy-bootstrap: no policy at base; evaluating with head policy")
    elif POLICY_REL in changed_paths:
        pre_notes.append("policy-change: evaluated with base policy; head policy takes effect after merge")
    return _finish(changed_paths, repo_root, policy, mode, pre_notes)

def run_working_tree_mode(policy_path: Path, repo_root: Path, mode: str | None = None) -> int:
    """F1: same findings/notes/ack logic as diff mode, but over the working
    tree and the checked-out policy (base-ref binding does not apply here)."""
    try:
        policy = load_policy(policy_path)
    except FileNotFoundError as exc:
        return _usage(str(exc))
    changed_paths = changed_paths_from_working_tree(repo_root)
    return _finish(changed_paths, repo_root, policy, mode, ["policy-source: working tree"])

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
        return _usage("choose only one of --diff-range or --working-tree")

    if args.diff_range or args.working_tree:
        if not args.policy:
            return _usage("--diff-range/--working-tree requires --policy")
        policy_path = Path(args.policy)
        if not policy_path.is_absolute():
            policy_path = repo_root / policy_path
        if args.working_tree:
            return run_working_tree_mode(policy_path, repo_root, args.mode or None)
        return run_diff_mode(args.diff_range, policy_path, repo_root, args.mode or None)

    if args.check_ledger:
        ledger_path = Path(args.ledger).resolve() if args.ledger else (repo_root / rl.LEDGER_REL).resolve()
        return run_ledger_mode(ledger_path, repo_root)

    return _usage("choose --check-ledger, --diff-range, or --working-tree")

if __name__ == "__main__":
    raise SystemExit(main())
