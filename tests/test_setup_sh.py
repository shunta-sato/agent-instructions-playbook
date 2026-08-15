from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SETUP_SCRIPT = REPO_ROOT / "setup.sh"


class SetupScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.workdir = Path(self.temp_dir.name) / "target"
        self.workdir.mkdir()
        subprocess.run(
            ["git", "init", "--quiet", str(self.workdir)],
            check=True,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_setup(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(SETUP_SCRIPT), *args],
            check=check,
            capture_output=True,
            text=True,
        )

    def git_exclude_file(self) -> Path:
        path = Path(
            subprocess.run(
                ["git", "-C", str(self.workdir), "rev-parse", "--git-path", "info/exclude"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        return path if path.is_absolute() else self.workdir / path

    def test_enables_all_clients_and_keeps_links_out_of_git_status(self) -> None:
        self.run_setup(str(self.workdir))

        expected = (REPO_ROOT / ".agents" / "skills").resolve()
        self.assertEqual((self.workdir / ".agents" / "skills").resolve(), expected)
        self.assertEqual((self.workdir / ".claude" / "skills").resolve(), expected)

        status = subprocess.run(
            ["git", "-C", str(self.workdir), "status", "--short"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(status.stdout, "")

        patterns = self.git_exclude_file().read_text(encoding="utf-8").splitlines()
        self.assertIn("/.agents/skills", patterns)
        self.assertIn("/.claude/skills", patterns)

    def test_second_run_is_idempotent(self) -> None:
        self.run_setup(str(self.workdir))
        self.run_setup(str(self.workdir))

        patterns = self.git_exclude_file().read_text(encoding="utf-8").splitlines()
        self.assertEqual(patterns.count("/.agents/skills"), 1)
        self.assertEqual(patterns.count("/.claude/skills"), 1)

    def test_defaults_to_the_current_worktree(self) -> None:
        subprocess.run([str(SETUP_SCRIPT)], cwd=self.workdir, check=True)

        self.assertTrue((self.workdir / ".agents" / "skills").is_symlink())
        self.assertTrue((self.workdir / ".claude" / "skills").is_symlink())

    def test_refuses_to_overwrite_an_existing_skill_directory(self) -> None:
        existing = self.workdir / ".claude" / "skills"
        existing.mkdir(parents=True)
        marker = existing / "local-skill.txt"
        marker.write_text("keep", encoding="utf-8")

        result = self.run_setup(str(self.workdir), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(marker.is_file())
        self.assertFalse((self.workdir / ".agents" / "skills").exists())

    def test_rejects_a_subdirectory_instead_of_installing_outside_repo_root(self) -> None:
        nested = self.workdir / "nested"
        nested.mkdir()

        result = self.run_setup(str(nested), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be the Git worktree root", result.stderr)

    def test_rejects_a_non_git_directory(self) -> None:
        non_git = Path(self.temp_dir.name) / "non-git"
        non_git.mkdir()

        result = self.run_setup(str(non_git), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not inside a Git worktree", result.stderr)


if __name__ == "__main__":
    unittest.main()
