from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECK_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_structure.py"
DEFAULT_BASELINE_RELPATH = ".agents/structure-baseline.json"


def _entry(rule: str, path: str, value: int, limit: int) -> dict:
    """Build one baseline-entry dict without repeating four keys per test."""
    return {"rule": rule, "path": path, "value": value, "limit": limit}


def _write(root: Path, relpath: str, text: str) -> Path:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _write_baseline(root: Path, entries: list[dict], version: int = 1) -> Path:
    document = json.dumps({"version": version, "entries": entries})
    return _write(root, DEFAULT_BASELINE_RELPATH, document)


def _run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


class PathConfinementTests(unittest.TestCase):
    """End-to-end checks that a baseline entry can never escape the repo
    root via an absolute path, ``..`` traversal, or a symlink (leaf or
    parent directory) — and that path aliases still collapse for duplicate
    detection. See ``scripts/structure_paths.py``.
    """

    def _repo_with_outside_file(self, parent: Path) -> tuple[Path, Path]:
        """Create ``repo`` (small clean source) and a sibling ``outside``
        dir (oversized source), returning ``(root, outside_file)``.
        """
        root = parent / "repo"
        outside = parent / "outside"
        root.mkdir()
        outside.mkdir()
        outside_file = _write(outside, "secret.py", "print(1)\n" * 500)
        _write(root, "src/parser.rs", "fn f() {}\n" * 20)
        return root, outside_file

    def _assert_entry_path_escapes(self, root: Path, entry_path: str) -> None:
        _write_baseline(root, [_entry("source-file-lines", entry_path, 500, 400)])
        result = _run(root, "src/parser.rs", "--json")
        self.assertEqual(result.returncode, 1)
        payload = json.loads(result.stdout)
        kinds = [issue["kind"] for issue in payload["baseline_errors"]]
        self.assertIn("path-escape", kinds)

    def test_absolute_outside_path_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as parent:
            root, outside_file = self._repo_with_outside_file(Path(parent))
            self._assert_entry_path_escapes(root, str(outside_file))

    def test_traversal_outside_path_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as parent:
            root, _outside_file = self._repo_with_outside_file(Path(parent))
            self._assert_entry_path_escapes(root, "../outside/secret.py")

    def test_symlinked_leaf_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as parent:
            root, outside_file = self._repo_with_outside_file(Path(parent))
            os.symlink(outside_file, root / "leaf_link.py")
            self._assert_entry_path_escapes(root, "leaf_link.py")

    def test_symlinked_parent_directory_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as parent:
            root, outside_file = self._repo_with_outside_file(Path(parent))
            os.symlink(outside_file.parent, root / "linked_dir")
            self._assert_entry_path_escapes(root, "linked_dir/secret.py")

    def test_path_alias_is_still_detected_as_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 500)
            _write_baseline(
                root,
                [
                    _entry("source-file-lines", "src/parser.rs", 500, 400),
                    _entry("source-file-lines", "./src/parser.rs", 500, 400),
                ],
            )
            result = _run(root, "src/parser.rs", "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            kinds = [issue["kind"] for issue in payload["baseline_errors"]]
            self.assertIn("duplicate-entry", kinds)


if __name__ == "__main__":
    unittest.main()
