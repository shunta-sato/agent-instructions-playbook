"""End-to-end tests for structure checker selection and feature/strict modes."""

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
    def test_working_tree_defaults_to_feature_and_blocks_hard_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/clean.py", "x = 1\n")
            _commit_all(root, "base")
            _write(root, "src/clean.py", "x = 1\n" * 1600)
            _write(root, "src/new_big.py", "y = 1\n" * 1600)
            rc, output = _capture(["--working-tree", "--repo-root", str(root)])
        self.assertEqual(rc, 1)
        self.assertIn("mode=feature", output)
        self.assertIn("src/clean.py", output)
        self.assertIn("src/new_big.py", output)

    def test_feature_advisory_reports_but_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            _write(root, "src/app.py", "x = 1\n" * 700)
            rc, output = _capture(["--working-tree", "--repo-root", str(root)])
        self.assertEqual(rc, 0)
        self.assertIn("ADVISORY source-file-lines", output)
        self.assertIn("pass (1 advisory", output)

    def test_deleted_file_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            path = _write(root, "src/gone.py", "x = 1\n" * 1600)
            _commit_all(root, "base")
            path.unlink()
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
    def test_diff_range_defaults_to_feature_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            _write(root, "src/app.py", "x = 1\n" * 700)
            _commit_all(root, "grow")
            rc, output = _capture(["--diff-range", "HEAD~1..HEAD", "--repo-root", str(root)])
        self.assertEqual(rc, 0)
        self.assertIn("ADVISORY source-file-lines", output)
        self.assertIn("mode=feature", output)

    def test_diff_range_hard_finding_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            _write(root, "src/app.py", "x = 1\n" * 1600)
            _commit_all(root, "grow")
            rc, output = _capture(["--diff-range", "HEAD~1..HEAD", "--repo-root", str(root)])
        self.assertEqual(rc, 1)
        self.assertIn("FINDING source-file-lines", output)

    def test_file_deleted_at_head_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            path = _write(root, "src/gone.py", "x = 1\n" * 1600)
            _commit_all(root, "base")
            path.unlink()
            _commit_all(root, "remove")
            rc, output = _capture(["--diff-range", "HEAD~1..HEAD", "--repo-root", str(root)])
        self.assertEqual(rc, 0)
        self.assertNotIn("gone.py", output)


class FeatureNoMaterialWorseningTests(unittest.TestCase):
    def test_small_change_in_preexisting_hard_debt_is_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/legacy.py", "x = 1\n" * 1600)
            _commit_all(root, "base")
            _write(root, "src/legacy.py", "x = 1\n" * 1601)
            rc, output = _capture(["--working-tree", "--repo-root", str(root)])
        self.assertEqual(rc, 0)
        self.assertIn("ADVISORY source-file-lines", output)
        self.assertIn("pre-existing hard debt", output)
        self.assertIn("delta=+1", output)

    def test_material_growth_in_preexisting_hard_debt_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/legacy.py", "x = 1\n" * 1600)
            _commit_all(root, "base")
            _write(root, "src/legacy.py", "x = 1\n" * 1651)
            rc, output = _capture(["--working-tree", "--repo-root", str(root)])
        self.assertEqual(rc, 1)
        self.assertIn("FINDING source-file-lines", output)
        self.assertIn("grew materially", output)

    def test_crossing_hard_guardrail_blocks_even_for_small_delta(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n" * 1499)
            _commit_all(root, "base")
            _write(root, "src/app.py", "x = 1\n" * 1501)
            rc, output = _capture(["--working-tree", "--repo-root", str(root)])
        self.assertEqual(rc, 1)
        self.assertIn("FINDING source-file-lines", output)

    def test_new_file_over_hard_guardrail_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "README.md", "base\n")
            _commit_all(root, "base")
            _write(root, "src/new_big.py", "x = 1\n" * 1501)
            rc, output = _capture(["--working-tree", "--repo-root", str(root)])
        self.assertEqual(rc, 1)
        self.assertIn("FINDING source-file-lines", output)

    def test_diff_range_uses_left_ref_as_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/legacy.py", "x = 1\n" * 1600)
            _commit_all(root, "base")
            _write(root, "src/legacy.py", "x = 1\n" * 1602)
            _commit_all(root, "small fix")
            rc, output = _capture([
                "--diff-range", "HEAD~1..HEAD", "--repo-root", str(root)
            ])
        self.assertEqual(rc, 0)
        self.assertIn("pre-existing hard debt", output)


class ExplicitListModeTests(unittest.TestCase):
    def test_explicit_list_defaults_to_strict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = _write(root, "src/big.py", "x = 1\n" * 700)
            rc, output = _capture([str(path)])
        self.assertEqual(rc, 1)
        self.assertIn("mode=strict", output)

    def test_explicit_feature_mode_is_available(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = _write(root, "src/big.py", "x = 1\n" * 700)
            rc, output = _capture([str(path), "--mode", "feature"])
        self.assertEqual(rc, 0)
        self.assertIn("ADVISORY", output)

    def test_modes_are_mutually_exclusive(self) -> None:
        with self.assertRaises(SystemExit):
            main(["--working-tree", "some/file.py"])

    def test_hard_limit_cannot_be_below_advisory_limit(self) -> None:
        with self.assertRaises(SystemExit):
            main(["--hard-source-lines", "500", "--max-source-lines", "600"])


class WaiverIntegrationTests(unittest.TestCase):
    def _write_policy(self, root: Path, waivers: list[dict]) -> None:
        _write(root, ".agents/project-policy.yml", json.dumps({"structure_waivers": waivers}))

    def test_waiver_honored_in_working_tree_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            self._write_policy(root, [{"path": "experiments/", "reason": "disposable probe code"}])
            _commit_all(root, "policy")
            _write(root, "experiments/probe.py", "x = 1\n" * 1600)
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
            _write(root, "experiments/probe.py", "x = 1\n" * 1600)
            _commit_all(root, "grow")
            rc, output = _capture(["--diff-range", "HEAD~1..HEAD", "--repo-root", str(root)])
        self.assertEqual(rc, 0)
        self.assertIn("waived", output)


if __name__ == "__main__":
    unittest.main()
