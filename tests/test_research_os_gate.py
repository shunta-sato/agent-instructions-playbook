"""Boundary-gate tests for the Research OS diff-range and working-tree modes.
Covers ``evaluate_diff``/``run_diff_mode``/``run_working_tree_mode``:
promotion, safety, symlink-boundary, declared-mode binding, the
promotion-acknowledgment downgrade (F7), rename-origin evaluation (G2), and
working-tree mode (F1). Base-policy binding (F6) and a real-git deletion
tombstone (c) live in the sibling ``test_research_os_round8`` (400-line
overflow); G1 (range-bound declared-mode selector) tests live in
``test_research_os_mode``; ledger/runner/claim tests live in
``test_research_os.py``; CI/Makefile wiring tests (including G4's
unit-test-before-boundary-gate ordering) live in ``test_ci_wiring``."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import check_research_evidence as cre
from tests.test_research_os_ack import ACK, POLICY as ACK_POLICY, _run, _sha256, _write_ack, _write_canonical_ledger


def _capture(fn, *args) -> tuple[int, str]:
    """Run ``fn(*args)``, returning (exit code, captured stdout)."""
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*args)
    return rc, buf.getvalue()


def _git_init(root: Path) -> None:
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def _commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", message], check=True, capture_output=True)


# --- (D) promotion boundary --------------------------------------------------


class PromotionTests(unittest.TestCase):
    POLICY = {"path_modes": {"experiments/": "research"}, "safety_paths": []}

    def test_unmatched_path_under_research_declaration_requires_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = cre.evaluate_diff(["experiments/e1/run.py", "src/app.py"], Path(tmp), self.POLICY)
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertNotIn("promotion-required: experiments/e1/run.py", findings)

    def test_research_only_diff_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, notes = cre.evaluate_diff(["experiments/e1/run.py"], Path(tmp), self.POLICY)
        self.assertEqual(findings, [])
        self.assertEqual(notes, [])


# --- (E) safety orthogonality ------------------------------------------------


class SafetyTests(unittest.TestCase):
    def test_safety_path_flagged_in_delivery_mode(self) -> None:
        policy = {"path_modes": {}, "safety_paths": ["SECURITY/"]}
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = cre.evaluate_diff(["SECURITY/policy.md"], Path(tmp), policy)
        self.assertIn("safety-review-required: SECURITY/policy.md", findings)

    def test_safety_path_flagged_in_research_mode(self) -> None:
        policy = {"path_modes": {"SECURITY/": "research"}, "safety_paths": ["SECURITY/"]}
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = cre.evaluate_diff(["SECURITY/keys.md"], Path(tmp), policy)
        self.assertIn("safety-review-required: SECURITY/keys.md", findings)

    def test_symlink_crossing_boundary_flagged(self) -> None:
        policy = {"path_modes": {"experiments/": "research", "src/": "delivery"}, "safety_paths": []}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "real.py").write_text("x\n", encoding="utf-8")
            (root / "experiments").mkdir()
            link = root / "experiments" / "link.py"
            link.symlink_to(root / "src" / "real.py")
            findings, _ = cre.evaluate_diff(["experiments/link.py"], root, policy)
        self.assertIn("symlink-boundary: experiments/link.py", findings)


# --- (S2) declared-mode boundary binding -------------------------------------


class ModeBindingTests(unittest.TestCase):
    POLICY = {"path_modes": {"experiments/": "research"}, "safety_paths": ["SECURITY/"]}

    def test_research_mode_flags_delivery_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = cre.evaluate_diff(["src/app.py"], Path(tmp), self.POLICY, "research")
        self.assertIn("promotion-required: src/app.py", findings)

    def test_delivery_mode_research_path_is_note_only(self) -> None:
        # A delivery-mode edit to a research path is legitimate: no finding, just a reminder note.
        with tempfile.TemporaryDirectory() as tmp:
            findings, notes = cre.evaluate_diff(["experiments/e1/run.py"], Path(tmp), self.POLICY, "delivery")
        self.assertEqual(findings, [])
        self.assertIn("mode: delivery-mode change under research path experiments/e1/run.py"
                       " — claims discipline still applies", notes)

    def test_no_mode_mixing_requires_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = cre.evaluate_diff(["experiments/e1/run.py", "src/app.py"], Path(tmp), self.POLICY, None)
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertNotIn("promotion-required: experiments/e1/run.py", findings)

    def test_safety_evaluated_in_every_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ("research", "delivery", None):
                findings, _ = cre.evaluate_diff(["SECURITY/p.md"], Path(tmp), self.POLICY, mode)
                self.assertIn("safety-review-required: SECURITY/p.md", findings)


# --- (S5) ack evidence-BINDING (mock ledgers) lives in test_research_os_ack;
# the real-git ``run_diff_mode`` end-to-end proofs for it live here. --------


def _ack_repo(tmp: str) -> tuple[Path, Path]:
    root = Path(tmp)
    _git_init(root)
    policy = root / "policy.json"
    policy.write_text(json.dumps(ACK_POLICY), encoding="utf-8")
    return root, policy


class AckSymlinkHeadBlobTests(unittest.TestCase):
    """Q3b follow-up: ``--diff-range`` hashes the ``git show <head>:<path>``
    blob, which for a symlink IS its readlink target string."""

    def _repo_with_committed_symlink(self, tmp: str, reviewed_sha256: str) -> tuple[Path, Path]:
        root, policy = _ack_repo(tmp)
        _write_canonical_ledger(root, [_run(
            "run-1", changed=[], allowed=[], reviewed=[{"path": "link", "sha256": reviewed_sha256, "mode": "120000"}],
        )])
        _commit_all(root, "base")
        (root / "target_dir").mkdir()
        (root / "link").symlink_to("target_dir")  # tracked symlink to a DIRECTORY
        _write_ack(root, ACK, covers=["link", ".agents/promotions/"], run_ids=["run-1"])
        _commit_all(root, "promote")
        return root, policy

    def test_matching_symlink_digest_downgrades_at_head(self) -> None:
        correct = hashlib.sha256(b"target_dir").hexdigest()  # readlink target, no newline
        with tempfile.TemporaryDirectory() as tmp:
            root, policy = self._repo_with_committed_symlink(tmp, correct)
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy, root, "research")
        self.assertEqual(rc, 0)
        self.assertIn(f"NOTE promotion acknowledged: {ACK} covers link", output)

    def test_mismatched_symlink_digest_stays_blocking_and_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, policy = self._repo_with_committed_symlink(tmp, "0" * 64)  # recorded digest drifted
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy, root, "research")
        self.assertEqual(rc, 1)
        self.assertIn("FINDING promotion-required: link", output)
        self.assertIn("NOTE stale-review: link", output)


class AckDiffModeTests(unittest.TestCase):
    """R4 end-to-end through ``run_diff_mode`` over a real git range."""

    def test_changed_files_citation_of_a_later_edit_stays_blocking(self) -> None:
        # B3: run-1 saw "x\n"; promote LATER edits to "y\n" — a changed_files listing alone must not bless this.
        with tempfile.TemporaryDirectory() as tmp:
            root, policy = _ack_repo(tmp)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("x\n", encoding="utf-8")
            _write_canonical_ledger(root, [_run("run-1", changed=["src/app.py"], allowed=["src/", ".agents/promotions/"])])
            _commit_all(root, "base")
            (root / "src" / "app.py").write_text("y\n", encoding="utf-8")
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"])
            _commit_all(root, "promote")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy, root, "research")
        self.assertEqual(rc, 1)
        self.assertIn("FINDING promotion-required: src/app.py", output)

    def test_reviewed_digest_of_final_content_exits_zero(self) -> None:  # a run reviewing the FINAL content covers
        with tempfile.TemporaryDirectory() as tmp:
            root, policy = _ack_repo(tmp)
            (root / "src").mkdir()
            app = root / "src" / "app.py"
            app.write_text("x\n", encoding="utf-8")
            _commit_all(root, "base")
            app.write_text("y\n", encoding="utf-8")
            run = _run("run-1", changed=["src/app.py"], allowed=["src/app.py", ".agents/promotions/"],
                       reviewed=[{"path": "src/app.py", "sha256": _sha256(app), "mode": "100644"}])
            _write_canonical_ledger(root, [run])
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"])
            _commit_all(root, "promote")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy, root, "research")
        self.assertEqual(rc, 0)
        self.assertIn(f"NOTE promotion acknowledged: {ACK} covers src/app.py", output)


# --- (c) real-git deletion tombstone coverage lives in ``test_research_os_round8`` (400-line-capped sibling) ---


# --- (S5) end-to-end exit codes through run_diff_mode ------------------------


class DiffModeExitCodeTests(unittest.TestCase):
    POLICY = {"path_modes": {"experiments/": "research", "research/": "research"}, "safety_paths": []}

    def _repo(self, tmp: str) -> tuple[Path, Path]:
        root = Path(tmp)
        _git_init(root)
        policy_path = root / "policy.json"
        policy_path.write_text(json.dumps(self.POLICY), encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "app.py").write_text("x\n", encoding="utf-8")
        (root / "research").mkdir()
        (root / "research" / "note.md").write_text("r\n", encoding="utf-8")
        _commit_all(root, "base")
        return root, policy_path

    def test_promotion_without_ack_exits_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = self._repo(tmp)
            (root / "src" / "app.py").write_text("y\n", encoding="utf-8")
            _commit_all(root, "change")
            rc = cre.run_diff_mode("HEAD~1..HEAD", policy_path, root, "research")
        self.assertEqual(rc, 1)

    def test_delivery_mode_research_edit_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = self._repo(tmp)
            (root / "research" / "note.md").write_text("changed\n", encoding="utf-8")
            _commit_all(root, "research-edit")
            rc = cre.run_diff_mode("HEAD~1..HEAD", policy_path, root, "delivery")
        self.assertEqual(rc, 0)


# --- (F6) base-policy binding lives in ``test_research_os_round8`` (400-line-capped sibling) ---

# --- (F1) working-tree mode ---------------------------------------------------


class WorkingTreeModeTests(unittest.TestCase):
    """F1: a skill can invoke the gate with a declared mode before committing."""

    def test_research_mode_working_tree_delivery_edit_requires_promotion(self) -> None:
        policy = {"path_modes": {"experiments/": "research"}, "safety_paths": []}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("x\n", encoding="utf-8")
            _commit_all(root, "base")
            (root / "src" / "app.py").write_text("y\n", encoding="utf-8")  # unstaged, uncommitted
            policy_path = root / "policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")
            rc, output = _capture(cre.run_working_tree_mode, policy_path, root, "research")
        self.assertEqual(rc, 1)
        self.assertIn("FINDING promotion-required: src/app.py", output)
        self.assertIn("NOTE policy-source: working tree", output)

    def test_changed_paths_from_working_tree_includes_untracked_excludes_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
            _commit_all(root, "base")
            (root / "new.py").write_text("v\n", encoding="utf-8")  # untracked
            (root / "ignored.txt").write_text("v\n", encoding="utf-8")  # untracked, ignored
            paths = cre.changed_paths_from_working_tree(root)
        self.assertIn("new.py", paths)
        self.assertNotIn("ignored.txt", paths)


# --- (G2) rename ORIGINS must still be evaluated -------------------------------


class RenameOriginTests(unittest.TestCase):
    """G2: the reviewer's repro — ``experiments/probe.py -> runtime/probe.py``
    (a research-path origin moved to delivery) and ``SECURITY/a -> docs/a``
    (a safety-path origin moved out) — must not bypass the gate just because
    ``--name-only``/porcelain collapses a rename to its destination alone."""

    POLICY = {"path_modes": {"experiments/": "research"}, "safety_paths": ["SECURITY/"]}

    def _repo(self, tmp: str) -> Path:
        root = Path(tmp)
        _git_init(root)
        (root / "experiments").mkdir()
        (root / "experiments" / "probe.py").write_text("p\n", encoding="utf-8")
        (root / "SECURITY").mkdir()
        (root / "SECURITY" / "a").write_text("s\n", encoding="utf-8")
        (root / ".agents").mkdir()
        (root / ".agents" / "project-policy.yml").write_text(json.dumps(self.POLICY), encoding="utf-8")
        _commit_all(root, "base")
        return root

    def test_rename_origins_evaluated_via_diff_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            (root / "runtime").mkdir()
            (root / "docs").mkdir()
            subprocess.run(["git", "-C", str(root), "mv", "experiments/probe.py", "runtime/probe.py"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "mv", "SECURITY/a", "docs/a"], check=True, capture_output=True)
            _commit_all(root, "rename")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", root / ".agents" / "project-policy.yml", root)  # no --mode
        self.assertEqual(rc, 1)
        self.assertIn("FINDING safety-review-required: SECURITY/a", output)
        self.assertIn("FINDING promotion-required: runtime/probe.py", output)

    def test_rename_origins_evaluated_via_working_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo(tmp)
            (root / "runtime").mkdir()
            (root / "docs").mkdir()
            subprocess.run(["git", "-C", str(root), "mv", "experiments/probe.py", "runtime/probe.py"], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(root), "mv", "SECURITY/a", "docs/a"], check=True, capture_output=True)
            rc, output = _capture(cre.run_working_tree_mode, root / ".agents" / "project-policy.yml", root, None)
        self.assertEqual(rc, 1)
        self.assertIn("FINDING safety-review-required: SECURITY/a", output)
        self.assertIn("FINDING promotion-required: runtime/probe.py", output)


if __name__ == "__main__":
    unittest.main()
