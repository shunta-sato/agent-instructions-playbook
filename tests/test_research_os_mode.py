"""Round-7 real-git tests for the boundary gate that don't fit the
400-line-capped siblings: M1 (CI research-effectiveness + declared_mode
fail-closed), M3 (NUL-delimited special-filename parsing), and M5 (deletion
tombstones must bind to the PR RANGE BASE, not a later HEAD). Mock-ledger
identity/coverage tests for the same fixes live in ``test_research_os_ack``;
promotion/safety/symlink/base-policy tests live in ``test_research_os_gate``."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import check_research_evidence as cre
from tests.test_research_os_ack import ACK, _run, _write_ack, _write_canonical_ledger
from tests.test_research_os_gate import _capture, _commit_all, _git_init


def _ack_repo(tmp: str) -> tuple[Path, Path]:
    root = Path(tmp)
    _git_init(root)
    policy = root / "policy.json"
    policy.write_text(json.dumps({"path_modes": {"experiments/": "research"}, "safety_paths": ["SECURITY/"]}),
                       encoding="utf-8")
    return root, policy


class ModeUndeclaredTests(unittest.TestCase):
    """M1: CI (no --mode) derives research-effectiveness from the policy and
    fails closed without a ledger ``declared_mode: research`` record."""

    POLICY = {"default_mode": "research", "path_modes": {}, "safety_paths": []}

    def _repo(self, tmp: str, policy: dict) -> tuple[Path, Path]:
        root = Path(tmp)
        _git_init(root)
        policy_path = root / "policy.json"
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        (root / "src").mkdir()
        (root / "src" / "app.py").write_text("x\n", encoding="utf-8")
        _commit_all(root, "base")
        return root, policy_path

    def test_default_mode_research_resolves_unmatched_path_as_research(self) -> None:
        # Repro: default_mode=research, path_modes={} -> unmatched path resolves research (M1).
        self.assertEqual(cre.resolve_mode("src/app.py", {}, "research"), "research")
        self.assertEqual(cre.resolve_mode("src/app.py", {}, "delivery"), "delivery")

    def test_research_effective_diff_with_no_declared_mode_record_fails_closed(self) -> None:
        # Repro to defeat (M1): this must no longer silently pass in the CI path.
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = self._repo(tmp, self.POLICY)
            (root / "src" / "app.py").write_text("y\n", encoding="utf-8")
            _commit_all(root, "change")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy_path, root)  # no --mode
        self.assertEqual(rc, 1)
        self.assertIn("FINDING mode-undeclared:", output)

    def test_declared_mode_record_present_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = self._repo(tmp, self.POLICY)
            (root / "src" / "app.py").write_text("y\n", encoding="utf-8")
            declared = _run("declare-1")
            declared["declared_mode"] = "research"
            _write_canonical_ledger(root, [declared])
            _commit_all(root, "change")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy_path, root)
        self.assertEqual(rc, 0)
        self.assertNotIn("mode-undeclared", output)

    def test_declared_mode_and_promotion_ack_together_pass(self) -> None:
        # A research-effective change with a delivery-mode path needs BOTH a
        # declared_mode record AND ack-covered promotion to pass (M1 + F7).
        policy = {"default_mode": "research", "path_modes": {"src/": "delivery"}, "safety_paths": []}
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = self._repo(tmp, policy)
            app = root / "src" / "app.py"
            app.write_text("y\n", encoding="utf-8")
            digest = hashlib.sha256(b"y\n").hexdigest()
            run = _run("run-1", changed=["src/app.py"], allowed=["src/app.py", ".agents/promotions/"],
                       reviewed=[{"path": "src/app.py", "sha256": digest, "mode": "100644"}])
            declared = _run("declare-1")
            declared["declared_mode"] = "research"
            _write_canonical_ledger(root, [run, declared])
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"])
            _commit_all(root, "change")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy_path, root)
        self.assertEqual(rc, 0, output)
        self.assertNotIn("mode-undeclared", output)

    def test_undeclared_and_uncovered_both_fire_together(self) -> None:
        policy = {"default_mode": "research", "path_modes": {"src/": "delivery"}, "safety_paths": []}
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = self._repo(tmp, policy)
            (root / "src" / "app.py").write_text("y\n", encoding="utf-8")
            _commit_all(root, "change")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy_path, root)
        self.assertEqual(rc, 1)
        self.assertIn("FINDING mode-undeclared:", output)
        self.assertIn("FINDING promotion-required: src/app.py", output)


class RangeBoundDeclarationTests(unittest.TestCase):
    """G1: the effective mode is selected from declared_mode run records NEW
    IN THE RANGE (present by run_id at head, absent at base) — a stale/base
    declaration never counts, and multiple distinct new declarations (normal
    multi-agent shape, not a conflict) resolve STRICTEST WINS: research if any."""

    POLICY = {"path_modes": {"experiments/": "research"}, "safety_paths": ["SECURITY/"]}

    def _repo(self, tmp: str) -> tuple[Path, Path]:
        root, policy_path = _ack_repo(tmp)
        (root / "src").mkdir()
        (root / "src" / "app.py").write_text("x\n", encoding="utf-8")
        (root / "experiments").mkdir()
        (root / "experiments" / "run.py").write_text("e\n", encoding="utf-8")
        _commit_all(root, "base")
        return root, policy_path

    def test_current_research_declaration_forces_promotion_on_delivery_only_diff(self) -> None:
        # Case 1: a research declaration NEW in the range is the effective
        # mode even though the diff itself never touches a research path.
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = self._repo(tmp)
            (root / "src" / "app.py").write_text("y\n", encoding="utf-8")
            declared = _run("declare-1")
            declared["declared_mode"] = "research"
            _write_canonical_ledger(root, [declared])
            _commit_all(root, "change")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy_path, root)  # no --mode
        self.assertEqual(rc, 1)
        self.assertIn("FINDING promotion-required: src/app.py", output)
        self.assertNotIn("mode-undeclared", output)

    def test_historical_declaration_at_base_does_not_count_as_new(self) -> None:
        # Case 2: the declaration was already present at the range BASE (not
        # new), so a fresh research-path diff still fails closed.
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = self._repo(tmp)
            declared = _run("declare-1")
            declared["declared_mode"] = "research"
            _write_canonical_ledger(root, [declared])
            _commit_all(root, "base-declared")
            (root / "experiments" / "run.py").write_text("e2\n", encoding="utf-8")
            _commit_all(root, "change")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy_path, root)
        self.assertEqual(rc, 1)
        self.assertIn("FINDING mode-undeclared:", output)

    def test_new_delivery_declaration_is_consumed_as_standard_delivery(self) -> None:
        # Case 3: a NEW delivery declaration IS the effective mode — a
        # research-path touch stays a note, not a promotion-required finding.
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = self._repo(tmp)
            (root / "experiments" / "run.py").write_text("e2\n", encoding="utf-8")
            declared = _run("declare-1")
            declared["declared_mode"] = "delivery"
            _write_canonical_ledger(root, [declared])
            _commit_all(root, "change")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy_path, root)
        self.assertEqual(rc, 0, output)
        self.assertNotIn("mode-undeclared", output)
        self.assertNotIn("promotion-required", output)
        self.assertIn("delivery-mode change under research path experiments/run.py", output)

    def test_mixed_new_declarations_resolve_strict_research_with_note(self) -> None:
        # Case 4 (refined): a supervisor's change-level research declaration
        # alongside a worker's per-task delivery declaration is normal
        # multi-round shape — NOT a blocking conflict. Strictest (research)
        # wins, surfaced via a visible NOTE, and forces promotion on the
        # delivery-only diff just like the sole-research case (1).
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = self._repo(tmp)
            (root / "src" / "app.py").write_text("y\n", encoding="utf-8")
            declared_research = _run("declare-research")
            declared_research["declared_mode"] = "research"
            declared_delivery = _run("declare-delivery")
            declared_delivery["declared_mode"] = "delivery"
            _write_canonical_ledger(root, [declared_research, declared_delivery])
            _commit_all(root, "change")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy_path, root)
        self.assertEqual(rc, 1)
        self.assertNotIn("FINDING mode-conflict", output)
        self.assertIn("NOTE mode-declarations: delivery, research", output)
        self.assertIn("FINDING promotion-required: src/app.py", output)

    def test_delivery_after_research_cannot_downgrade(self) -> None:
        # A later-appended delivery declaration must not weaken an
        # already-present research one — ambiguity resolves toward MORE
        # gating, never less, regardless of ledger append order.
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = self._repo(tmp)
            (root / "src" / "app.py").write_text("y\n", encoding="utf-8")
            declared_research = _run("declare-research")
            declared_research["declared_mode"] = "research"
            declared_delivery = _run("declare-delivery-appended-later")
            declared_delivery["declared_mode"] = "delivery"
            _write_canonical_ledger(root, [declared_delivery, declared_research])  # delivery written first on disk
            _commit_all(root, "change")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy_path, root)
        self.assertEqual(rc, 1)
        self.assertIn("FINDING promotion-required: src/app.py", output)  # still research-effective, not downgraded


class SpecialFilenameSafetyTests(unittest.TestCase):
    """M3: a NUL-delimited parse matches a special (tab-containing) filename
    against a safety-path prefix; the default C-quoted form would break a
    plain-prefix match, letting the path evade the safety gate."""

    def test_tab_containing_path_matches_safety_prefix_via_diff_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = _ack_repo(tmp)
            (root / "SECURITY").mkdir()
            (root / "README.md").write_text("x\n", encoding="utf-8")
            _commit_all(root, "base")
            (root / "SECURITY" / "a\tb").write_bytes(b"s\n")
            _commit_all(root, "add special path")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy_path, root, "delivery")
        self.assertEqual(rc, 1)
        self.assertIn("FINDING safety-review-required: SECURITY/a\tb", output)

    def test_tab_containing_path_matches_safety_prefix_via_working_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = _ack_repo(tmp)
            (root / "SECURITY").mkdir()
            _commit_all(root, "base")
            (root / "SECURITY" / "a\tb").write_bytes(b"s\n")  # untracked
            rc, output = _capture(cre.run_working_tree_mode, policy_path, root, "delivery")
        self.assertEqual(rc, 1)
        self.assertIn("FINDING safety-review-required: SECURITY/a\tb", output)


class TombstoneBaseMismatchTests(unittest.TestCase):
    """M5: a deletion tombstone must be recorded against the PR RANGE BASE.
    A modify-then-delete history means a tombstone recorded against the
    intermediate (post-modify) HEAD is mechanically rejected, not silently
    treated as covering."""

    def test_tombstone_against_later_head_does_not_cover(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, policy = _ack_repo(tmp)
            (root / "src").mkdir()
            old = root / "src" / "old.py"
            old.write_text("legacy\n", encoding="utf-8")
            _commit_all(root, "base")  # <- the PR range BASE
            old.write_text("modified\n", encoding="utf-8")
            _commit_all(root, "modify")  # intermediate HEAD the recorder mistakenly cited
            later_digest = hashlib.sha256(b"modified\n").hexdigest()
            run = _run("run-1", changed=["src/old.py"], allowed=["src/old.py", ".agents/promotions/"],
                       reviewed=[{"path": "src/old.py", "deleted": True, "base_sha256": later_digest, "mode": "100644"}])
            _write_canonical_ledger(root, [run])
            old.unlink()
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"])
            _commit_all(root, "delete")
            rc, output = _capture(cre.run_diff_mode, "HEAD~2..HEAD", policy, root, "research")
        self.assertEqual(rc, 1)
        self.assertIn("FINDING promotion-required: src/old.py", output)
        self.assertIn("NOTE tombstone-base-mismatch: src/old.py", output)

    def test_tombstone_against_range_base_covers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, policy = _ack_repo(tmp)
            (root / "src").mkdir()
            old = root / "src" / "old.py"
            old.write_text("legacy\n", encoding="utf-8")
            base_digest = hashlib.sha256(b"legacy\n").hexdigest()
            _commit_all(root, "base")  # <- the PR range BASE
            old.write_text("modified\n", encoding="utf-8")
            _commit_all(root, "modify")
            run = _run("run-1", changed=["src/old.py"], allowed=["src/old.py", ".agents/promotions/"],
                       reviewed=[{"path": "src/old.py", "deleted": True, "base_sha256": base_digest, "mode": "100644"}])
            _write_canonical_ledger(root, [run])
            old.unlink()
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"])
            _commit_all(root, "delete")
            rc, output = _capture(cre.run_diff_mode, "HEAD~2..HEAD", policy, root, "research")
        self.assertEqual(rc, 0, output)
        self.assertIn(f"NOTE promotion acknowledged: {ACK} covers src/old.py", output)


if __name__ == "__main__":
    unittest.main()
