from __future__ import annotations

import argparse
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.agent_run import (
    add_record_parser,
    build_run_record,
    evaluate_run_record,
    reviewed_files_from_args,
    validation_passed,
)


def _git_init(root: Path) -> None:
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def _commit_all(root: Path, message: str) -> None:
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", message], check=True, capture_output=True)


def _record_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    add_record_parser(subparsers)
    return parser.parse_args(["record", *argv])


class ReviewedFilesTests(unittest.TestCase):
    def test_records_script_computed_sha256(self) -> None:
        # Q3b: the script hashes the file at record time (caller supplies no digest).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("payload\n", encoding="utf-8")
            entries = reviewed_files_from_args(["a.txt"], root)
        self.assertEqual(
            entries, [{"path": "a.txt", "sha256": hashlib.sha256(b"payload\n").hexdigest()}]
        )

    def test_missing_reviewed_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                reviewed_files_from_args(["ghost.txt"], Path(tmp))

    def test_symlink_hashes_readlink_target_string(self) -> None:
        # Supervisor follow-up: a git-tracked symlink (e.g. the .claude/skills
        # mirror, which points at a DIRECTORY) must not be rejected as missing,
        # and must hash the readlink target string — the same content git
        # stores as the symlink's blob — not the resolved target's bytes.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "real_dir").mkdir()
            (root / "link").symlink_to("real_dir")
            entries = reviewed_files_from_args(["link"], root)
        self.assertEqual(
            entries,
            [{"path": "link", "sha256": hashlib.sha256(b"real_dir").hexdigest()}],
        )


class AgentRunValidationTests(unittest.TestCase):
    def test_validation_passed_requires_command_evidence(self) -> None:
        self.assertFalse(validation_passed({"passed": True}))
        self.assertFalse(validation_passed({"commands": []}))

    def test_validation_passed_accepts_nonempty_passing_commands(self) -> None:
        self.assertTrue(
            validation_passed(
                {
                    "commands": [
                        {"cmd": "make test-unit", "exit_code": 0, "passed": True}
                    ],
                    "passed": True,
                }
            )
        )

    def test_forged_record_without_command_evidence_is_rejected(self) -> None:
        judgment = evaluate_run_record(
            {
                "record_type": "agent_run",
                "run_id": "poc-forged-no-validation-output",
                "allowed_files": ["scripts/agent_run.py"],
                "changed_files": ["scripts/agent_run.py"],
                "outcome": {"agent_completed": True},
                "validation": {"passed": True},
            }
        )

        self.assertFalse(judgment["validation_passed"])
        self.assertFalse(judgment["accepted"])

    def test_validation_passed_rejects_nonzero_exit_with_passed_forced_true(self) -> None:
        # (b): a contradictory record — "cmd" 1 with passed forced true — must
        # not pass; every command's own exit_code must be 0, not just its flag.
        self.assertFalse(
            validation_passed(
                {"commands": [{"cmd": "make test-unit", "exit_code": 1, "passed": True}], "passed": True}
            )
        )

    def test_validation_passed_requires_every_command_to_exit_zero(self) -> None:
        self.assertFalse(
            validation_passed(
                {
                    "commands": [
                        {"cmd": "make test-unit", "exit_code": 0, "passed": True},
                        {"cmd": "make lint", "exit_code": 1, "passed": True},
                    ],
                    "passed": True,
                }
            )
        )
        self.assertTrue(
            validation_passed(
                {
                    "commands": [
                        {"cmd": "make test-unit", "exit_code": 0, "passed": True},
                        {"cmd": "make lint", "exit_code": 0, "passed": True},
                    ],
                    "passed": True,
                }
            )
        )


class ReviewChangedFlagTests(unittest.TestCase):
    """B3: ``--review-changed`` gives content-identity evidence for changed
    paths too, by also hashing them into ``reviewed_files``."""

    def _base_argv(self, root: Path, brief: Path, *extra: str) -> list[str]:
        return [
            "--repo-root", str(root),
            "--harness", "test-harness",
            "--task-class", "focused_code_change",
            "--capability-profile", "focused_code_edit",
            "--prompt-detail", "strict",
            "--brief-source", str(brief),
            "--allowed-file", "src/app.py",
            *extra,
        ]

    def test_review_changed_adds_changed_file_to_reviewed_with_digest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("payload\n", encoding="utf-8")
            brief = root / "brief.md"
            brief.write_text("brief\n", encoding="utf-8")
            args = _record_args(self._base_argv(
                root, brief, "--changed-file", "src/app.py", "--review-changed",
            ))
            _, record = build_run_record(args)
        self.assertEqual(
            record["reviewed_files"],
            [{"path": "src/app.py", "sha256": hashlib.sha256(b"payload\n").hexdigest()}],
        )

    def test_review_changed_dedupes_against_explicit_reviewed_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("payload\n", encoding="utf-8")
            brief = root / "brief.md"
            brief.write_text("brief\n", encoding="utf-8")
            args = _record_args(self._base_argv(
                root, brief,
                "--changed-file", "src/app.py",
                "--reviewed-file", "src/app.py",
                "--review-changed",
            ))
            _, record = build_run_record(args)
        self.assertEqual(len(record["reviewed_files"]), 1)

    def test_without_review_changed_flag_reviewed_files_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("payload\n", encoding="utf-8")
            brief = root / "brief.md"
            brief.write_text("brief\n", encoding="utf-8")
            args = _record_args(self._base_argv(root, brief, "--changed-file", "src/app.py"))
            _, record = build_run_record(args)
        self.assertNotIn("reviewed_files", record)


class ReviewedDeletedTests(unittest.TestCase):
    """(c)/M2: ``--reviewed-deleted`` tombstones a path with the sha256 AND
    git-mode of its blob at current HEAD (before the delete commit lands),
    since there is no head blob left to hash once the deletion is committed."""

    def _base_argv(self, root: Path, brief: Path, *extra: str) -> list[str]:
        return [
            "--repo-root", str(root),
            "--harness", "test-harness",
            "--task-class", "focused_code_change",
            "--capability-profile", "focused_code_edit",
            "--prompt-detail", "strict",
            "--brief-source", str(brief),
            "--allowed-file", "src/old.py",
            *extra,
        ]

    def test_reviewed_deleted_records_tombstone_from_head_blob(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "src").mkdir()
            (root / "src" / "old.py").write_text("legacy\n", encoding="utf-8")
            _commit_all(root, "base")
            brief = root / "brief.md"
            brief.write_text("brief\n", encoding="utf-8")
            args = _record_args(self._base_argv(root, brief, "--reviewed-deleted", "src/old.py"))
            _, record = build_run_record(args)
        self.assertEqual(
            record["reviewed_files"],
            [{"path": "src/old.py", "deleted": True,
              "base_sha256": hashlib.sha256(b"legacy\n").hexdigest(), "mode": "100644"}],
        )

    def test_reviewed_deleted_missing_at_head_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "src").mkdir()
            (root / "src" / "keep.py").write_text("x\n", encoding="utf-8")
            _commit_all(root, "base")
            brief = root / "brief.md"
            brief.write_text("brief\n", encoding="utf-8")
            args = _record_args(self._base_argv(root, brief, "--reviewed-deleted", "src/ghost.py"))
            with self.assertRaises(ValueError):
                build_run_record(args)


if __name__ == "__main__":
    unittest.main()
