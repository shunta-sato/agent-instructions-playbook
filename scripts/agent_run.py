#!/usr/bin/env python3
"""Record lightweight delegated agent runs in a repository-local JSONL ledger."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
RUN_RECORD_TYPE = "agent_run"
DEFAULT_LEDGER_REL = ".agents/runs/agent-runs.jsonl"
FAILING_QUALITY_GATES = {"blocked", "error", "fail", "failed", "no-submit", "no_submit", "reject", "rejected"}

def repo_root_from_args(explicit_root: str) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path(__file__).resolve().parent.parent

def ledger_path_from_args(repo_root: Path, explicit_ledger: str) -> Path:
    if explicit_ledger:
        ledger_path = Path(explicit_ledger)
        if not ledger_path.is_absolute():
            ledger_path = repo_root / ledger_path
        return ledger_path.resolve()
    return (repo_root / DEFAULT_LEDGER_REL).resolve()

def normalize_repo_path(raw_path: str, repo_root: Path) -> str:
    path = Path(raw_path)
    if path.is_absolute():
        try:
            relpath = path.resolve().relative_to(repo_root.resolve())
        except ValueError as exc:
            raise ValueError(f"path is outside repo root: {raw_path}") from exc
    else:
        relpath = path

    if not relpath.parts or ".." in relpath.parts:
        raise ValueError(f"path must be repo-relative and must not contain '..': {raw_path}")
    return relpath.as_posix()

def unique_sorted(paths: list[str]) -> list[str]:
    return sorted(dict.fromkeys(paths))

def _sha256_reviewed_path(path: Path) -> str:
    """A symlink hashes its readlink TARGET STRING (git's own blob content for
    it); a regular file hashes its bytes."""
    if path.is_symlink():
        return hashlib.sha256(os.readlink(path).encode("utf-8")).hexdigest()
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _sha256_head_blob(repo_root: Path, rel_path: str) -> str:
    """sha256 of ``rel_path``'s git blob at current HEAD; raises if absent there."""
    completed = subprocess.run(["git", "-C", str(repo_root), "show", f"HEAD:{rel_path}"], capture_output=True)
    if completed.returncode != 0:
        raise ValueError(f"reviewed-deleted path does not exist at HEAD: {rel_path}")
    return hashlib.sha256(completed.stdout).hexdigest()

def _git_mode(repo_root: Path, rel_path: str) -> str | None:
    """M2: git mode (100644/100755/120000); ``None`` when untracked/no repo."""
    completed = subprocess.run(
        ["git", "-C", str(repo_root), "ls-files", "--stage", "--", rel_path], capture_output=True, text=True,
    )
    line = completed.stdout.strip()
    return line.split()[0] if line else None

def reviewed_files_from_args(raw_paths: list[str] | None, repo_root: Path) -> list[dict[str, str]]:
    """Q3b/M2: the SCRIPT records each reviewed path's (sha256, git-mode)."""
    entries: dict[str, dict[str, str]] = {}
    for raw in raw_paths or []:
        rel = normalize_repo_path(raw, repo_root)
        if rel in entries:
            continue
        absolute = repo_root / rel
        if not (absolute.is_symlink() or absolute.is_file()):
            raise ValueError(f"reviewed file is missing: {raw}")
        entries[rel] = {"path": rel, "sha256": _sha256_reviewed_path(absolute)}
        mode = _git_mode(repo_root, rel)
        if mode:
            entries[rel]["mode"] = mode
    return sorted(entries.values(), key=lambda entry: entry["path"])

def reviewed_deletions_from_args(raw_paths: list[str] | None, repo_root: Path) -> list[dict[str, Any]]:
    """(c)/M2: ``--reviewed-deleted PATH`` tombstones a path (base_sha256 +
    base/HEAD git-mode), hashed now since deletion leaves no head blob later."""
    entries: dict[str, dict[str, Any]] = {}
    for raw in raw_paths or []:
        rel = normalize_repo_path(raw, repo_root)
        if rel not in entries:
            entries[rel] = {"path": rel, "deleted": True, "base_sha256": _sha256_head_blob(repo_root, rel)}
            mode = _git_mode(repo_root, rel)
            if mode:
                entries[rel]["mode"] = mode
    return sorted(entries.values(), key=lambda entry: entry["path"])

def issue_run_id(slug: str) -> str:
    safe_slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", slug.strip()).strip("-._")
    if not safe_slug:
        safe_slug = "agent-run"
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{timestamp}-{safe_slug}-{uuid.uuid4().hex[:8]}"

def parse_bool(value: str) -> bool:
    normalized = value.lower()
    if normalized in {"1", "true", "yes", "y"}:
        return True
    if normalized in {"0", "false", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"expected boolean value, got {value!r}")

def git_lines(repo_root: Path, args: list[str]) -> list[str]:
    try:
        completed = subprocess.run(
            ["git", "-C", repo_root.as_posix(), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise ValueError("git executable was not found") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise ValueError(f"git {' '.join(args)} failed: {detail}") from exc
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]

def changed_files_from_git(repo_root: Path, include_untracked: bool) -> list[str]:
    paths = git_lines(repo_root, ["diff", "--name-only", "HEAD", "--"])
    if include_untracked:
        paths.extend(git_lines(repo_root, ["ls-files", "--others", "--exclude-standard"]))
    return unique_sorted([normalize_repo_path(path, repo_root) for path in paths])

def copy_brief(source: Path, run_id: str, ledger_path: Path, repo_root: Path) -> str:
    if not source.is_file():
        raise ValueError(f"brief source is missing: {source}")

    destination = ledger_path.parent / run_id / "brief.md"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return normalize_repo_path(destination, repo_root)

def validation_commands(raw_results: list[list[str]] | None) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    for command, exit_code_text in raw_results or []:
        if not command.strip():
            raise ValueError("validation command must be non-empty")
        try:
            exit_code = int(exit_code_text)
        except ValueError as exc:
            raise ValueError(f"validation exit code must be an integer: {exit_code_text}") from exc
        commands.append(
            {
                "cmd": command,
                "exit_code": exit_code,
                "passed": exit_code == 0,
            }
        )
    return commands

def validation_passed(validation: dict[str, Any]) -> bool:
    """M4: exact types, not truthiness — a bool exit_code/non-True passed is rejected."""
    if validation.get("blocker"):
        return False
    commands = validation.get("commands", [])
    if not isinstance(commands, list) or not commands:
        return False
    return all(
        isinstance(command, dict)
        and isinstance(command.get("cmd"), str)
        and bool(command["cmd"].strip())
        and type(command.get("exit_code")) is int  # excludes bool: type(True) is bool, not int
        and command.get("exit_code") == 0  # every command's own exit code, not just a caller-set flag
        and command.get("passed") is True
        for command in commands
    )

def quality_gate_allows_acceptance(value: Any) -> bool:
    normalized = str(value or "not_run").strip().lower()
    return normalized not in FAILING_QUALITY_GATES

def evaluate_run_record(record: dict[str, Any]) -> dict[str, Any]:
    allowed_files = set(record.get("allowed_files", []))
    changed_files = set(record.get("changed_files", []))
    outside_allowed_files = sorted(changed_files - allowed_files)

    validation = record.get("validation", {})
    validation_ok = validation_passed(validation if isinstance(validation, dict) else {})
    quality_gate = validation.get("quality_gate", "not_run") if isinstance(validation, dict) else "not_run"

    outcome = record.get("outcome", {})
    # M4: identity, not truthiness — bool("false") is True, so a forged string must not pass.
    agent_completed = outcome.get("agent_completed") is True if isinstance(outcome, dict) else False
    scope_compliant = not outside_allowed_files
    accepted = (
        agent_completed
        and validation_ok
        and scope_compliant
        and quality_gate_allows_acceptance(quality_gate)
    )

    telemetry = record.get("telemetry", {})
    telemetry_status = telemetry.get("status", "not_collected") if isinstance(telemetry, dict) else "not_collected"

    return {
        "accepted": accepted,
        "agent_completed": agent_completed,
        "validation_passed": validation_ok,
        "scope_compliant": scope_compliant,
        "outside_allowed_files": outside_allowed_files,
        "quality_gate": quality_gate,
        "telemetry_status": telemetry_status,
    }

def load_agent_run_records(ledger_path: Path) -> list[dict[str, Any]]:
    if not ledger_path.is_file():
        raise ValueError(f"ledger file is missing: {ledger_path}")

    records: list[dict[str, Any]] = []
    for line_no, raw_line in enumerate(ledger_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{ledger_path}:{line_no}: invalid JSON: {exc.msg}") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"{ledger_path}:{line_no}: expected JSON object")
        if payload.get("record_type") == RUN_RECORD_TYPE:
            records.append(payload)
    return records

def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(payload, sort_keys=True, separators=(",", ":")))
        file.write("\n")

def telemetry_from_args(args: argparse.Namespace, repo_root: Path) -> dict[str, Any]:
    if not args.codex_jsonl:
        return {"status": "not_collected"}

    from parse_codex_jsonl import extract_telemetry_from_file

    path = Path(args.codex_jsonl)
    if not path.is_absolute():
        path = repo_root / path
    return extract_telemetry_from_file(path.resolve())

def build_run_record(args: argparse.Namespace) -> tuple[Path, dict[str, Any]]:
    repo_root = repo_root_from_args(args.repo_root)
    ledger_path = ledger_path_from_args(repo_root, args.ledger)
    run_id = args.run_id or issue_run_id(args.run_slug or args.task_class)

    allowed_files = unique_sorted(
        [normalize_repo_path(path, repo_root) for path in args.allowed_file]
    )
    changed_files = [normalize_repo_path(path, repo_root) for path in args.changed_file or []]
    if args.changed_from_git:
        changed_files.extend(changed_files_from_git(repo_root, args.include_untracked))
    changed_files = unique_sorted(changed_files)

    commands = validation_commands(args.validation_result)
    validation_blocker = args.validation_blocker or None
    validation = {
        "commands": commands,
        "passed": bool(commands) and all(command["passed"] for command in commands) and not validation_blocker,
        "blocker": validation_blocker,
        "quality_gate": args.quality_gate,
    }

    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "record_type": RUN_RECORD_TYPE,
        "run_id": run_id,
        "created_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "harness": args.harness,
        "task_class": args.task_class,
        "capability_profile": args.capability_profile,
        "requested_model": args.requested_model or None,
        "resolved_model": args.resolved_model or None,
        "resolver_lock_version": args.resolver_lock_version or None,
        "prompt_detail": args.prompt_detail,
        "effort": args.effort or None,
        "declared_mode": args.declared_mode or None,  # M1: research/delivery epistemic-mode evidence
        "brief_path": copy_brief(Path(args.brief_source).resolve(), run_id, ledger_path, repo_root),
        "allowed_files": allowed_files,
        "changed_files": changed_files,
        "validation": validation,
        "telemetry": telemetry_from_args(args, repo_root),
        "outcome": {
            "agent_completed": args.agent_completed,
        },
    }
    reviewed_paths = list(args.reviewed_file or [])
    if args.review_changed:  # B3: content-identity review, not just a changed-path listing
        reviewed_paths += args.changed_file or []
    reviewed_files = reviewed_files_from_args(reviewed_paths, repo_root)
    reviewed_files += reviewed_deletions_from_args(args.reviewed_deleted, repo_root)
    if reviewed_files:  # optional field: absent for the common no-review record
        record["reviewed_files"] = sorted(reviewed_files, key=lambda e: e["path"])
    record["outcome"].update(evaluate_run_record(record))
    return ledger_path, record

def render_record_text(ledger_path: Path, record: dict[str, Any]) -> str:
    outcome = record["outcome"]
    return "\n".join(
        [
            f"run_id: {record['run_id']}",
            f"ledger: {ledger_path}",
            f"accepted: {str(outcome['accepted']).lower()}",
            f"agent_completed: {str(outcome['agent_completed']).lower()}",
            f"validation_passed: {str(outcome['validation_passed']).lower()}",
            f"scope_compliant: {str(outcome['scope_compliant']).lower()}",
            f"telemetry_status: {outcome['telemetry_status']}",
        ]
    )

def add_record_parser(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    parser = subparsers.add_parser("record", help="Append one delegated agent run record.")
    parser.add_argument("--repo-root", default="", help="Repository root.")
    parser.add_argument("--ledger", default="", help="Ledger path; defaults to .agents/runs/agent-runs.jsonl.")
    parser.add_argument("--run-id", default="", help="Optional explicit run_id.")
    parser.add_argument("--run-slug", default="", help="Slug used when generating run_id.")
    parser.add_argument("--harness", required=True, help="Harness name, such as codex-cli or copilot-cli.")
    parser.add_argument("--task-class", required=True, help="Model-routing task class.")
    parser.add_argument("--capability-profile", required=True, help="Model-routing capability profile.")
    parser.add_argument("--requested-model", default="", help="Requested model, when supplied by current routing.")
    parser.add_argument("--resolved-model", default="", help="Resolved model, when known from current routing.")
    parser.add_argument("--resolver-lock-version", default="", help="Resolver lock/catalog version, when known.")
    parser.add_argument("--prompt-detail", required=True, choices=("compact", "normal", "strict"),
                         help="Prompt detail level from model routing.")
    parser.add_argument("--effort", default="", help="Effort setting, when applicable.")
    parser.add_argument("--declared-mode", default="", choices=("", "research", "delivery"),
                         help="M1: declared epistemic mode for this run, persisted as top-level declared_mode.")
    parser.add_argument("--brief-source", required=True, help="Task brief file to copy into the run directory.")
    parser.add_argument("--allowed-file", action="append", required=True,
                         help="Allowed edit file. Repeat for multiple files.")
    parser.add_argument("--changed-file", action="append",
                         help="Changed file to record. Repeat for multiple files.")
    parser.add_argument("--changed-from-git", action="store_true", help="Add changed files from git diff against HEAD.")
    parser.add_argument("--reviewed-file", action="append",
                         help="File reviewed for this run; the script records its sha256 at record time. Repeat.")
    parser.add_argument("--review-changed", action="store_true",
                         help="Also add every --changed-file path to reviewed_files with a script-computed digest.")
    parser.add_argument("--reviewed-deleted", action="append",
                         help="Path deleted in this change; records a tombstone (base_sha256+mode of its HEAD blob). Repeat.")
    parser.add_argument("--include-untracked", action=argparse.BooleanOptionalAction, default=True,
                         help="Include untracked files when using --changed-from-git.")
    parser.add_argument(
        "--validation-result",
        action="append",
        nargs=2,
        metavar=("CMD", "EXIT_CODE"),
        help="Validation command and exit code. Repeat for multiple commands.",
    )
    parser.add_argument("--validation-blocker", default="", help="Reason validation could not run.")
    parser.add_argument("--quality-gate", default="not_run", help="quality-gate result, when known.")
    parser.add_argument("--agent-completed", type=parse_bool, default=True,
                         help="Whether the delegated agent completed execution.")
    parser.add_argument("--codex-jsonl", default="", help="Optional Codex CLI JSONL to extract token usage from.")
    parser.add_argument("--format", choices=("json", "text"), default="text", help="Output format.")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Append lightweight delegated agent run records."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    add_record_parser(subparsers)
    return parser.parse_args()

def main() -> int:
    args = parse_args()
    try:
        if args.command != "record":
            raise ValueError(f"unknown command: {args.command}")
        ledger_path, record = build_run_record(args)
        append_jsonl(ledger_path, record)
    except ValueError as exc:
        print(f"Agent run recording failed: {exc}")
        return 1

    if args.format == "json":
        print(json.dumps(record, indent=2, sort_keys=True))
    else:
        print(render_record_text(ledger_path, record))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
