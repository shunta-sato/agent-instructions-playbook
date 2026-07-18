#!/usr/bin/env python3
"""Boundary-gate half of the Research OS evidence checker (ledger-chain half + CLI in
``check_research_evidence``, split for the structure budget). Evaluates a changed-path set under a
declared/derived mode for promotion, symlink, and safety findings; binds acknowledgments to ``agent_run``
evidence (R4) whose own outcome re-derives. Coverage needs (digest, git-mode) identity: LIVE at HEAD, DELETED
via a tombstone at the RANGE BASE (M2/M5). A CI diff with no ``--mode`` selects the effective mode from
declared_mode run records NEW IN THE RANGE — STRICTEST WINS on mixed values (research if any, with a NOTE,
never a block) — falling back to policy-derived research-effectiveness and failing closed without one (M1/G1)."""

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
QUALITY_GATE_PASS = ("pass", "submit")  # Q3c: Delivery-run evidence needs an explicit passing gate.

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
    """Left ref of ``A..B``/``A...B``, trailing dots stripped (F6 base)."""
    return diff_range.split("..", 1)[0].rstrip(".")

def head_ref_of_range(diff_range: str) -> str:
    """Right ref of ``A..B``/``A...B`` — reviewed_files verify against this (Q3b)."""
    return re.split(r"\.\.\.?", diff_range)[-1] or "HEAD"

def load_base_policy(repo_root: Path, base_ref: str) -> dict[str, Any] | None:
    """The policy committed at ``base_ref``; ``None`` when absent there."""
    completed = subprocess.run(["git", "-C", str(repo_root), "show", f"{base_ref}:{POLICY_REL}"], capture_output=True, text=True)
    return _parse_policy(completed.stdout) if completed.returncode == 0 else None

def resolve_mode(path: str, path_modes: dict[str, str], default_mode: str) -> str:
    """Longest-prefix match; unmatched paths resolve to ``default_mode`` (M1)."""
    best_prefix, best_mode = "", default_mode
    for prefix, mode in path_modes.items():
        if (path == prefix or path.startswith(prefix)) and len(prefix) >= len(best_prefix):
            best_prefix, best_mode = prefix, mode
    return best_mode

# --- agent-run evidence (R4 / Q3) --------------------------------------------

def _parse_agent_runs(text: str) -> dict[str, dict[str, Any]]:
    runs: dict[str, dict[str, Any]] = {}
    for raw in text.splitlines():
        if not raw.strip():
            continue
        try:
            rec = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(rec, dict) and rec.get("record_type") == AGENT_RUN and rec.get("run_id"):
            runs[rec["run_id"]] = rec
    return runs

def load_agent_runs(repo_root: Path) -> dict[str, dict[str, Any]]:
    """Canonical ``agent_run`` records indexed by run_id (empty if absent)."""
    path = repo_root / rl.LEDGER_REL
    return _parse_agent_runs(path.read_text(encoding="utf-8")) if path.is_file() else {}

def agent_runs_at_ref(repo_root: Path, ref: str) -> dict[str, dict[str, Any]]:
    """G1: ``agent_run`` records at an arbitrary ref (empty when the ledger is absent there)."""
    completed = subprocess.run(["git", "-C", str(repo_root), "show", f"{ref}:{rl.LEDGER_REL}"], capture_output=True, text=True)
    return _parse_agent_runs(completed.stdout) if completed.returncode == 0 else {}

def new_declared_modes(repo_root: Path, head: str, base: str) -> set[str]:
    """G1: declared_mode values NEW in the range (by run_id, present at head/absent at base) — stale/base declarations never count."""
    head_runs, base_ids = agent_runs_at_ref(repo_root, head), set(agent_runs_at_ref(repo_root, base).keys())
    return {rec["declared_mode"] for run_id, rec in head_runs.items() if run_id not in base_ids and rec.get("declared_mode") in ("research", "delivery")}

def _run_is_delivery_evidence(run: dict[str, Any]) -> tuple[bool, str]:
    """Q3c: passing validation commands + a passing quality gate + re-derived acceptance."""
    validation = run.get("validation")
    if not isinstance(validation, dict) or not ar.validation_passed(validation):
        return False, "did not pass validation"
    gate = str(validation.get("quality_gate", "")).strip().lower()
    if gate not in QUALITY_GATE_PASS:
        return False, "quality gate not recorded as pass"
    if ar.evaluate_run_record(run)["accepted"] is not True:
        return False, "run outcome was not accepted"
    return True, ""

def ack_evidence_gaps(claim_ids: list[str], run_ids: list[str], valid_claims: set[str], runs: dict[str, dict[str, Any]]) -> list[str]:
    """R4.1/R4.2: reasons an acknowledgment fails to bind to ledger evidence."""
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
    """Structural parse -> ``(covers, run_ids, claim_ids, missing)`` (F7/R4)."""
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
        (has_scope, "Scope:"), (has_claim, "claim ref or 'no research claims promoted'"),
        (bool(covers), "Covers: prefixes"), (bool(run_ids), "Delivery-run: run_ids"),
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

# --- reviewed-file identity binding (Q3b / M2) --------------------------------

def _disk_identity(repo_root: Path, path: str) -> tuple[str | None, str | None]:
    """(sha256, git-mode) on disk; a symlink hashes its readlink TARGET STRING at mode 120000."""
    absolute = repo_root / path
    if absolute.is_symlink():
        return hashlib.sha256(os.readlink(absolute).encode("utf-8")).hexdigest(), "120000"
    if absolute.is_file():
        return rl.sha256_file(absolute), "100755" if os.access(absolute, os.X_OK) else "100644"
    return None, None

def _git_identity(repo_root: Path, ref: str, path: str) -> tuple[str | None, str | None]:
    """(sha256, git-mode) of ``path`` at ``ref``; ``(None, None)`` when absent there."""
    tree = subprocess.run(["git", "-C", str(repo_root), "ls-tree", ref, "--", path], capture_output=True, text=True).stdout.strip()
    if not tree:
        return None, None
    blob = subprocess.run(["git", "-C", str(repo_root), "show", f"{ref}:{path}"], capture_output=True).stdout
    return hashlib.sha256(blob).hexdigest(), tree.split()[0]

# --- diff evaluation ---------------------------------------------------------

def _is_mechanism_path(path: str) -> bool:
    """Q3d: ack files + the run ledger are the promotion MECHANISM, never ``promotion-required``."""
    return path.startswith(PROMOTIONS_DIR) or path == rl.LEDGER_REL

def _valid_acknowledgments(changed_paths: list[str], repo_root: Path, notes: list[str]) -> list[tuple[str, list[str], list[dict[str, str]]]]:
    """Parse + evidence-bind each acknowledgment in the changed set (F7/R4)."""
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

def _ack_coverage(path: str, valid_acks: list[tuple[str, list[str], list[dict[str, str]]]],
                   identity: Callable[[str], tuple[str | None, str | None]],
                   base_identity: Callable[[str], tuple[str | None, str | None]]) -> tuple[str | None, list[str]]:
    """Coverage for ``path`` -> ``(covering ack, extra notes)``: LIVE needs a (digest, mode) match at HEAD,
    DELETED a tombstone match at the RANGE BASE (wrong-kind never covers the other); G3: a mode-less entry
    never covers — no grandfather path."""
    head_digest, head_mode = identity(path)
    base_digest, base_mode = base_identity(path)
    deleted = head_digest is None and base_digest is not None
    current_digest, current_mode = (base_digest, base_mode) if deleted else (head_digest, head_mode)
    mismatch_note = f"tombstone-base-mismatch: {path} (record a tombstone against the range base)" if deleted else f"stale-review: {path}"
    notes: list[str] = []
    for ack, covers, reviewed in valid_acks:
        if not any(path.startswith(prefix) for prefix in covers):
            continue
        for entry in reviewed:
            if entry.get("path") != path or bool(entry.get("deleted")) != deleted:
                continue
            entry_mode = entry.get("mode")
            if entry_mode is None:
                notes.append(f"unbound-mode: {path} (mode-less reviewed entry never covers)")
                continue
            entry_digest = entry.get("base_sha256") if deleted else entry.get("sha256")
            if current_digest != entry_digest or entry_mode != current_mode:
                notes.append(mismatch_note)
                continue
            return ack, notes
    return None, notes

def evaluate_diff(changed_paths: list[str], repo_root: Path, policy: dict[str, Any], mode: str | None = None,
                   identity: Callable[[str], tuple[str | None, str | None]] | None = None,
                   base_identity: Callable[[str], tuple[str | None, str | None]] | None = None,
                   ) -> tuple[list[str], list[str]]:
    """Boundary findings (blocking) + notes (non-blocking) under ``mode``; ``identity``/``base_identity`` resolve (sha256, git-mode) at head/base."""
    if identity is None:
        identity = lambda p: _disk_identity(repo_root, p)
    if base_identity is None:
        base_identity = lambda p: (None, None)
    path_modes = policy.get("path_modes", {}) or {}
    default_mode = policy.get("default_mode", "delivery")
    safety_paths = policy.get("safety_paths", []) or []
    modes = {path: resolve_mode(path, path_modes, default_mode) for path in changed_paths}

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
            cover, cov_notes = _ack_coverage(path, valid_acks, identity, base_identity)
            if cover:
                notes.append(f"promotion acknowledged: {cover} covers {path}")
                notes.extend(cov_notes)
            else:
                notes.extend(cov_notes)
                findings.append(f"promotion-required: {path}")
        if mode == "delivery" and modes[path] == "research":
            notes.append(f"mode: delivery-mode change under research path {path} — claims discipline still applies")

        absolute = repo_root / path
        if absolute.is_symlink():
            try:
                target_rel = Path(os.path.realpath(absolute)).resolve().relative_to(repo_root.resolve()).as_posix()
                target_mode = resolve_mode(target_rel, path_modes, default_mode)
            except ValueError:
                target_mode = "delivery"
            if modes[path] == "research" or target_mode != modes[path]:
                findings.append(f"symlink-boundary: {path}")

        if any(path == prefix or path.startswith(prefix) for prefix in safety_paths):
            findings.append(f"safety-review-required: {path}")
    return findings, notes

# --- changed-path sources + runners ------------------------------------------

def _git_output_z(repo_root: Path, *args: str) -> list[str]:
    """M3: NUL-delimited git output, decoded raw (no C-quote stripping)."""
    out = subprocess.run(
        ["git", "-C", str(repo_root), "-c", "core.quotepath=false", *args],
        check=True, capture_output=True,
    ).stdout
    return [p.decode("utf-8", "surrogateescape") for p in out.split(b"\0") if p]

def changed_paths_from_range(repo_root: Path, diff_range: str) -> list[str]:
    """G2: ``--no-renames`` so a rename's ORIGIN appears as its own (deleted) path, not collapsed into the
    destination alone — a research-path or safety-path origin must still be evaluated."""
    return _git_output_z(repo_root, "diff", "--no-renames", "--name-only", "-z", diff_range)

def changed_paths_from_working_tree(repo_root: Path) -> list[str]:
    """F1/M3/G2: staged+unstaged+untracked paths (porcelain -z; a rename/copy's second bare token is the ORIG_PATH
    — kept, not skipped, so the origin is evaluated same as the destination). ``--untracked-files=all`` lists a
    file inside a brand-new untracked DIRECTORY individually, not collapsed to the directory's own path."""
    paths: list[str] = []
    skip_next = False
    for token in _git_output_z(repo_root, "status", "--porcelain", "-z", "--untracked-files=all"):
        if skip_next:
            paths.append(token)  # G2: rename/copy ORIG_PATH
            skip_next = False
            continue
        status, path = token[:2], token[3:]
        paths.append(path)
        skip_next = "R" in status or "C" in status
    return paths

def _finish(changed_paths: list[str], repo_root: Path, policy: dict[str, Any], mode: str | None, pre_notes: list[str],
            identity: Callable[[str], tuple[str | None, str | None]] | None = None,
            base_identity: Callable[[str], tuple[str | None, str | None]] | None = None,
            extra_findings: list[str] | None = None) -> int:
    findings, notes = evaluate_diff(changed_paths, repo_root, policy, mode, identity, base_identity)
    findings = list(extra_findings or []) + findings
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

    # M1/G1: CI (no --mode) selects the effective mode from declarations NEW IN THE RANGE first,
    # falling back to path/default research-effectiveness only when there are none.
    default_mode = policy.get("default_mode", "delivery")
    path_modes = policy.get("path_modes", {}) or {}
    research_effective = default_mode == "research" or any(resolve_mode(p, path_modes, default_mode) == "research" for p in changed_paths)
    effective_mode, extra_findings = mode, []
    if mode is None:
        declarations = new_declared_modes(repo_root, head, base)
        if len(declarations) > 1:
            # G1: mixing per-task delivery declarations with a change-level research one is
            # normal multi-agent shape, not a conflict. STRICTEST WINS below: ambiguity only
            # ever resolves toward MORE gating — a later delivery declaration cannot downgrade.
            pre_notes.append(f"mode-declarations: {', '.join(sorted(declarations))}")
        if declarations:
            effective_mode = "research" if "research" in declarations else "delivery"
        elif research_effective:
            effective_mode = "research"
            extra_findings.append("mode-undeclared: research-effective diff has no declared_mode: research run record")

    return _finish(changed_paths, repo_root, policy, effective_mode, pre_notes,
                   lambda p: _git_identity(repo_root, head, p), lambda p: _git_identity(repo_root, base, p),
                   extra_findings=extra_findings)

def run_working_tree_mode(policy_path: Path, repo_root: Path, mode: str | None = None) -> int:
    """F1: same findings/notes/ack logic as diff mode, over the working tree."""
    try:
        policy = load_policy(policy_path)
    except FileNotFoundError as exc:
        return _usage(str(exc))
    changed_paths = changed_paths_from_working_tree(repo_root)
    return _finish(changed_paths, repo_root, policy, mode, ["policy-source: working tree"],
                   base_identity=lambda p: _git_identity(repo_root, "HEAD", p))
