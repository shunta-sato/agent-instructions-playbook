#!/usr/bin/env python3
"""Validate ``submission_evidence`` ledger records (Wave 2 of the
lint-migration program; ``plans/20260726-submission-evidence.md``).

Same ledger as ``agent_run``. The writer (``scripts/submission_run.py``)
captures changed-file digests, validation results, cited run IDs,
triggered-branch artifacts, ``gate_decision``, and ``head_commit`` -- the
commit whose state the digests describe. This checker RE-DERIVES every
DECLARED claim against that commit identity; it cannot detect omissions
(an evidence branch the recorder never declared), which stays a
quality-gate judgment until a path-class map exists.

Modes (mutually exclusive): ``--record RUN_ID`` validates that record
against its own ``head_commit``. ``--diff-range A..B`` validates EVERY
submission record whose ``head_commit`` lies inside the range (reachable
from B, not from A) -- a merged record describes its own commit forever
and never blocks later branches. ``--working-tree`` validates records
whose ``head_commit`` equals the current HEAD, with digests checked
against the working tree (the dirt those records describe). No candidate
=> adoption-phase pass, exit 0 (adjudication 3).

Findings: ``schema:<field>`` (presence AND type; paths must be relative
without ``..``); ``cited-run:{missing,not-accepted,gate,duplicate}:<id>``
(re-derived acceptance; ``quality_gate`` must be pass/submit, or
``not_run`` when this record's own gate_decision is submit -- the
supervisor's gate stands in for an ungated worker run);
``artifact-missing:<path|branch>``; ``artifact-run:*`` (run-id-shaped
artifacts re-validated as citations); ``contract-not-submit:<path>`` (the
FIRST decision token in ``## Decision`` must be ``submit``; the unfilled
``submit / no-submit`` template is a finding); ``validation-chain-missing``
/ ``validation-failed:<cmd>`` (canonical chain present AND no recorded
command failed -- exit codes are the recorder's declaration, nothing is
re-executed); ``stale-record:<path>``; ``gate-decision:<value>``.

Exit 0 clean/adoption-phase, 1 findings, 2 usage/lookup errors. Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:  # direct execution: scripts/ is on sys.path[0]
    import agent_run as ar
    import submission_checks as sc
except ModuleNotFoundError:  # imported as scripts.lint_submission (tests, -m)
    from scripts import agent_run as ar
    from scripts import submission_checks as sc

# Re-exported so tests and callers keep one import surface.
check_schema = sc.check_schema
check_cited_runs = sc.check_cited_runs
check_triggered_branches = sc.check_triggered_branches
check_validation_chain = sc.check_validation_chain
check_freshness = sc.check_freshness
check_gate_decision = sc.check_gate_decision
evaluate_submission_record = sc.evaluate_submission_record

SUBMISSION_RECORD_TYPE = "submission_evidence"
AGENT_RUN_RECORD_TYPE = "agent_run"
DEFAULT_LEDGER_REL = ".agents/runs/agent-runs.jsonl"

# Pinned schema (plans/20260726-submission-evidence.md's "Record schema" block).
REQUIRED_FIELDS = (
    "schema_version", "record_type", "run_id", "created_at", "branch",
    "base_ref", "head_commit", "changed_files", "validation", "cited_runs",
    "triggered_branches", "gate_decision", "notes",
)
FIELD_TYPES = {
    "changed_files": list, "cited_runs": list, "triggered_branches": list,
    "validation": dict, "gate_decision": str, "branch": str, "notes": str,
}

# The canonical verify chain (COMMANDS.md: `make verify`, `make lint`, and the
# `python3 -m unittest ...` command the ledger actually records). Do not add
# markers beyond these three -- the brief pins exactly this pair/single.
VERIFY_MARKER = "make verify"
UNITTEST_MARKER = "python3 -m unittest"
LINT_MARKER = "make lint"

DECISION_SECTION_RE = re.compile(r"^## Decision\s*\n(.*?)(?:\n## |\Z)", re.S | re.M)
DECISION_TOKEN_RE = re.compile(r"\b(no-submit|submit)\b")
UNFILLED_TEMPLATE_RE = re.compile(r"\bsubmit\s*/\s*no-submit\b")

# --- repo/ledger plumbing (mirrors scripts/agent_run.py) --------------------

def repo_root_from_args(explicit_root: str) -> Path:
    return Path(explicit_root).resolve() if explicit_root else Path(__file__).resolve().parent.parent

def ledger_path_from_args(repo_root: Path, explicit_ledger: str) -> Path:
    if explicit_ledger:
        ledger_path = Path(explicit_ledger)
        if not ledger_path.is_absolute():
            ledger_path = repo_root / ledger_path
        return ledger_path.resolve()
    return (repo_root / DEFAULT_LEDGER_REL).resolve()

def load_ledger_records(ledger_path: Path) -> list[dict[str, Any]]:
    """All JSON-object lines (any record_type); ``[]`` when the ledger is absent."""
    if not ledger_path.is_file():
        return []
    records: list[dict[str, Any]] = []
    for line_no, raw_line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{ledger_path}:{line_no}: invalid JSON: {exc.msg}") from exc
        if isinstance(payload, dict):
            records.append(payload)
    return records

# --- git state resolution ---------------------------------------------------

# --- record selection --------------------------------------------------------

def find_submission_record(records: list[dict[str, Any]], run_id: str) -> dict[str, Any] | None:
    matches = [r for r in records if r.get("record_type") == SUBMISSION_RECORD_TYPE and r.get("run_id") == run_id]
    return matches[-1] if matches else None

def _is_ancestor(repo_root: Path, ancestor: str, descendant: str) -> bool:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "merge-base", "--is-ancestor", ancestor, descendant],
        capture_output=True,
    )
    return result.returncode == 0

def _rev_parse(repo_root: Path, ref: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--verify", f"{ref}^{{commit}}"],
        capture_output=True, text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None

def candidate_records_for_range(
    repo_root: Path, records: list[dict[str, Any]], base: str, head: str
) -> list[dict[str, Any]]:
    """Submission records whose head_commit lies inside base..head. A merged
    record's head_commit is reachable from base, so it is excluded and can
    never turn stale against a later branch (F1). ALL candidates are
    evaluated -- a clean record cannot shadow a dirty sibling (F11)."""
    candidates = []
    for record in records:
        if record.get("record_type") != SUBMISSION_RECORD_TYPE:
            continue
        head_commit = record.get("head_commit")
        if not isinstance(head_commit, str) or not head_commit:
            continue
        if _rev_parse(repo_root, head_commit) is None:
            continue
        if _is_ancestor(repo_root, head_commit, head) and not _is_ancestor(repo_root, head_commit, base):
            candidates.append(record)
    return candidates

def candidate_records_for_head(
    repo_root: Path, records: list[dict[str, Any]], head_sha: str
) -> list[dict[str, Any]]:
    return [
        r for r in records
        if r.get("record_type") == SUBMISSION_RECORD_TYPE
        and r.get("head_commit") == head_sha
    ]

# --- CLI ---------------------------------------------------------------------

def _emit(findings: list[str], detail: str) -> int:
    for finding in findings:
        print(f"FINDING {finding}")
    if findings:
        print(f"lint-submission: {len(findings)} finding(s)")
        return 1
    suffix = f" ({detail})" if detail else ""
    print(f"lint-submission: pass{suffix}")
    return 0

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate submission_evidence ledger records.")
    parser.add_argument("--repo-root", default="", help="Repository root override.")
    parser.add_argument("--ledger", default="", help="Ledger path override.")
    parser.add_argument("--record", metavar="RUN_ID", default="", help="Validate exactly this submission_evidence record.")
    parser.add_argument("--working-tree", action="store_true", help="Match against git status --porcelain.")
    parser.add_argument("--diff-range", metavar="A..B", default="", help="Match against git diff --name-only A..B.")
    args = parser.parse_args(argv)
    if sum([bool(args.record), args.working_tree, bool(args.diff_range)]) != 1:
        parser.error("choose exactly one of --record RUN_ID, --working-tree, or --diff-range A..B")
    return args

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = repo_root_from_args(args.repo_root)
    ledger_path = ledger_path_from_args(repo_root, args.ledger)

    try:
        records = load_ledger_records(ledger_path)
    except ValueError as exc:
        print(f"lint-submission: error: {exc}", file=sys.stderr)
        return 2

    agent_runs_by_id: dict[str, dict[str, Any]] = {}
    duplicate_ids: set[str] = set()
    for r in records:
        if r.get("record_type") == AGENT_RUN_RECORD_TYPE and isinstance(r.get("run_id"), str):
            if r["run_id"] in agent_runs_by_id:
                duplicate_ids.add(r["run_id"])
            agent_runs_by_id[r["run_id"]] = r

    if args.record:
        record = find_submission_record(records, args.record)
        if record is None:
            print(f"lint-submission: error: submission_evidence record not found: {args.record}", file=sys.stderr)
            return 2
        head_commit = record.get("head_commit")
        if isinstance(head_commit, str) and head_commit and _rev_parse(repo_root, head_commit) is None:
            # A claimed-but-unresolvable identity must not fall back to the
            # working tree: that would validate against unrelated state.
            return _emit([f"unknown-head-commit:{head_commit}"], "")
        state_ref = head_commit if isinstance(head_commit, str) and head_commit else None
        findings = evaluate_submission_record(
            record, repo_root, agent_runs_by_id, state_ref, duplicate_ids
        )
        return _emit(findings, f"{args.record} validated")

    if args.working_tree:
        head_sha = _rev_parse(repo_root, "HEAD")
        if head_sha is None:
            print("lint-submission: error: cannot resolve HEAD", file=sys.stderr)
            return 2
        candidates = candidate_records_for_head(repo_root, records, head_sha)
        state_ref = None  # digests describe the dirt on HEAD => check disk
    else:
        base, _, head = args.diff_range.partition("..")
        head = head.lstrip(".") or "HEAD"
        base_sha = _rev_parse(repo_root, base)
        head_sha = _rev_parse(repo_root, head)
        if base_sha is None or head_sha is None:
            print(f"lint-submission: error: cannot resolve range {args.diff_range}", file=sys.stderr)
            return 2
        candidates = candidate_records_for_range(repo_root, records, base_sha, head_sha)
        state_ref = "own"  # each record describes its OWN commit, also in-range:
        # a later commit editing an earlier record's files must not stale it.

    if not candidates:
        print("lint-submission: pass (no submission record; adoption phase)")
        return 0

    findings: list[str] = []
    for record in candidates:
        record_ref = record.get("head_commit") if state_ref == "own" else state_ref
        findings += evaluate_submission_record(
            record, repo_root, agent_runs_by_id, record_ref, duplicate_ids
        )
    ids = ", ".join(str(r.get("run_id")) for r in candidates)
    return _emit(findings, f"{ids} validated ({len(candidates)} candidate(s))")

if __name__ == "__main__":
    raise SystemExit(main())
