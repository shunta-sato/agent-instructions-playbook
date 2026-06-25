from __future__ import annotations

import unittest

from scripts.agent_run import evaluate_run_record, validation_passed


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
