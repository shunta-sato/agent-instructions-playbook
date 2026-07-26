"""CI/Makefile wiring tests: the chain, not just the script.

Split out of ``test_research_os_gate`` (400-line overflow): asserts that the
boundary-gate, context-budget, and structure-diff checks are actually wired
into the Makefile ``lint`` target and the ``agent-index.yml`` workflow, in
the required step order (including G4's unit-test-before-boundary-gate
ordering)."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

_STEP_NAME_RE = re.compile(r"^ {6}- name: (.+)$")
_STEP_RUN_RE = re.compile(r"^ {8}run: (.+)$")
_VALIDATOR_WORDS = ("validate", "check", "report", "generate")


def _workflow_step_order(text: str) -> list[tuple[str, str | None]]:
    """``[(step name, run command or None)]`` in file order (line scan over
    this workflow's regular ``- name: ...`` / ``run: ...`` shape)."""
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


# --- wiring: the chain, not just the script ----------------------------------


class WiringTests(unittest.TestCase):
    def test_makefile_lint_target_invokes_check(self) -> None:
        makefile = Path(__file__).resolve().parent.parent / "Makefile"
        text = makefile.read_text(encoding="utf-8")
        lint_block = text.split("\nlint:", 1)[1].split("\nanalysis:", 1)[0]
        self.assertIn("check_research_evidence.py --check-ledger", lint_block)

    def test_makefile_lint_target_invokes_context_budget_check(self) -> None:
        # WS-A wave 3: the context-budget gate must sit in the same
        # verify/analysis chain as the other mechanical checks.
        makefile = Path(__file__).resolve().parent.parent / "Makefile"
        text = makefile.read_text(encoding="utf-8")
        lint_block = text.split("\nlint:", 1)[1].split("\nanalysis:", 1)[0]
        self.assertIn("check_context_budget.py", lint_block)

    def test_workflow_runs_context_budget_check_before_unit_tests(self) -> None:
        # WS-A wave 3: the budget gate must run in CI, before the unit-test
        # step (it is a cheap static check; no reason to wait on the suite).
        workflow = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "agent-index.yml"
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("check_context_budget.py", text)

        steps = _workflow_step_order(text)
        budget_indices = [i for i, (_, run) in enumerate(steps) if run and "check_context_budget.py" in run]
        self.assertEqual(len(budget_indices), 1, steps)
        budget_index = budget_indices[0]

        test_indices = [i for i, (_, run) in enumerate(steps) if run and ("unittest" in run or "test-unit" in run)]
        self.assertTrue(test_indices, steps)
        self.assertTrue(all(budget_index < i for i in test_indices),
                         f"context-budget step {budget_index} must run before unit-test step(s) {test_indices} "
                         f"in {steps}")

    def test_workflow_runs_diff_range_boundary_gate(self) -> None:
        # S1/B3: the gate must be wired into CI and run AFTER every other
        # validator step (it judges the whole PR's changed-path set, so a
        # later step could otherwise still fail on files it already blessed).
        workflow = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "agent-index.yml"
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("check_research_evidence.py --diff-range", text)
        self.assertIn("github.event_name == 'pull_request'", text)

        steps = _workflow_step_order(text)
        boundary_indices = [i for i, (_, run) in enumerate(steps)
                             if run and "check_research_evidence.py" in run and "--diff-range" in run]
        self.assertEqual(len(boundary_indices), 1, steps)
        boundary_index = boundary_indices[0]
        other_validator_indices = [i for i, (name, _) in enumerate(steps)
                                    if i != boundary_index and any(w in name.lower() for w in _VALIDATOR_WORDS)]
        self.assertTrue(other_validator_indices, steps)
        self.assertTrue(all(i < boundary_index for i in other_validator_indices),
                         f"boundary-gate step (index {boundary_index}) must run after every other validator step: "
                         f"{[i for i in other_validator_indices if i > boundary_index]} in {steps}")

        # G4: the 197-test suite must actually run in CI, and before the boundary gate.
        test_indices = [i for i, (_, run) in enumerate(steps) if run and ("unittest" in run or "test-unit" in run)]
        self.assertTrue(test_indices, steps)
        self.assertTrue(all(i < boundary_index for i in test_indices),
                         f"unit-test step(s) {test_indices} must run before boundary gate {boundary_index} in {steps}")

    def test_workflow_runs_wave0_lints_before_unit_tests(self) -> None:
        # F5 (Wave 0 review): the instruction-graph and command-doc-drift
        # lints must run in CI unconditionally (push and PR), before the
        # unit-test step — otherwise "wired into make lint" is only a local
        # guarantee and CI would accept a PR that breaks either lint.
        workflow = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "agent-index.yml"
        text = workflow.read_text(encoding="utf-8")
        steps = _workflow_step_order(text)

        test_indices = [i for i, (_, run) in enumerate(steps) if run and ("unittest" in run or "test-unit" in run)]
        self.assertTrue(test_indices, steps)
        for script in ("lint_instruction_graph.py", "lint_command_docs.py", "lint_artifacts.py"):
            lint_indices = [i for i, (_, run) in enumerate(steps) if run and script in run]
            self.assertEqual(len(lint_indices), 1, f"{script} must appear exactly once in {steps}")
            self.assertTrue(all(lint_indices[0] < i for i in test_indices),
                             f"{script} step {lint_indices[0]} must run before unit-test step(s) {test_indices} "
                             f"in {steps}")

    def test_workflow_runs_structure_diff_check_before_unit_tests(self) -> None:
        # L1: the structure-lint diff check must be wired into CI, guarded like
        # the boundary-gate step (PR-only, relies on the full-history checkout),
        # and run before the unit-test step since it depends on neither.
        workflow = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "agent-index.yml"
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("check_structure.py --diff-range", text)

        steps = _workflow_step_order(text)
        structure_indices = [i for i, (_, run) in enumerate(steps)
                              if run and "check_structure.py" in run and "--diff-range" in run]
        self.assertEqual(len(structure_indices), 1, steps)
        structure_index = structure_indices[0]

        test_indices = [i for i, (_, run) in enumerate(steps) if run and ("unittest" in run or "test-unit" in run)]
        self.assertTrue(test_indices, steps)
        self.assertTrue(all(structure_index < i for i in test_indices),
                         f"structure-diff step {structure_index} must run before unit-test step(s) {test_indices} "
                         f"in {steps}")

    def test_workflow_runs_submission_lint_check_after_structure_diff_before_unit_tests(self) -> None:
        # W2-B (plans/20260726-submission-evidence.md): validate-if-present
        # submission_evidence check, guarded like the structure-diff step
        # (PR-only) and positioned just after it, before the unit-test step.
        workflow = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "agent-index.yml"
        text = workflow.read_text(encoding="utf-8")
        self.assertIn("lint_submission.py --diff-range", text)

        steps = _workflow_step_order(text)
        submission_indices = [i for i, (_, run) in enumerate(steps)
                               if run and "lint_submission.py" in run and "--diff-range" in run]
        self.assertEqual(len(submission_indices), 1, steps)
        submission_index = submission_indices[0]

        structure_indices = [i for i, (_, run) in enumerate(steps)
                              if run and "check_structure.py" in run and "--diff-range" in run]
        self.assertEqual(len(structure_indices), 1, steps)
        structure_index = structure_indices[0]
        self.assertEqual(submission_index, structure_index + 1,
                          f"submission-lint step {submission_index} must sit immediately after "
                          f"structure-diff step {structure_index} in {steps}")

        test_indices = [i for i, (_, run) in enumerate(steps) if run and ("unittest" in run or "test-unit" in run)]
        self.assertTrue(test_indices, steps)
        self.assertTrue(all(submission_index < i for i in test_indices),
                         f"submission-lint step {submission_index} must run before unit-test step(s) "
                         f"{test_indices} in {steps}")


if __name__ == "__main__":
    unittest.main()
