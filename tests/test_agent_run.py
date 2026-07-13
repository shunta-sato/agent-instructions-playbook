from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.agent_run import evaluate_run_record, reviewed_files_from_args, validation_passed


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


if __name__ == "__main__":
    unittest.main()
