"""Boundary-gate tests for the Research OS diff-range mode.

Covers ``check_research_evidence.evaluate_diff`` / ``run_diff_mode``:
promotion, safety, symlink-boundary, declared-mode binding, the non-blocking
mode note, the promotion-acknowledgment downgrade, and CI wiring. Ledger,
runner, and claim tests live in the sibling ``test_research_os.py``.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import check_research_evidence as cre


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
            findings, _ = cre.evaluate_diff(
                ["experiments/e1/run.py", "src/app.py"], Path(tmp), self.POLICY
            )
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertNotIn("promotion-required: experiments/e1/run.py", findings)

    def test_research_only_diff_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, notes = cre.evaluate_diff(
                ["experiments/e1/run.py"], Path(tmp), self.POLICY
            )
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
        with tempfile.TemporaryDirectory() as tmp:
            findings, notes = cre.evaluate_diff(
                ["experiments/e1/run.py"], Path(tmp), self.POLICY, "delivery"
            )
        # Delivery-mode edits to research paths are legitimate: no finding
        # (exit 0), just a claims-discipline reminder note.
        self.assertEqual(findings, [])
        self.assertIn(
            "mode: delivery-mode change under research path experiments/e1/run.py"
            " — claims discipline still applies",
            notes,
        )

    def test_no_mode_mixing_requires_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = cre.evaluate_diff(
                ["experiments/e1/run.py", "src/app.py"], Path(tmp), self.POLICY, None
            )
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertNotIn("promotion-required: experiments/e1/run.py", findings)

    def test_safety_evaluated_in_every_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            for mode in ("research", "delivery", None):
                findings, _ = cre.evaluate_diff(["SECURITY/p.md"], Path(tmp), self.POLICY, mode)
                self.assertIn("safety-review-required: SECURITY/p.md", findings)


# --- (S5) promotion acknowledgment -------------------------------------------


class AcknowledgmentTests(unittest.TestCase):
    POLICY = {"path_modes": {"experiments/": "research"}, "safety_paths": ["SECURITY/"]}
    ACK = ".agents/promotions/2026-07-12-promote.md"

    def test_ack_downgrades_promotion_to_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, notes = cre.evaluate_diff(
                ["src/app.py", self.ACK], Path(tmp), self.POLICY, "research"
            )
        self.assertEqual(
            [f for f in findings if f.startswith("promotion-required:")], []
        )
        self.assertIn(f"promotion acknowledged: {self.ACK} covers src/app.py", notes)

    def test_promotion_without_ack_still_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = cre.evaluate_diff(["src/app.py"], Path(tmp), self.POLICY, "research")
        self.assertIn("promotion-required: src/app.py", findings)

    def test_safety_not_downgraded_by_ack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = cre.evaluate_diff(
                ["SECURITY/policy.md", self.ACK], Path(tmp), self.POLICY, "research"
            )
        # A safety path is never laundered by an acknowledgment.
        self.assertIn("safety-review-required: SECURITY/policy.md", findings)
        self.assertEqual(
            [f for f in findings if f.startswith("promotion-required:")], []
        )

    def test_readme_is_not_an_acknowledgment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, notes = cre.evaluate_diff(
                ["src/app.py", ".agents/promotions/README.md"],
                Path(tmp),
                self.POLICY,
                "research",
            )
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertEqual([n for n in notes if n.startswith("promotion acknowledged:")], [])


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

    def test_promotion_with_ack_in_diff_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, policy_path = self._repo(tmp)
            (root / "src" / "app.py").write_text("y\n", encoding="utf-8")
            (root / ".agents" / "promotions").mkdir(parents=True)
            (root / ".agents" / "promotions" / "2026-07-12-promote.md").write_text(
                "ack\n", encoding="utf-8"
            )
            _commit_all(root, "promote")
            rc = cre.run_diff_mode("HEAD~1..HEAD", policy_path, root, "research")
        self.assertEqual(rc, 0)

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


# --- wiring: the chain, not just the script ----------------------------------


class WiringTests(unittest.TestCase):
    def test_makefile_lint_target_invokes_check(self) -> None:
        makefile = Path(__file__).resolve().parent.parent / "Makefile"
        text = makefile.read_text(encoding="utf-8")
        lint_block = text.split("\nlint:", 1)[1].split("\nanalysis:", 1)[0]
        self.assertIn("check_research_evidence.py --check-ledger", lint_block)

    def test_workflow_runs_diff_range_boundary_gate(self) -> None:
        # S1: the promotion/safety gate must actually be wired into CI, not
        # merely available as a script — mirror the Makefile chain test.
        workflow = (
            Path(__file__).resolve().parent.parent
            / ".github" / "workflows" / "agent-index.yml"
        )
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("check_research_evidence.py --diff-range", text)
        self.assertIn("github.event_name == 'pull_request'", text)


if __name__ == "__main__":
    unittest.main()
