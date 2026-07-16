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
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import check_research_evidence as cre

_STEP_NAME_RE = re.compile(r"^ {6}- name: (.+)$")
_STEP_RUN_RE = re.compile(r"^ {8}run: (.+)$")
_VALIDATOR_WORDS = ("validate", "check", "report", "generate")


def _workflow_step_order(text: str) -> list[tuple[str, str | None]]:
    """``[(step name, run command or None)]`` in file order for a single-job
    GitHub Actions workflow (stdlib-only line scan; no YAML parser needed for
    this file's regular ``- name: ...`` / ``run: ...`` shape)."""
    steps: list[tuple[str, str | None]] = []
    pending_name: str | None = None
    for line in text.splitlines():
        name_match = _STEP_NAME_RE.match(line)
        if name_match:
            if pending_name is not None:
                steps.append((pending_name, None))
            pending_name = name_match.group(1).strip()
            continue
        run_match = _STEP_RUN_RE.match(line)
        if run_match and pending_name is not None:
            steps.append((pending_name, run_match.group(1).strip()))
            pending_name = None
    if pending_name is not None:
        steps.append((pending_name, None))
    return steps


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


# --- (S5) promotion-acknowledgment evidence binding (R4) lives in
# tests/test_research_os_ack.py -----------------------------------------


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

        # B3: the boundary gate judges the whole PR's changed-path set, so it
        # must run AFTER every other validator step, not interleaved with them
        # — otherwise a later validator step could still fail on files the
        # boundary gate already blessed as promoted/reviewed.
        steps = _workflow_step_order(text)
        boundary_indices = [
            i for i, (_, run) in enumerate(steps) if run and "--diff-range" in run
        ]
        self.assertEqual(len(boundary_indices), 1, steps)
        boundary_index = boundary_indices[0]
        other_validator_indices = [
            i for i, (name, _) in enumerate(steps)
            if i != boundary_index and any(word in name.lower() for word in _VALIDATOR_WORDS)
        ]
        self.assertTrue(other_validator_indices, steps)
        self.assertTrue(
            all(i < boundary_index for i in other_validator_indices),
            f"boundary-gate step (index {boundary_index}) must run after every "
            f"other validator step; out-of-order indices: "
            f"{[i for i in other_validator_indices if i > boundary_index]} in {steps}",
        )


if __name__ == "__main__":
    unittest.main()
