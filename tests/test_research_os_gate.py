"""Boundary-gate tests for the Research OS diff-range and working-tree modes.

Covers ``check_research_evidence.evaluate_diff`` / ``run_diff_mode`` /
``run_working_tree_mode``: promotion, safety, symlink-boundary, declared-mode
binding, the non-blocking mode note, the promotion-acknowledgment downgrade
(F7), base-policy binding (F6), working-tree mode (F1), and CI wiring.
Ledger, runner, and claim tests live in the sibling ``test_research_os.py``.
"""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import check_research_evidence as cre


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


def _write_valid_ack(repo_root: Path, ack_rel: str, covers: list[str]) -> None:
    """F7: a conforming acknowledgment — Scope:, a claims line, and Covers:."""
    ack_path = repo_root / ack_rel
    ack_path.parent.mkdir(parents=True, exist_ok=True)
    covers_lines = "\n".join(f"- {prefix}" for prefix in covers)
    ack_path.write_text(
        f"Scope: test coverage\nno research claims promoted\nCovers:\n{covers_lines}\n",
        encoding="utf-8",
    )


class AcknowledgmentTests(unittest.TestCase):
    POLICY = {"path_modes": {"experiments/": "research"}, "safety_paths": ["SECURITY/"]}
    ACK = ".agents/promotions/2026-07-12-promote.md"

    def test_ack_downgrades_promotion_to_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_valid_ack(root, self.ACK, ["src/", ".agents/"])  # also covers itself
            findings, notes = cre.evaluate_diff(["src/app.py", self.ACK], root, self.POLICY, "research")
        self.assertEqual(
            [f for f in findings if f.startswith("promotion-required:")], []
        )
        self.assertIn(f"promotion acknowledged: {self.ACK} covers src/app.py", notes)

    def test_promotion_without_ack_still_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = cre.evaluate_diff(["src/app.py"], Path(tmp), self.POLICY, "research")
        self.assertIn("promotion-required: src/app.py", findings)

    def test_invalid_ack_downgrades_nothing(self) -> None:
        # F7: an ack missing every required element (Scope/claims/Covers)
        # must not launder the finding, and the gate must say why.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".agents" / "promotions").mkdir(parents=True)
            (root / self.ACK).write_text("not a real ack\n", encoding="utf-8")
            findings, notes = cre.evaluate_diff(["src/app.py", self.ACK], root, self.POLICY, "research")
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any(n.startswith(f"invalid-acknowledgment: {self.ACK}") for n in notes), notes)

    def test_partial_covers_leaves_uncovered_findings_blocking(self) -> None:
        # F7: a valid ack only downgrades paths under its Covers prefixes;
        # an uncovered delivery path stays blocking even with a valid ack.
        policy = {"path_modes": {"experiments/": "research"}, "safety_paths": []}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_valid_ack(root, self.ACK, ["src/", ".agents/"])  # covers src/, not tools/
            findings, notes = cre.evaluate_diff(
                ["src/app.py", "tools/build.py", self.ACK], root, policy, "research"
            )
        self.assertEqual([f for f in findings if f.startswith("promotion-required:")], ["promotion-required: tools/build.py"])
        self.assertIn(f"promotion acknowledged: {self.ACK} covers src/app.py", notes)

    def test_safety_not_downgraded_by_ack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_valid_ack(root, self.ACK, ["SECURITY/", ".agents/"])
            findings, _ = cre.evaluate_diff(["SECURITY/policy.md", self.ACK], root, self.POLICY, "research")
        # A safety path is never laundered by an acknowledgment, even a valid
        # one whose Covers prefix matches it.
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
            # Covers both the promoted path AND the ack's own .agents/ path.
            _write_valid_ack(root, ".agents/promotions/2026-07-12-promote.md", ["src/", ".agents/"])
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


# --- (F6) base-policy binding -------------------------------------------------


class BasePolicyBindingTests(unittest.TestCase):
    """F6: the gate judges a PR under the policy committed at the range's BASE
    ref, so a head-side policy edit cannot weaken its own gate."""

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
            # HEAD removes the safety_paths entry AND touches the safety file;
            # if the gate used this weakened head policy it would pass.
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
