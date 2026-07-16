#!/usr/bin/env python3
"""Boundary-gate half of the Research OS evidence checker (ledger-chain half +
CLI live in ``check_research_evidence``, split for the structure budget).
Evaluates a changed-path set under a declared ``--mode`` for promotion,
symlink-boundary, and safety findings (default-deny); loads the policy with
base-ref binding (F6); binds acknowledgments to ``agent_run`` evidence (R4)
whose OWN outcome re-derives as accepted. Coverage is EVIDENCE not
authorization and requires CONTENT identity: a LIVE path needs a
digest-verified ``reviewed_files`` entry (never ``changed_files``/B3 or
``allowed_files``/Q3a-b); a DELETED path (present at base, absent at head)
needs a tombstone entry (``deleted: true`` + matching ``base_sha256``) — the
two entry kinds never cover each other's path kind. Ack files + the run
ledger are the promotion MECHANISM, never promotion-required (Q3d). Recorded
validation/quality-gate fields are SELF-REPORTS, not executed proof; the CI
workflow at the reviewed head is the EXECUTED evidence. Tamper-EVIDENT, not
tamper-PROOF. Stdlib only."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

try:  # direct execution: scripts/ is on sys.path[0]
    import research_ledger as rl
except ModuleNotFoundError:  # imported as scripts.research_gate (tests, -m)
    from scripts import research_ledger as rl

try:
    import agent_run as ar
except ModuleNotFoundError:
    from scripts import agent_run as ar

POLICY_REL = ".agents/project-policy.yml"
PROMOTIONS_DIR = ".agents/promotions/"  # an acknowledgment is any *.md here except README.md
AGENT_RUN = "agent_run"
# Q3c: a Delivery-run is evidence only with an explicitly recorded passing gate.
QUALITY_GATE_PASS = ("pass", "submit")

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

# --- policy ------------------------------------------------------------------

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

def head_ref_of_range(diff_range: str) -> str:
    """Right ref of ``A..B``/``A...B`` — the diff head reviewed_files digests verify against (Q3b)."""
    return re.split(r"\.\.\.?", diff_range)[-1] or "HEAD"

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

# --- agent-run evidence (R4 / Q3) --------------------------------------------

def load_agent_runs(repo_root: Path) -> dict[str, dict[str, Any]]:
    """Canonical ``agent_run`` records indexed by run_id (empty if absent)."""
    path = repo_root / rl.LEDGER_REL
    runs: dict[str, dict[str, Any]] = {}
    if not path.is_file():
        return runs
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(rec, dict) and rec.get("record_type") == AGENT_RUN and rec.get("run_id"):
            runs[rec["run_id"]] = rec
    return runs

def _run_is_delivery_evidence(run: dict[str, Any]) -> tuple[bool, str]:
    """Q3c: evidence only with passing validation COMMANDS + an explicit
    passing quality gate + the run's own re-derived ``evaluate_run_record``
    acceptance (agent_completed + in-scope changes) — never a stored boolean."""
    validation = run.get("validation")
    if not isinstance(validation, dict) or not ar.validation_passed(validation):
        return False, "did not pass validation"
    gate = str(validation.get("quality_gate", "")).strip().lower()
    if gate not in QUALITY_GATE_PASS:
        return False, "quality gate not recorded as pass"
    if ar.evaluate_run_record(run)["accepted"] is not True:
        return False, "run outcome was not accepted"
    return True, ""

def ack_evidence_gaps(
    claim_ids: list[str], run_ids: list[str], valid_claims: set[str], runs: dict[str, dict[str, Any]]
) -> list[str]:
    """R4.1/R4.2 + Q3c: reasons an otherwise-structural acknowledgment fails to
    bind to ledger evidence (unresolved claim, unknown run, or a run that
    didn't pass validation / quality-gate / its own acceptance re-derivation)."""
    gaps = [f"claim {cid} does not resolve in the canonical ledger"
            for cid in claim_ids if cid not in valid_claims]
    for rid in run_ids:
        run = runs.get(rid)
        if run is None:
            gaps.append(f"unknown Delivery-run {rid}")
            continue
        ok, reason = _run_is_delivery_evidence(run)
        if not ok:
            gaps.append(f"run {rid}: {reason}" if reason.startswith("quality gate")
                        else f"Delivery-run {rid} {reason}")
    return gaps

# --- acknowledgment parsing --------------------------------------------------

def _parse_acknowledgment(text: str) -> tuple[list[str], list[str], list[str], list[str]]:
    """Structural parse → ``(covers, run_ids, claim_ids, missing)`` (F7/R4): a
    ``Scope:`` line, a ``C-<n>`` ref or ``no research claims promoted``, a
    ``Covers:`` section of ``- `` prefixes, and >=1 ``Delivery-run:`` id. Any
    gap → empty covers/run_ids (downgrades nothing) plus what is absent."""
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
    try:  # lazy: the ledger-check half imports this module, so import it here
        import check_research_evidence as cre
    except ModuleNotFoundError:
        from scripts import check_research_evidence as cre
    ledger = repo_root / rl.LEDGER_REL
    records = rl.load_research_records(ledger)
    if not records:
        return set()
    findings = cre.check_ledger(records, repo_root, ledger)
    ids = {r["claim_id"] for r in records if r.get("record_type") == rl.CLAIM and r.get("claim_id")}
    return {cid for cid in ids if not any(cid in f for f in findings)}

# --- reviewed-file digest binding (Q3b) --------------------------------------

def _disk_digest(repo_root: Path, path: str) -> str | None:
    """sha256 of ``path`` on disk (working-tree/default HEAD-side resolver), or
    ``None`` when absent. A symlink hashes its readlink TARGET STRING, matching
    ``agent_run``'s recorder and git's own blob content for a symlink."""
    absolute = repo_root / path
    if absolute.is_symlink():
        return hashlib.sha256(os.readlink(absolute).encode("utf-8")).hexdigest()
    return rl.sha256_file(absolute) if absolute.is_file() else None

def _git_blob_digest(repo_root: Path, ref: str, path: str) -> str | None:
    """sha256 of ``path`` as committed at ``ref`` (``git show`` yields the raw
    blob either way — file bytes, or a symlink's readlink target string — so
    hashing ``stdout`` as-is matches ``agent_run``'s recorded digest). ``None``
    when the blob is absent there — the signal a deleted/nonexistent path uses."""
    completed = subprocess.run(["git", "-C", str(repo_root), "show", f"{ref}:{path}"], capture_output=True)
    return hashlib.sha256(completed.stdout).hexdigest() if completed.returncode == 0 else None

# --- diff evaluation ---------------------------------------------------------

def _is_mechanism_path(path: str) -> bool:
    """Q3d: acknowledgment files under ``.agents/promotions/`` and the run ledger
    are the promotion/recording MECHANISM, not promoted content, so they are
    never ``promotion-required``. Safety and symlink checks still apply below."""
    return path.startswith(PROMOTIONS_DIR) or path == rl.LEDGER_REL

def _valid_acknowledgments(
    changed_paths: list[str], repo_root: Path, notes: list[str]
) -> list[tuple[str, list[str], list[dict[str, str]]]]:
    """Parse + evidence-bind each acknowledgment in the changed set (F7/R4). A
    valid ack yields ``(ack, covers, reviewed_entries)``; an invalid one
    downgrades nothing and appends an ``invalid-acknowledgment`` note."""
    acks = [p for p in changed_paths if p.startswith(PROMOTIONS_DIR) and p.endswith(".md") and Path(p).name != "README.md"]
    if not acks:
        return []
    agent_runs = load_agent_runs(repo_root)
    valid_claims = _valid_canonical_claim_ids(repo_root)
    valid: list[tuple[str, list[str], list[dict[str, str]]]] = []
    for ack in sorted(acks):
        ack_abs = repo_root / ack
        text = ack_abs.read_text(encoding="utf-8") if ack_abs.is_file() else ""
        covers, run_ids, claim_ids, missing = _parse_acknowledgment(text)
        reasons = missing or ack_evidence_gaps(claim_ids, run_ids, valid_claims, agent_runs)
        if reasons:
            notes.append(f"invalid-acknowledgment: {ack} ({', '.join(reasons)})")
            continue
        reviewed = [e for rid in run_ids for e in agent_runs[rid].get("reviewed_files", []) if isinstance(e, dict)]
        valid.append((ack, covers, reviewed))
    return valid

def _ack_coverage(
    path: str,
    valid_acks: list[tuple[str, list[str], list[dict[str, str]]]],
    blob_digest: Callable[[str], str | None],
    base_blob_digest: Callable[[str], str | None],
) -> tuple[str | None, str | None]:
    """Coverage for one promoted ``path`` -> ``(covering ack, stale note)``. A
    LIVE path needs a non-tombstone entry whose sha256 matches the head blob;
    a DELETED one (no head blob, one at base) needs a tombstone entry whose
    base_sha256 matches the BASE blob — the wrong-kind entry never covers the
    other. A same-kind entry with a drifted digest yields a stale note."""
    head_digest = blob_digest(path)
    deleted = head_digest is None and base_blob_digest(path) is not None
    current = base_blob_digest(path) if deleted else head_digest
    stale: str | None = None
    for ack, covers, reviewed in valid_acks:
        if not any(path.startswith(prefix) for prefix in covers):
            continue
        for entry in reviewed:
            if entry.get("path") != path or bool(entry.get("deleted")) != deleted:
                continue
            if current == (entry.get("base_sha256") if deleted else entry.get("sha256")):
                return ack, None
            stale = f"stale-tombstone: {path}" if deleted else f"stale-review: {path}"
    return None, stale

def evaluate_diff(
    changed_paths: list[str],
    repo_root: Path,
    policy: dict[str, Any],
    mode: str | None = None,
    blob_digest: Callable[[str], str | None] | None = None,
    base_blob_digest: Callable[[str], str | None] | None = None,
) -> tuple[list[str], list[str]]:
    """Boundary findings (blocking) and notes (non-blocking) for a changed-path
    set under ``mode`` (see the module docstring). ``blob_digest`` resolves the
    diff-head sha256 of a path (defaults to the working-tree disk hash);
    ``base_blob_digest`` resolves its BASE-side sha256 for deletion-tombstone
    matching (defaults to "unknown", so callers that never exercise deletions
    are unaffected)."""
    if blob_digest is None:
        blob_digest = lambda p: _disk_digest(repo_root, p)
    if base_blob_digest is None:
        base_blob_digest = lambda p: None
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
    valid_acks = _valid_acknowledgments(changed_paths, repo_root, notes)

    for path in sorted(changed_paths):
        if promote_delivery and modes[path] == "delivery" and not _is_mechanism_path(path):
            cover, stale = _ack_coverage(path, valid_acks, blob_digest, base_blob_digest)
            if cover:
                notes.append(f"promotion acknowledged: {cover} covers {path}")
            else:
                if stale:
                    notes.append(stale)
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

# --- changed-path sources + runners ------------------------------------------

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

def _finish(
    changed_paths: list[str],
    repo_root: Path,
    policy: dict[str, Any],
    mode: str | None,
    pre_notes: list[str],
    blob_digest: Callable[[str], str | None] | None = None,
    base_blob_digest: Callable[[str], str | None] | None = None,
) -> int:
    findings, notes = evaluate_diff(changed_paths, repo_root, policy, mode, blob_digest, base_blob_digest)
    for note in pre_notes + notes:
        print(f"NOTE {note}")
    return _emit(findings, f"{len(changed_paths)} changed path(s)")

def run_diff_mode(diff_range: str, policy_path: Path, repo_root: Path, mode: str | None = None) -> int:
    # F6: judge under the BASE policy so a head-side edit cannot weaken its own gate.
    changed_paths = changed_paths_from_range(repo_root, diff_range)
    pre_notes: list[str] = []
    base = base_ref_of_range(diff_range)
    try:
        policy = load_base_policy(repo_root, base)
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
    head = head_ref_of_range(diff_range)
    return _finish(changed_paths, repo_root, policy, mode, pre_notes,
                   lambda p: _git_blob_digest(repo_root, head, p),
                   lambda p: _git_blob_digest(repo_root, base, p))

def run_working_tree_mode(policy_path: Path, repo_root: Path, mode: str | None = None) -> int:
    """F1: same findings/notes/ack logic as diff mode, but over the working tree
    and the checked-out policy; reviewed_files digests hash the file on disk,
    against a HEAD-committed base (so an uncommitted delete can tombstone)."""
    try:
        policy = load_policy(policy_path)
    except FileNotFoundError as exc:
        return _usage(str(exc))
    changed_paths = changed_paths_from_working_tree(repo_root)
    return _finish(changed_paths, repo_root, policy, mode, ["policy-source: working tree"],
                   base_blob_digest=lambda p: _git_blob_digest(repo_root, "HEAD", p))
