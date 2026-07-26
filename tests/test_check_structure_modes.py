"""Tests for check_structure.py's git-driven selection modes (--working-tree,
--diff-range), added alongside the pre-existing explicit-list mode. Fixture
style mirrors tests/test_research_os_gate.py (real git repos in a tempdir);
mode dispatch is exercised end-to-end through ``main()``, like
tests/test_context_budget.py does for its own CLI entry point."""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.check_structure import main


def _capture(argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = main(argv)
    return rc, buf.getvalue()


def _git_init(root: Path) -> None:
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def _commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", message], check=True, capture_output=True)


def _write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


class WorkingTreeModeTests(unittest.TestCase):
    def test_added_and_modified_files_are_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/clean.py", "x = 1\n")
            _commit_all(root, "base")
            _write(root, "src/clean.py", "x = 1\n" * 500)  # modified, now oversized
            _write(root, "src/new_big.py", "y = 1\n" * 500)  # untracked, oversized
            rc, output = _capture(["--working-tree", "--repo-root", str(root)])
        self.assertEqual(rc, 1)
        self.assertIn("src/clean.py", output)
        self.assertIn("src/new_big.py", output)

    def test_deleted_file_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            path = _write(root, "src/gone.py", "x = 1\n" * 500)
            _commit_all(root, "base")
            path.unlink()  # unstaged deletion
            rc, output = _capture(["--working-tree", "--repo-root", str(root)])
        self.assertEqual(rc, 0)
        self.assertNotIn("gone.py", output)

    def test_unchanged_tree_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/clean.py", "x = 1\n")
            _commit_all(root, "base")
            rc, output = _capture(["--working-tree", "--repo-root", str(root)])
        self.assertEqual(rc, 0)
        self.assertIn("0 source files checked", output)


class DiffRangeModeTests(unittest.TestCase):
    def test_changed_file_still_present_is_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            _write(root, "src/app.py", "x = 1\n" * 500)
            _commit_all(root, "grow")
            rc, output = _capture(["--diff-range", "HEAD~1..HEAD", "--repo-root", str(root)])
        self.assertEqual(rc, 1)
        self.assertIn("src/app.py", output)

    def test_file_deleted_at_head_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            path = _write(root, "src/gone.py", "x = 1\n" * 500)
            _commit_all(root, "base")
            path.unlink()
            _commit_all(root, "remove")
            rc, output = _capture(["--diff-range", "HEAD~1..HEAD", "--repo-root", str(root)])
        self.assertEqual(rc, 0)
        self.assertNotIn("gone.py", output)


class ExplicitListModeTests(unittest.TestCase):
    def test_explicit_list_mode_is_unaffected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = _write(root, "src/big.py", "x = 1\n" * 500)
            rc, output = _capture([str(path)])
        self.assertEqual(rc, 1)
        self.assertIn("src/big.py", output)

    def test_modes_are_mutually_exclusive(self) -> None:
        with self.assertRaises(SystemExit):
            main(["--working-tree", "some/file.py"])


class WaiverIntegrationTests(unittest.TestCase):
    def _write_policy(self, root: Path, waivers: list[dict]) -> None:
        _write(root, ".agents/project-policy.yml", json.dumps({"structure_waivers": waivers}))

    def test_waiver_honored_in_working_tree_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            self._write_policy(root, [{"path": "experiments/", "reason": "disposable probe code"}])
            _commit_all(root, "policy")
            _write(root, "experiments/probe.py", "x = 1\n" * 500)
            rc, output = _capture(["--working-tree", "--repo-root", str(root)])
        self.assertEqual(rc, 0)
        self.assertIn("waived", output)

    def test_waiver_honored_in_diff_range_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            self._write_policy(root, [{"path": "experiments/", "reason": "disposable probe code"}])
            _write(root, "experiments/probe.py", "x = 1\n")
            _commit_all(root, "base")
            _write(root, "experiments/probe.py", "x = 1\n" * 500)
            _commit_all(root, "grow")
            rc, output = _capture(["--diff-range", "HEAD~1..HEAD", "--repo-root", str(root)])
        self.assertEqual(rc, 0)
        self.assertIn("waived", output)


if __name__ == "__main__":
    unittest.main()
