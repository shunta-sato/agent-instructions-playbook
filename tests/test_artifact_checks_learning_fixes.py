"""Regression tests for the adversarial-review fixes to the learning
checker (F1 per-object required fields, F2 fill-prefix sentinel, F6 ref
shapes, F7 attempt-scoped closure correlation, F8 five-field observe-first),
split from tests/test_artifact_checks_learning.py (structure budget)."""

from __future__ import annotations

import unittest
from pathlib import Path

from tests.test_artifact_checks_learning import (
    RETRO_SPEC,
    _good_record,
    _good_report,
    _write_pack,
)

try:
    from scripts.artifact_checks_learning import run_checks
except ModuleNotFoundError:  # direct execution
    from artifact_checks_learning import run_checks


def _run_pack(record, extra_report_text: str = "", replace_report: str | None = None):
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        report = (replace_report if replace_report is not None else _good_report()) + extra_report_text
        pack = _write_pack(root, record, report)
        return run_checks(root, pack, RETRO_SPEC, {})


class ReviewFixRegressionTests(unittest.TestCase):
    """Adversarial-review fixes: the one-token evasions of the closure rules
    (F1), unchecked ref shapes (F6), attempt-scoped correlation (F7), and
    the five-field observe-first contract (F8)."""

    def test_omitted_enforceability_is_a_finding(self) -> None:
        record = _good_record()
        del record["learnings"][0]["enforceability"]
        findings = _run_pack(record)
        self.assertIn("retro:missing-field:learning:L1:enforceability", findings)

    def test_omitted_preventability_is_a_finding(self) -> None:
        record = _good_record()
        del record["attempts"][0]["preventability"]
        findings = _run_pack(record)
        self.assertIn("retro:missing-field:attempt:A1:preventability", findings)

    def test_empty_learnings_with_durable_disposition_is_a_finding(self) -> None:
        record = _good_record()
        record["learnings"] = []
        record["current_work_disposition"] = "harden-repository"
        findings = _run_pack(record)
        self.assertIn("retro:empty-learnings:harden-repository", findings)

    def test_traversal_evidence_ref_is_a_finding(self) -> None:
        record = _good_record()
        record["attempts"][0]["evidence_refs"] = ["../../secrets.env"]
        findings = _run_pack(record)
        self.assertIn("retro:path:traversal:attempt:A1:0", findings)

    def test_absolute_prior_record_is_a_finding(self) -> None:
        record = _good_record()
        record["recurrence"]["prior_records"] = ["/etc/passwd"]
        findings = _run_pack(record)
        self.assertIn("retro:path:absolute:recurrence.prior_records:0", findings)

    def test_attempt_refs_scope_closure_rule_to_named_attempts(self) -> None:
        # F7: a learning citing only a productive-exploration attempt is not
        # forced into a lint action by an unrelated preventable attempt.
        record = _good_record()
        record["attempts"].append(dict(record["attempts"][0],
                                       id="A2", preventability="productive-exploration"))
        learning = record["learnings"][0]
        learning["enforceability"] = "deterministic"
        learning["attempt_refs"] = ["A2"]
        learning["retention_actions"] = [{
            "kind": "retrospective-only", "status": "implemented", "target": "",
            "verification_commands": [], "tracking_ref": "", "closure_condition": "recorded",
        }]
        findings = _run_pack(record)
        self.assertFalse(any(f.startswith("retro:closure:5.1") for f in findings), findings)

    def test_observe_first_requires_missing_evidence_field(self) -> None:
        record = _good_record()
        learning = record["learnings"][0]
        learning["retention_actions"] = [{
            "kind": "observe-first", "status": "planned", "target": "",
            "verification_commands": [], "tracking_ref": "T-1",
            "closure_condition": "re-evaluate",
            "signal": "s", "artifact_path": "reports/x.md", "revisit_condition": "r",
        }]
        findings = _run_pack(record)
        self.assertIn("retro:closure:5.5:L1:0:missing_evidence", findings)

    def test_fill_placeholder_with_colon_is_a_finding(self) -> None:
        # F2: template placeholders use "<fill>"; any "<fill..." remnant fails.
        record = _good_record()
        findings = _run_pack(record, extra_report_text="\n<fill: describe>\n")
        self.assertTrue(any("fill-sentinel" in f for f in findings), findings)



class UnresolvableAttemptRefsTests(unittest.TestCase):
    def test_unresolvable_refs_fail_closed(self) -> None:
        # F16: attempt_refs naming no real attempt must produce a finding AND
        # re-engage the record-level 5.1 correlation, never silence it.
        record = _good_record()
        learning = record["learnings"][0]
        learning["attempt_refs"] = ["A9"]
        learning["retention_actions"] = [{
            "kind": "llm-wiki", "status": "implemented", "target": "README.md",
            "verification_commands": [], "tracking_ref": "", "closure_condition": "recorded",
        }]
        findings = _run_pack(record)
        self.assertIn("retro:unknown-attempt-ref:L1:A9", findings)
        self.assertTrue(any(f.startswith("retro:closure:5.1:L1") for f in findings), findings)


class CodexReviewRegressionTests(unittest.TestCase):
    """PR-review P2 fixes: non-string refs (C1), token-delimited report ID
    citation (C2), non-list container shapes (C3), absorption decision
    required (C4)."""

    def test_non_string_attempt_ref_is_a_finding_not_a_crash(self) -> None:
        record = _good_record()
        record["learnings"][0]["attempt_refs"] = [{"id": "A1"}]
        findings = _run_pack(record)
        self.assertIn("retro:unknown-attempt-ref:L1:<non-string>", findings)

    def test_attempt_id_prefix_does_not_satisfy_citation(self) -> None:
        record = _good_record()
        record["attempts"][0]["id"] = "A1"
        report = _good_report().replace("A1", "A10")
        findings = _run_pack(record, replace_report=report)
        self.assertIn("retro:report-missing-id:attempt:A1", findings)

    def test_non_list_attempts_is_a_finding(self) -> None:
        record = _good_record()
        record["attempts"] = {"A1": record["attempts"][0]}
        findings = _run_pack(record)
        self.assertIn("retro:bad-shape:attempts", findings)

    def test_absorption_without_decision_fails_5_4(self) -> None:
        record = _good_record()
        learning = record["learnings"][0]
        learning["retention_actions"].append({
            "kind": "new-skill-candidate", "status": "planned", "target": "",
            "verification_commands": [], "tracking_ref": "T-2", "closure_condition": "gate",
        })
        del learning["existing_skill_absorption"]["decision"]
        findings = _run_pack(record)
        self.assertIn("retro:closure:5.4:L1", findings)


if __name__ == "__main__":
    unittest.main()
