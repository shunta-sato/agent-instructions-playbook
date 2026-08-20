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

    def test_overlay_keeps_external_skills_and_links_playbook_skills(self) -> None:
        external_agents = self.workdir / ".agents" / "skills" / "external-flutter-skill"
        external_agents.mkdir(parents=True)
        (external_agents / "SKILL.md").write_text("external", encoding="utf-8")
        external_claude = self.workdir / ".claude" / "skills" / "external-flutter-skill"
        external_claude.mkdir(parents=True)
        (external_claude / "SKILL.md").write_text("external", encoding="utf-8")

        self.run_setup("--overlay", str(self.workdir))

        expected = (REPO_ROOT / ".agents" / "skills" / "dev-workflow").resolve()
        self.assertEqual((self.workdir / ".agents" / "skills" / "dev-workflow").resolve(), expected)
        self.assertEqual((self.workdir / ".claude" / "skills" / "dev-workflow").resolve(), expected)
        self.assertEqual((external_agents / "SKILL.md").read_text(encoding="utf-8"), "external")
        self.assertEqual((external_claude / "SKILL.md").read_text(encoding="utf-8"), "external")

        status = subprocess.run(
            [
                "git",
                "-C",
                str(self.workdir),
                "status",
                "--short",
                "--untracked-files=all",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn(".agents/skills/external-flutter-skill/SKILL.md", status.stdout)
        self.assertIn(".claude/skills/external-flutter-skill/SKILL.md", status.stdout)
        self.assertNotIn("dev-workflow", status.stdout)

    def test_overlay_is_idempotent(self) -> None:
        self.run_setup("--overlay", str(self.workdir))
        self.run_setup("--overlay", str(self.workdir))

        patterns = self.git_exclude_file().read_text(encoding="utf-8").splitlines()
        self.assertEqual(patterns.count("/.agents/skills/dev-workflow"), 1)
        self.assertEqual(patterns.count("/.claude/skills/dev-workflow"), 1)

    def test_overlay_rejects_name_collision_before_partial_install(self) -> None:
        collision = self.workdir / ".agents" / "skills" / "dev-workflow"
        collision.mkdir(parents=True)
        marker = collision / "SKILL.md"
        marker.write_text("external", encoding="utf-8")

        result = self.run_setup("--overlay", str(self.workdir), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to replace existing path", result.stderr)
        self.assertEqual(marker.read_text(encoding="utf-8"), "external")
        self.assertFalse((self.workdir / ".claude" / "skills" / "dev-workflow").exists())

    def test_overlay_rejects_legacy_directory_symlink(self) -> None:
        self.run_setup(str(self.workdir))

        result = self.run_setup("--overlay", str(self.workdir), check=False)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("overlay mode requires a real directory", result.stderr)

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
