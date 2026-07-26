#!/usr/bin/env python3
"""Check functions for ``submission_evidence`` records, split from
``scripts/lint_submission.py`` (structure budget). Semantics, finding ids,
and the state_ref contract are documented in that module's docstring."""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
from pathlib import Path
from typing import Any

try:  # direct execution: scripts/ is on sys.path[0]
    import agent_run as ar
except ModuleNotFoundError:  # imported as scripts.submission_checks
    from scripts import agent_run as ar

SCHEMA_VERSION = 1
QUALITY_GATE_PASS = {"pass", "submit"}
CONTRACT_REVIEW_PREFIX = "reports/workflow-contract-review/"

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
RUN_ID_SHAPE_RE = re.compile(r"^\d{8}T\d{6}Z-")

# --- content resolution: a commit sha, or None for the working tree ---------

def _exists_at(repo_root: Path, state_ref: str | None, rel_path: str) -> bool:
    """state_ref None means the working tree; otherwise a commit sha."""
    if state_ref is None:
        absolute = repo_root / rel_path
        return absolute.is_file() or absolute.is_symlink()
    result = subprocess.run(
        ["git", "-C", str(repo_root), "cat-file", "-e", f"{state_ref}:{rel_path}"],
        capture_output=True,
    )
    return result.returncode == 0

def _read_at(repo_root: Path, state_ref: str | None, rel_path: str) -> str:
    if state_ref is None:
        try:
            return (repo_root / rel_path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""
    result = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{state_ref}:{rel_path}"],
        capture_output=True, text=True,
    )
    return result.stdout if result.returncode == 0 else ""

def _sha256_at(repo_root: Path, state_ref: str, rel_path: str) -> str | None:
    result = subprocess.run(
        ["git", "-C", str(repo_root), "show", f"{state_ref}:{rel_path}"], capture_output=True
    )
    return hashlib.sha256(result.stdout).hexdigest() if result.returncode == 0 else None

def _sha256_current(path: Path) -> str:
    """A symlink hashes its readlink TARGET STRING; a regular file hashes its
    bytes (mirrors scripts/agent_run.py's ``_sha256_reviewed_path``)."""
    if path.is_symlink():
        return hashlib.sha256(os.readlink(path).encode("utf-8")).hexdigest()
    return hashlib.sha256(path.read_bytes()).hexdigest()

def check_schema(record: dict[str, Any]) -> list[str]:
    findings = [f"schema:{field}" for field in REQUIRED_FIELDS if field not in record]
    if "schema_version" in record and record.get("schema_version") != SCHEMA_VERSION:
        findings.append("schema:schema_version")
    for field, expected_type in FIELD_TYPES.items():
        if field in record and not isinstance(record[field], expected_type):
            findings.append(f"schema:{field}")
    head_commit = record.get("head_commit")
    if "head_commit" in record and not (isinstance(head_commit, str) and head_commit):
        findings.append("schema:head_commit")
    for entry in record.get("changed_files") if isinstance(record.get("changed_files"), list) else []:
        path = entry.get("path") if isinstance(entry, dict) else None
        if (not isinstance(path, str) or not path or path.startswith("/")
                or ".." in path.split("/")):
            findings.append("schema:changed_files")
            break
    return sorted(set(findings))

def check_cited_runs(
    record: dict[str, Any],
    agent_runs_by_id: dict[str, dict[str, Any]],
    duplicate_ids: set[str] | None = None,
) -> list[str]:
    cited = record.get("cited_runs")
    if not isinstance(cited, list):
        return []
    # A never-gated worker run (quality_gate not_run) is citable only when
    # this record's own gate_decision is submit: the supervisor's gate
    # stands in for the worker's (F8).
    gate_standin = record.get("gate_decision") == "submit"
    findings: list[str] = []
    for run_id in cited:
        run_id_str = run_id if isinstance(run_id, str) else str(run_id)
        run = agent_runs_by_id.get(run_id_str) if isinstance(run_id, str) else None
        if run is None:
            findings.append(f"cited-run:missing:{run_id_str}")
            continue
        if duplicate_ids and run_id_str in duplicate_ids:
            findings.append(f"cited-run:duplicate:{run_id_str}")
        if ar.evaluate_run_record(run)["accepted"] is not True:
            findings.append(f"cited-run:not-accepted:{run_id_str}")
        validation = run.get("validation")
        quality_gate = validation.get("quality_gate") if isinstance(validation, dict) else None
        gate_value = str(quality_gate or "").strip().lower()
        if gate_value not in QUALITY_GATE_PASS and not (gate_value == "not_run" and gate_standin):
            findings.append(f"cited-run:gate:{run_id_str}")
    return findings

def _decision_concludes_submit(text: str) -> bool:
    """The FIRST decision token in the section decides; the shipped
    template's literal `submit / no-submit` line means unfilled (F6)."""
    match = DECISION_SECTION_RE.search(text)
    if not match:
        return False
    body = match.group(1)
    if UNFILLED_TEMPLATE_RE.search(body):
        return False
    token = DECISION_TOKEN_RE.search(body)
    return bool(token and token.group(1) == "submit")

RUN_ID_SHAPE_RE = re.compile(r"^\d{8}T\d{6}Z-")


def check_triggered_branches(
    record: dict[str, Any],
    repo_root: Path,
    agent_runs_by_id: dict[str, dict[str, Any]],
    state_ref: str | None = None,
) -> list[str]:
    triggered = record.get("triggered_branches")
    if not isinstance(triggered, list):
        return []
    findings: list[str] = []
    for entry in triggered:
        if not isinstance(entry, dict):
            findings.append("artifact-missing:<malformed entry>")
            continue
        artifact = entry.get("artifact")
        if not isinstance(artifact, str) or not artifact:
            branch = entry.get("branch") if isinstance(entry.get("branch"), str) else "<unnamed>"
            findings.append(f"artifact-missing:{branch}")
            continue
        if RUN_ID_SHAPE_RE.match(artifact):
            findings += [
                f.replace("cited-run:", "artifact-run:", 1)
                for f in check_cited_runs(
                    {"cited_runs": [artifact], "gate_decision": record.get("gate_decision")},
                    agent_runs_by_id,
                )
            ]
            continue
        if not _exists_at(repo_root, state_ref, artifact):
            findings.append(f"artifact-missing:{artifact}")
            continue
        if artifact.startswith(CONTRACT_REVIEW_PREFIX):
            if not _decision_concludes_submit(_read_at(repo_root, state_ref, artifact)):
                findings.append(f"contract-not-submit:{artifact}")
    return findings

def _cmd_ok(cmd: Any) -> bool:
    return (
        isinstance(cmd, dict)
        and type(cmd.get("exit_code")) is int  # excludes bool: type(True) is bool, not int
        and cmd.get("exit_code") == 0
        and cmd.get("passed") is True
    )

def check_validation_chain(record: dict[str, Any]) -> list[str]:
    validation = record.get("validation")
    commands = validation.get("commands") if isinstance(validation, dict) else None
    if not isinstance(commands, list):
        return ["validation-chain-missing"]

    verify_cmds = [c for c in commands if isinstance(c, dict) and VERIFY_MARKER in str(c.get("cmd", ""))]
    unittest_cmds = [c for c in commands if isinstance(c, dict) and UNITTEST_MARKER in str(c.get("cmd", ""))]
    lint_cmds = [c for c in commands if isinstance(c, dict) and LINT_MARKER in str(c.get("cmd", ""))]

    verify_ok = any(_cmd_ok(c) for c in verify_cmds)
    pair_ok = any(_cmd_ok(c) for c in unittest_cmds) and any(_cmd_ok(c) for c in lint_cmds)

    # Every recorded failing command is a finding regardless of the chain
    # verdict -- a passing marker must not launder an honest failure (F5).
    findings = [
        f"validation-failed:{c.get('cmd')}"
        for c in commands
        if isinstance(c, dict) and not _cmd_ok(c)
    ]
    if not (verify_ok or pair_ok):
        findings.append("validation-chain-missing")
    return findings

def check_freshness(
    record: dict[str, Any], repo_root: Path, state_ref: str | None = None
) -> list[str]:
    changed = record.get("changed_files")
    if not isinstance(changed, list):
        return []
    findings: list[str] = []
    for entry in changed:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path")
        if not isinstance(path, str) or not path:
            continue
        expected_sha = entry.get("sha256")
        if state_ref is None:
            absolute = repo_root / path
            exists = absolute.is_file() or absolute.is_symlink()
            actual = _sha256_current(absolute) if exists else None
        else:
            actual = _sha256_at(repo_root, state_ref, path)
            exists = actual is not None
        if expected_sha is None:
            if exists:
                findings.append(f"stale-record:{path}")
            continue
        if actual != expected_sha:
            findings.append(f"stale-record:{path}")
    return findings

def check_gate_decision(record: dict[str, Any]) -> list[str]:
    value = record.get("gate_decision")
    return [] if value == "submit" else [f"gate-decision:{value}"]

def evaluate_submission_record(
    record: dict[str, Any],
    repo_root: Path,
    agent_runs_by_id: dict[str, dict[str, Any]],
    state_ref: str | None = None,
    duplicate_ids: set[str] | None = None,
) -> list[str]:
    findings: list[str] = []
    findings += check_schema(record)
    findings += check_cited_runs(record, agent_runs_by_id, duplicate_ids)
    findings += check_triggered_branches(record, repo_root, agent_runs_by_id, state_ref)
    findings += check_validation_chain(record)
    findings += check_freshness(record, repo_root, state_ref)
    findings += check_gate_decision(record)
    return findings

