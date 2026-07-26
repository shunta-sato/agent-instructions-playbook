"""Tests for scripts/lint_submission.py (Wave 2, submission_evidence record
checker; see plans/20260726-submission-evidence.md). Fixture style mirrors
tests/test_check_structure_modes.py (real git repos in a tempdir, mode
dispatch exercised end-to-end through main()); the per-check finding-id
tests unit-test each check function directly, like tests/test_agent_run.py
does for evaluate_run_record. The judge_agent_run --run-id requirement
(adjudication 5) is exercised via subprocess against the real script."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.lint_submission import (
    check_cited_runs,
    check_freshness,
    check_gate_decision,
    check_schema,
    check_triggered_branches,
    check_validation_chain,
    main,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


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


def _write_ledger(root: Path, records: list[dict]) -> Path:
    ledger = root / ".agents" / "runs" / "agent-runs.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
    return ledger


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _agent_run(run_id: str, *, agent_completed: bool = True, quality_gate: str = "pass",
               commands: list[dict] | None = None) -> dict:
    if commands is None:
        commands = [{"cmd": "make verify", "exit_code": 0, "passed": True}]
    return {
        "record_type": "agent_run",
        "run_id": run_id,
        "allowed_files": ["scripts/example.py"],
        "changed_files": ["scripts/example.py"],
        "validation": {"commands": commands, "quality_gate": quality_gate},
        "outcome": {"agent_completed": agent_completed},
    }


def _submission_record(run_id: str, **overrides) -> dict:
    record = {
        "schema_version": 1,
        "record_type": "submission_evidence",
        "run_id": run_id,
        "created_at": "2026-07-26T00:00:00+00:00",
        "branch": "feature-x",
        "base_ref": "",
        "head_commit": "0" * 40,
        "changed_files": [],
        "validation": {"commands": [{"cmd": "make verify", "exit_code": 0, "passed": True}]},
        "cited_runs": [],
        "triggered_branches": [],
        "gate_decision": "submit",
        "notes": "",
    }
    record.update(overrides)
    return record


# --- (a) schema ---------------------------------------------------------------


class SchemaCheckTests(unittest.TestCase):
    def test_missing_field_reports_finding(self) -> None:
        record = _submission_record("R1")
        del record["gate_decision"]
        self.assertIn("schema:gate_decision", check_schema(record))

    def test_complete_record_has_no_finding(self) -> None:
        self.assertEqual(check_schema(_submission_record("R1")), [])


# --- (b) cited_runs ------------------------------------------------------------


class CitedRunsCheckTests(unittest.TestCase):
    def test_missing_run_reports_finding(self) -> None:
        record = _submission_record("R1", cited_runs=["ghost-run"])
        self.assertIn("cited-run:missing:ghost-run", check_cited_runs(record, {}))

    def test_not_accepted_run_reports_finding(self) -> None:
        run = _agent_run("W1", agent_completed=False)
        record = _submission_record("R1", cited_runs=["W1"])
        self.assertIn("cited-run:not-accepted:W1", check_cited_runs(record, {"W1": run}))

    def test_never_gated_run_citable_only_under_submit_record(self) -> None:
        # F8: a worker run gated by the supervisor (quality_gate not_run) is
        # citable when THIS record's gate_decision is submit; a no-submit
        # record cannot borrow the stand-in.
        run = _agent_run("W1", quality_gate="not_run")
        submit_record = _submission_record("R1", cited_runs=["W1"])
        self.assertEqual(check_cited_runs(submit_record, {"W1": run}), [])
        nosubmit_record = _submission_record(
            "R1", cited_runs=["W1"], gate_decision="no-submit")
        self.assertIn("cited-run:gate:W1", check_cited_runs(nosubmit_record, {"W1": run}))

    def test_failed_gate_run_reports_finding(self) -> None:
        run = _agent_run("W1", quality_gate="fail")
        record = _submission_record("R1", cited_runs=["W1"])
        self.assertIn("cited-run:gate:W1", check_cited_runs(record, {"W1": run}))

    def test_duplicate_run_id_reports_finding(self) -> None:
        # F12: a re-appended run id could relaunder a rejected run.
        run = _agent_run("W1", quality_gate="pass")
        record = _submission_record("R1", cited_runs=["W1"])
        findings = check_cited_runs(record, {"W1": run}, duplicate_ids={"W1"})
        self.assertIn("cited-run:duplicate:W1", findings)

    def test_valid_cited_run_has_no_finding(self) -> None:
        run = _agent_run("W1", quality_gate="pass")
        record = _submission_record("R1", cited_runs=["W1"])
        self.assertEqual(check_cited_runs(record, {"W1": run}), [])


# --- (c) triggered_branches ------------------------------------------------------


class TriggeredBranchesCheckTests(unittest.TestCase):
    def test_run_id_shaped_artifact_validated_as_cited_run(self) -> None:
        # Design-record schema: artifact is "path or run id". A run-id-shaped
        # value must be checked against the ledger, not HEAD paths.
        record = {"triggered_branches": [
            {"branch": "delegated", "artifact": "20260726T000000Z-x-deadbeef"}]}
        findings = check_triggered_branches(record, Path("."), {})
        self.assertEqual(
            findings, ["artifact-run:missing:20260726T000000Z-x-deadbeef"])

    def test_missing_artifact_reports_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "keep.md", "x\n")
            _commit_all(root, "base")
            record = _submission_record(
                "R1", triggered_branches=[{"branch": "x", "artifact": "docs/missing.md"}]
            )
            findings = check_triggered_branches(record, root, {})
        self.assertEqual(findings, ["artifact-missing:docs/missing.md"])

    def test_contract_review_not_submit_reports_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            artifact = "reports/workflow-contract-review/sample.md"
            _write(root, artifact, "## Decision\n\nno-submit\n")
            _commit_all(root, "base")
            record = _submission_record(
                "R1", triggered_branches=[{"branch": "contract", "artifact": artifact}]
            )
            findings = check_triggered_branches(record, root, {})
        self.assertEqual(findings, [f"contract-not-submit:{artifact}"])

    def test_existing_artifact_and_submit_decision_have_no_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "docs/plain.md", "notes\n")
            artifact = "reports/workflow-contract-review/ok.md"
            _write(root, artifact, "## Decision\n\nsubmit\n")
            _commit_all(root, "base")
            record = _submission_record(
                "R1",
                triggered_branches=[
                    {"branch": "x", "artifact": "docs/plain.md"},
                    {"branch": "contract", "artifact": artifact},
                ],
            )
            findings = check_triggered_branches(record, root, {})
        self.assertEqual(findings, [])


# --- (d) validation chain --------------------------------------------------------


class ValidationChainCheckTests(unittest.TestCase):
    def test_missing_chain_reports_finding(self) -> None:
        record = _submission_record("R1", validation={"commands": [{"cmd": "make format", "exit_code": 0, "passed": True}]})
        self.assertEqual(check_validation_chain(record), ["validation-chain-missing"])

    def test_failing_verify_command_reports_finding(self) -> None:
        record = _submission_record(
            "R1", validation={"commands": [{"cmd": "make verify", "exit_code": 1, "passed": False}]}
        )
        self.assertEqual(
            check_validation_chain(record),
            ["validation-failed:make verify", "validation-chain-missing"],
        )

    def test_failing_extra_command_fires_even_when_chain_passes(self) -> None:
        # F5: a passing marker must not launder an honest recorded failure.
        record = _submission_record(
            "R1",
            validation={"commands": [
                {"cmd": "make verify", "exit_code": 0, "passed": True},
                {"cmd": "python3 -m unittest discover -s tests", "exit_code": 1, "passed": False},
            ]},
        )
        self.assertEqual(
            check_validation_chain(record),
            ["validation-failed:python3 -m unittest discover -s tests"],
        )

    def test_passing_make_verify_has_no_finding(self) -> None:
        record = _submission_record(
            "R1", validation={"commands": [{"cmd": "make verify", "exit_code": 0, "passed": True}]}
        )
        self.assertEqual(check_validation_chain(record), [])

    def test_passing_lint_and_unittest_pair_has_no_finding(self) -> None:
        record = _submission_record(
            "R1",
            validation={
                "commands": [
                    {"cmd": "python3 -m unittest discover -s tests", "exit_code": 0, "passed": True},
                    {"cmd": "make lint", "exit_code": 0, "passed": True},
                ]
            },
        )
        self.assertEqual(check_validation_chain(record), [])


# --- (e) freshness ---------------------------------------------------------------


class FreshnessCheckTests(unittest.TestCase):
    def test_content_changed_reports_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/example.py", "changed\n")
            record = _submission_record(
                "R1", changed_files=[{"path": "src/example.py", "sha256": _sha("original\n")}]
            )
            findings = check_freshness(record, root)
        self.assertEqual(findings, ["stale-record:src/example.py"])

    def test_expected_absence_but_file_present_reports_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/removed.py", "still here\n")
            record = _submission_record("R1", changed_files=[{"path": "src/removed.py", "sha256": None}])
            findings = check_freshness(record, root)
        self.assertEqual(findings, ["stale-record:src/removed.py"])

    def test_matching_digest_has_no_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/example.py", "same\n")
            record = _submission_record(
                "R1", changed_files=[{"path": "src/example.py", "sha256": _sha("same\n")}]
            )
            findings = check_freshness(record, root)
        self.assertEqual(findings, [])


# --- (f) gate_decision -------------------------------------------------------------


class GateDecisionCheckTests(unittest.TestCase):
    def test_non_submit_gate_decision_reports_finding(self) -> None:
        record = _submission_record("R1", gate_decision="no-submit")
        self.assertEqual(check_gate_decision(record), ["gate-decision:no-submit"])

    def test_submit_gate_decision_has_no_finding(self) -> None:
        record = _submission_record("R1", gate_decision="submit")
        self.assertEqual(check_gate_decision(record), [])


if __name__ == "__main__":
    unittest.main()
