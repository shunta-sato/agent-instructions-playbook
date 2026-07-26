#!/usr/bin/env python3
"""Writer half of the submission-evidence pipeline (Wave 2 of the
lint-migration program; design record: `plans/20260726-submission-evidence.md`).

``record`` appends one ``submission_evidence`` record to the shared
``agent_run`` ledger (``.agents/runs/agent-runs.jsonl``), reusing
`scripts/agent_run.py`'s ledger machinery (``append_jsonl``, ``issue_run_id``,
its path/normalization helpers, and ``validation_commands``) instead of
re-implementing it; `agent_run.py` itself is never modified.

``changed_files`` is always COMPUTED by this tool from git -- ``--working-tree``
or ``--diff-range A..B`` -- and never accepted as caller-supplied arguments,
each existing path getting a sha256 at record time (``null`` for a path that
no longer exists there). The ledger's OWN path is unconditionally excluded
from ``changed_files``: appending this very record would otherwise always
self-dirty it, turning every record into a false "the ledger changed" entry.

This writer VALIDATES SHAPE ONLY (well-formed validation pairs / citations /
triggered-branch declarations). It does not re-derive whether a cited run is
actually accepted or a cited artifact actually exists -- that re-derivation
is `scripts/lint_submission.py`'s job (the checker), per the design record's
writer/checker split.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

try:  # direct execution: scripts/ is on sys.path[0]
    import agent_run as ar
except ModuleNotFoundError:  # imported as scripts.submission_run (tests, -m)
    from scripts import agent_run as ar

SCHEMA_VERSION = 1
RECORD_TYPE = "submission_evidence"
RUN_SLUG = "submission"


# --- git plumbing -------------------------------------------------------------

def _git(repo_root: Path, *args: str, expect_ok: bool = True) -> subprocess.CompletedProcess:
    """Run git; ``expect_ok`` raises ValueError on a nonzero exit (fail-closed,
    no fallback parsing). ``expect_ok=False`` is for calls where a nonzero exit
    is an EXPECTED outcome carrying its own meaning (a path absent at a ref
    means "deleted", not a git failure) rather than an error."""
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), "-c", "core.quotepath=false", *args],
            capture_output=True,
        )
    except FileNotFoundError as exc:
        raise ValueError("git executable was not found") from exc
    if expect_ok and completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).decode("utf-8", "replace").strip()
        raise ValueError(f"git {' '.join(args)} failed: {detail}")
    return completed


def _z_paths(completed: subprocess.CompletedProcess) -> list[str]:
    return [p.decode("utf-8", "surrogateescape") for p in completed.stdout.split(b"\0") if p]


def changed_paths_working_tree(repo_root: Path) -> list[str]:
    """``git status --porcelain -z --untracked-files=all``: NUL-delimited, a
    rename/copy's second bare token is the ORIG_PATH (mirrors
    scripts/research_gate.py's hardened parsing) -- kept as its own entry, not
    collapsed into the destination, so it gets its own changed_files row."""
    paths: list[str] = []
    skip_next = False
    for token in _z_paths(_git(repo_root, "status", "--porcelain", "-z", "--untracked-files=all")):
        if skip_next:
            paths.append(token)
            skip_next = False
            continue
        status, path = token[:2], token[3:]
        paths.append(path)
        skip_next = "R" in status or "C" in status
    return paths


def changed_paths_diff_range(repo_root: Path, diff_range: str) -> list[str]:
    """``--no-renames`` so a rename's origin appears as its own (deleted) path
    rather than being paired away, mirroring scripts/research_gate.py."""
    return _z_paths(_git(repo_root, "diff", "--no-renames", "--name-only", "-z", diff_range))


def base_ref_of_diff_range(diff_range: str) -> str:
    """Left ref of ``A..B``/``A...B``, trailing dots stripped (mirrors
    scripts/research_gate.py's ``base_ref_of_range``)."""
    return diff_range.split("..", 1)[0].rstrip(".")


def head_ref_of_diff_range(diff_range: str) -> str:
    """Right ref of ``A..B``/``A...B``; an empty right side (``A..``) resolves
    to HEAD (mirrors scripts/research_gate.py's ``head_ref_of_range``)."""
    return re.split(r"\.\.\.?", diff_range)[-1] or "HEAD"


def current_branch(repo_root: Path) -> str:
    return _git(repo_root, "rev-parse", "--abbrev-ref", "HEAD").stdout.decode("utf-8", "replace").strip()


def sha256_on_disk(repo_root: Path, rel_path: str) -> str | None:
    """Current on-disk bytes at record time; ``None`` when the path no longer
    exists there (a deletion, or the origin side of a rename). A symlink
    hashes its readlink TARGET STRING -- the same content git stores as its
    blob -- rather than the bytes it points at, mirroring agent_run.py's own
    reviewed-file digest so identity stays git-blob-consistent."""
    absolute = repo_root / rel_path
    if absolute.is_symlink():
        return hashlib.sha256(os.readlink(absolute).encode("utf-8")).hexdigest()
    if absolute.is_file():
        return hashlib.sha256(absolute.read_bytes()).hexdigest()
    return None


def sha256_at_ref(repo_root: Path, ref: str, rel_path: str) -> str | None:
    """sha256 of ``rel_path``'s git blob at ``ref``; ``None`` when absent
    there (a deletion by that ref, or a --no-renames rename's origin path)."""
    completed = _git(repo_root, "show", f"{ref}:{rel_path}", expect_ok=False)
    if completed.returncode != 0:
        return None
    return hashlib.sha256(completed.stdout).hexdigest()


# --- record assembly -----------------------------------------------------------

def _changed_file_entries(repo_root: Path, args: argparse.Namespace, ledger_rel: str) -> tuple[list[dict[str, Any]], str]:
    """-> (changed_files, base_ref). Excludes ``ledger_rel`` -- the ledger's own
    path -- unconditionally: appending this record would otherwise always
    self-dirty it under --working-tree."""
    if args.working_tree:
        raw_paths = changed_paths_working_tree(repo_root)
        digest_of = lambda p: sha256_on_disk(repo_root, p)
        base_ref = ""
    else:
        diff_range = args.diff_range
        if ".." not in diff_range:
            raise ValueError(f"--diff-range must be A..B or A...B: {diff_range!r}")
        raw_paths = changed_paths_diff_range(repo_root, diff_range)
        head_ref = head_ref_of_diff_range(diff_range)
        digest_of = lambda p: sha256_at_ref(repo_root, head_ref, p)
        base_ref = base_ref_of_diff_range(diff_range)

    digests: dict[str, str | None] = {}
    for path in raw_paths:
        if path == ledger_rel or path in digests:
            continue
        digests[path] = digest_of(path)

    entries = sorted(
        ({"path": path, "sha256": digest} for path, digest in digests.items()),
        key=lambda entry: entry["path"],
    )
    return entries, base_ref


def _parse_triggered_branch(raw: str) -> dict[str, str]:
    if "=" not in raw:
        raise ValueError(f"--triggered-branch must be KEY=ARTIFACT: {raw!r}")
    key, artifact = raw.split("=", 1)
    key, artifact = key.strip(), artifact.strip()
    if not key or not artifact:
        raise ValueError(f"--triggered-branch KEY and ARTIFACT must both be non-empty: {raw!r}")
    return {"branch": key, "artifact": artifact}


def _cited_runs(raw_run_ids: list[str] | None) -> list[str]:
    for run_id in raw_run_ids or []:
        if not run_id.strip():
            raise ValueError("--cited-run must be non-empty")
    return ar.unique_sorted(raw_run_ids or [])


def build_record(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    repo_root = ar.repo_root_from_args(args.repo_root)
    ledger_path = ar.ledger_path_from_args(repo_root, args.ledger)
    ledger_rel = ar.normalize_repo_path(str(ledger_path), repo_root)

    changed_files, base_ref = _changed_file_entries(repo_root, args, ledger_rel)
    if args.diff_range:
        head_commit = _git(repo_root, "rev-parse", head_ref_of_diff_range(args.diff_range)).stdout.decode("utf-8", "replace").strip()
    else:
        head_commit = _git(repo_root, "rev-parse", "HEAD").stdout.decode("utf-8", "replace").strip()
    branch = current_branch(repo_root)
    commands = ar.validation_commands(args.validation_result)
    cited_runs = _cited_runs(args.cited_run)
    triggered_branches = [_parse_triggered_branch(raw) for raw in args.triggered_branch or []]

    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "record_type": RECORD_TYPE,
        "run_id": ar.issue_run_id(RUN_SLUG),
        # No separate importable "utc timestamp" symbol exists in agent_run.py
        # (it builds created_at inline in build_run_record); this mirrors that
        # same stdlib expression rather than reaching for a private helper.
        "created_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "branch": branch,
        "base_ref": base_ref,
        "head_commit": head_commit,
        "changed_files": changed_files,
        "validation": {"commands": commands},
        "cited_runs": cited_runs,
        "triggered_branches": triggered_branches,
        "gate_decision": args.gate_decision,
        "notes": args.notes or "",
    }
    return ledger_path, record


# --- CLI -----------------------------------------------------------------------

def add_record_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("record", help="Append one submission_evidence record.")
    parser.add_argument("--repo-root", default="", help="Repository root.")
    parser.add_argument("--ledger", default="", help="Ledger path; defaults to .agents/runs/agent-runs.jsonl.")

    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--working-tree", action="store_true", help="Compute changed_files from `git status --porcelain -z --untracked-files=all`.")
    source.add_argument("--diff-range", metavar="A..B", default="", help="Compute changed_files from `git diff --name-only A..B`; base_ref is the range's left side.")

    parser.add_argument("--validation-result", action="append", nargs=2, metavar=("CMD", "EXIT_CODE"), help="Validation command and exit code (same semantics as agent_run.py). Repeat for multiple commands.")
    parser.add_argument("--cited-run", action="append", metavar="RUN_ID", help="agent_run run_id this submission cites as evidence. Repeat for multiple.")
    parser.add_argument("--triggered-branch", action="append", metavar="KEY=ARTIFACT", help="A quality-gate branch key and the artifact path (or run id) satisfying it. Repeat for multiple.")
    parser.add_argument("--gate-decision", required=True, choices=("submit", "no-submit"), help="The quality-gate decision this submission_evidence record reports.")
    parser.add_argument("--notes", default="", help="Free-text open risks or skips.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append submission_evidence records to the agent_run ledger.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    add_record_parser(subparsers)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command != "record":
            raise ValueError(f"unknown command: {args.command}")
        ledger_path, record = build_record(args)
        ar.append_jsonl(ledger_path, record)
    except ValueError as exc:
        print(f"submission-run: error: {exc}", file=sys.stderr)
        return 1

    print(record["run_id"])
    print(
        f"submission_evidence: {len(record['changed_files'])} changed file(s), "
        f"gate_decision={record['gate_decision']}, ledger={ledger_path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
