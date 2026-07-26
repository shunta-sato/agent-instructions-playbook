"""End-to-end mode tests for scripts/lint_submission.py, split from
tests/test_lint_submission.py (structure budget): --record / --working-tree /
--diff-range dispatch, head_commit candidate selection (F1), all-candidates
evaluation (F11), adoption-phase pass, and the judge_agent_run --run-id
requirement."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from tests.test_lint_submission import (
    REPO_ROOT,
    _agent_run,
    _capture,
    _commit_all,
    _git_init,
    _sha,
    _submission_record,
    _write,
    _write_ledger,
)

# --- end-to-end: modes -------------------------------------------------------------


class HappyPathTests(unittest.TestCase):
    def test_fully_valid_record_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            ledger = _write_ledger(
                root,
                [
                    _agent_run("W1"),
                    _submission_record(
                        "SUB-1",
                        changed_files=[{"path": "src/app.py", "sha256": _sha("x = 1\n")}],
                        cited_runs=["W1"],
                    ),
                ],
            )
            rc, output = _capture(["--record", "SUB-1", "--repo-root", str(root), "--ledger", str(ledger)])
        self.assertEqual(rc, 0, output)
        self.assertIn("pass", output)


class NoRecordAdoptionPhaseTests(unittest.TestCase):
    def test_no_submission_record_passes_with_adoption_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            missing_ledger = root / ".agents" / "runs" / "agent-runs.jsonl"
            rc, output = _capture(["--working-tree", "--repo-root", str(root), "--ledger", str(missing_ledger)])
        self.assertEqual(rc, 0)
        self.assertEqual(output.strip(), "lint-submission: pass (no submission record; adoption phase)")


def _head_sha(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


class CandidateSelectionTests(unittest.TestCase):
    def test_record_at_current_head_is_validated_in_working_tree_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            _write(root, "src/app.py", "x = 2\n")
            record = _submission_record(
                "SUB-1",
                head_commit=_head_sha(root),
                changed_files=[{"path": "src/app.py", "sha256": _sha("x = 2\n")}],
            )
            ledger = _write_ledger(root, [record])
            rc, output = _capture(["--working-tree", "--repo-root", str(root), "--ledger", str(ledger)])
        self.assertEqual(rc, 0, output)
        self.assertIn("SUB-1", output)

    def test_record_with_foreign_head_commit_is_ignored(self) -> None:
        # F1: a record from another commit's submission never turns stale
        # against this tree -- it is simply not a candidate.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            record = _submission_record(
                "SUB-OLD",
                changed_files=[{"path": "src/app.py", "sha256": _sha("stale content\n")}],
            )  # placeholder head_commit never resolves here
            ledger = _write_ledger(root, [record])
            rc, output = _capture(["--working-tree", "--repo-root", str(root), "--ledger", str(ledger)])
        self.assertEqual(rc, 0, output)
        self.assertIn("adoption phase", output)

    def test_all_candidates_evaluated_dirty_sibling_fails_the_run(self) -> None:
        # F11: a clean record cannot shadow a dirty sibling at the same head.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            head = _head_sha(root)
            dirty = _submission_record(
                "SUB-DIRTY", head_commit=head, gate_decision="no-submit")
            clean = _submission_record("SUB-CLEAN", head_commit=head)
            ledger = _write_ledger(root, [dirty, clean])
            rc, output = _capture(["--working-tree", "--repo-root", str(root), "--ledger", str(ledger)])
        self.assertEqual(rc, 1, output)
        self.assertIn("gate-decision:no-submit", output)

    def test_diff_range_mode_validates_in_range_record_against_range_head(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            base = _head_sha(root)
            _write(root, "src/app.py", "x = 2\n")
            _commit_all(root, "feature")
            head = _head_sha(root)
            record = _submission_record(
                "SUB-R",
                head_commit=head,
                changed_files=[{"path": "src/app.py", "sha256": _sha("x = 2\n")}],
            )
            ledger = _write_ledger(root, [record])
            rc, output = _capture([
                "--diff-range", f"{base}..{head}",
                "--repo-root", str(root), "--ledger", str(ledger),
            ])
        self.assertEqual(rc, 0, output)
        self.assertIn("SUB-R", output)


class JudgeAgentRunRequiresRunIdTests(unittest.TestCase):
    def test_missing_run_id_is_refused(self) -> None:
        result = subprocess.run(
            ["python3", "scripts/judge_agent_run.py"], cwd=REPO_ROOT, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("--run-id", result.stderr)



if __name__ == "__main__":
    unittest.main()
