"""Round-8 real-git tests for the boundary gate that don't fit the
400-line-capped siblings: F6 (base-policy binding) and (c) (a real git
deletion covered by a ``--reviewed-deleted`` tombstone). Moved here verbatim
from ``test_research_os_gate`` to make room for its G2/G4 additions; no
behavior change. G1 (range-bound declared-mode selector) tests live in
``test_research_os_mode``; G2 (rename-origin evaluation) tests live in
``test_research_os_gate``."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import check_research_evidence as cre
from tests.test_research_os_ack import _run, _write_ack, _write_canonical_ledger
from tests.test_research_os_gate import ACK, _ack_repo, _capture, _commit_all, _git_init


class BasePolicyBindingTests(unittest.TestCase):
    """F6: the gate judges a PR under the BASE-committed policy, so a head-side edit cannot weaken its own gate."""

    def _repo_with_base_policy(self, tmp: str, policy: dict) -> Path:
        root = Path(tmp)
        _git_init(root)
        (root / ".agents").mkdir()
        (root / ".agents" / "project-policy.yml").write_text(json.dumps(policy), encoding="utf-8")
        (root / "SECURITY").mkdir()
        (root / "SECURITY" / "policy.md").write_text("s\n", encoding="utf-8")
        _commit_all(root, "base")
        return root

    def test_head_side_policy_weakening_does_not_weaken_evaluation(self) -> None:
        base_policy = {"path_modes": {}, "safety_paths": ["SECURITY/"]}
        with tempfile.TemporaryDirectory() as tmp:
            root = self._repo_with_base_policy(tmp, base_policy)
            # HEAD weakens the policy AND touches the safety file — would pass if the gate used it.
            weakened = {"path_modes": {}, "safety_paths": []}
            (root / ".agents" / "project-policy.yml").write_text(json.dumps(weakened), encoding="utf-8")
            (root / "SECURITY" / "policy.md").write_text("s2\n", encoding="utf-8")
            _commit_all(root, "weaken policy + touch safety path")
            fallback_policy = root / "unused-fallback.json"
            fallback_policy.write_text(json.dumps(weakened), encoding="utf-8")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", fallback_policy, root, "delivery")
        self.assertEqual(rc, 1)  # base policy still flags SECURITY/policy.md
        self.assertIn("FINDING safety-review-required: SECURITY/policy.md", output)
        self.assertIn("NOTE policy-change: evaluated with base policy; head policy takes effect after merge", output)

    def test_bootstrap_fallback_emits_note_when_no_base_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("x\n", encoding="utf-8")
            _commit_all(root, "base-no-policy")  # no .agents/project-policy.yml at base
            (root / "src" / "app.py").write_text("y\n", encoding="utf-8")
            _commit_all(root, "change")
            policy_path = root / "policy.json"
            policy_path.write_text(json.dumps({"path_modes": {}, "safety_paths": []}), encoding="utf-8")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy_path, root, "delivery")
        self.assertEqual(rc, 0)
        self.assertIn("NOTE policy-bootstrap: no policy at base; evaluating with head policy", output)


class AckDeletionDiffModeTests(unittest.TestCase):
    """(c): a real git deletion, covered by a ``--reviewed-deleted`` tombstone recorded before the delete commit."""

    def test_deletion_covered_by_tombstone_at_diff_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, policy = _ack_repo(tmp)
            (root / "src").mkdir()
            old = root / "src" / "old.py"
            old.write_text("legacy\n", encoding="utf-8")
            base_digest = hashlib.sha256(b"legacy\n").hexdigest()
            run = _run("run-1", changed=["src/old.py"], allowed=["src/old.py", ".agents/promotions/"],
                       reviewed=[{"path": "src/old.py", "deleted": True, "base_sha256": base_digest, "mode": "100644"}])
            _write_canonical_ledger(root, [run])
            _commit_all(root, "base")
            old.unlink()
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"])
            _commit_all(root, "delete")
            rc, output = _capture(cre.run_diff_mode, "HEAD~1..HEAD", policy, root, "research")
        self.assertEqual(rc, 0)
        self.assertIn(f"NOTE promotion acknowledged: {ACK} covers src/old.py", output)


if __name__ == "__main__":
    unittest.main()
