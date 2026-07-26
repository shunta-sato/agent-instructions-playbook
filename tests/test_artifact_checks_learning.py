"""Tests for scripts/artifact_checks_learning.py: the retrospective-pack
shape of the `learning` checker (spec section 15 "Artifact checker" list,
one test per case, plus a few extra cases for full section 8 coverage and
one wiring check). Wiki-shape tests live in
tests/test_artifact_checks_learning_wiki.py (400-line budget split, named
per the task brief). Fixture style mirrors tests/test_artifact_lint_packs.py
(temp dirs via tempfile.TemporaryDirectory, spec dicts constructed inline
-- never through the real .agents/artifact-registry.json, which this task
does not own)."""

from __future__ import annotations

import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from scripts.artifact_checks_learning import run_checks
except ImportError:  # pragma: no cover - direct execution without repo root on sys.path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.artifact_checks_learning import run_checks

# Mirrors the registry sample in the binding spec (section 8) exactly, so
# these tests exercise the same shape the supervisor will register.
RETRO_SPEC = {
    "checker": "learning",
    "detect_dir_glob": "reports/retrospectives/*",
    "required_files": ["record.json", "report.md"],
    "forbid_fill_sentinel": True,
    "forbid_symlinks": True,
}

PACK_RELPATH = ("reports", "retrospectives", "20260726-example")
TARGET_RELPATH = "scripts/example_lint.py"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, obj) -> None:
    _write(path, json.dumps(obj))


def _good_record() -> dict:
    """One learning whose single retention action (an implemented
    `local-lint`) simultaneously satisfies closure 5.1 (deterministic +
    preventable attempt) and 5.3 (project-specific + required-before-action)
    -- a fresh copy per call so tests can mutate freely."""
    return {
        "schema_version": 1,
        "retrospective_id": "R-20260726-example",
        "title": "Example retrospective",
        "outcome": "recovered",
        "current_work_disposition": "harden-repository",
        "trigger": {"kind": "rollback", "evidence_refs": ["commit:abc123"]},
        "attempts": [
            {
                "id": "A1",
                "hypothesis_or_approach": "first approach",
                "evidence_sought": ["test output"],
                "evidence_refs": ["commit:abc123"],
                "result": "failed",
                "failure_class": "approach",
                "preventability": "preventable",
                "changed_next": "switched approach",
            },
            {
                "id": "A2",
                "hypothesis_or_approach": "second approach",
                "evidence_sought": [],
                "evidence_refs": ["commit:def456"],
                "result": "succeeded",
                "failure_class": "approach",
                "preventability": "unknown",
                "changed_next": "n/a",
            },
        ],
        "learnings": [
            {
                "id": "L1",
                "claim": "example claim",
                "evidence_refs": ["commit:abc123"],
                "causal_confidence": "plausible",
                "scope": "project-specific",
                "enforceability": "deterministic",
                "criticality": "required-before-action",
                "applies_when": ["this project"],
                "does_not_apply_when": ["other projects"],
                "existing_skill_absorption": {
                    "skills_considered": [],
                    "decision": "not-applicable",
                    "rationale": "",
                },
                "retention_actions": [
                    {
                        "kind": "local-lint",
                        "status": "implemented",
                        "target": TARGET_RELPATH,
                        "verification_commands": ["python3 " + TARGET_RELPATH],
                        "tracking_ref": "",
                        "closure_condition": "lint passes in CI",
                    }
                ],
            }
        ],
        "recurrence": {"status": "first-seen", "prior_records": []},
    }


def _good_report() -> str:
    return (
        "# Failure Learning Record\n\n"
        "Retrospective ID: R-20260726-example\n\n"
        "## Trigger and scope\n\nrollback triggered this.\n\n"
        "## Evidence sources\n\ncommit:abc123\n\n"
        "## Attempt sequence\n\nA1, A2\n\n"
        "## Failed invariants and earliest signals\n\ndetails\n\n"
        "## Contrast with the final or current attempt\n\ndetails\n\n"
        "## Learning claims\n\nL1: example claim\n\n"
        "## Promotion decisions\n\nharden-repository\n\n"
        "## Rejected non-lessons\n\nnone\n\n"
        "## Remaining unknowns\n\nnone\n\n"
        "## Closure\n\nsee retention actions\n"
    )


def _write_pack(root: Path, record: dict, report_text: str | None = None, make_target: bool = True) -> Path:
    pack = root.joinpath(*PACK_RELPATH)
    _write_json(pack / "record.json", record)
    _write(pack / "report.md", _good_report() if report_text is None else report_text)
    if make_target:
        _write(root / TARGET_RELPATH, "# example lint stub\n")
    return pack


class ArtifactCheckerTests(unittest.TestCase):
    def _check(self, record=None, report_text=None, make_target=True):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write_pack(root, record if record is not None else _good_record(), report_text, make_target)
            return run_checks(root, pack, RETRO_SPEC, {})

    # 1: normal pack passes
    def test_good_pack_passes(self) -> None:
        self.assertEqual(self._check(), [])

    # 2: record.json missing
    def test_record_json_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root.joinpath(*PACK_RELPATH)
            _write(pack / "report.md", _good_report())
            findings = run_checks(root, pack, RETRO_SPEC, {})
        self.assertIn("retro:missing-file:record.json", findings)

    # 3: report.md missing
    def test_report_md_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root.joinpath(*PACK_RELPATH)
            _write_json(pack / "record.json", _good_record())
            findings = run_checks(root, pack, RETRO_SPEC, {})
        self.assertIn("retro:missing-file:report.md", findings)

    # 4: JSON parse failure
    def test_record_json_parse_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = root.joinpath(*PACK_RELPATH)
            _write(pack / "record.json", "{not json")
            _write(pack / "report.md", _good_report())
            findings = run_checks(root, pack, RETRO_SPEC, {})
        self.assertEqual(findings, ["retro:json-parse:record.json"])

    # 5: invalid enum
    def test_invalid_enum(self) -> None:
        record = _good_record()
        record["outcome"] = "bogus"
        self.assertIn("retro:enum:outcome", self._check(record))

    # 6: duplicate Attempt ID
    def test_duplicate_attempt_id(self) -> None:
        record = _good_record()
        record["attempts"][1]["id"] = "A1"
        self.assertIn("retro:duplicate-id:attempt:A1", self._check(record))

    # 7: duplicate Learning ID
    def test_duplicate_learning_id(self) -> None:
        record = _good_record()
        record["learnings"].append(copy.deepcopy(record["learnings"][0]))
        self.assertIn("retro:duplicate-id:learning:L1", self._check(record))

    # 8: absolute target path
    def test_absolute_target_path(self) -> None:
        record = _good_record()
        record["learnings"][0]["retention_actions"][0]["target"] = "/etc/passwd"
        self.assertIn("retro:path:absolute:target:L1:0", self._check(record))

    # 9: `..` traversal
    def test_traversal_target_path(self) -> None:
        record = _good_record()
        record["learnings"][0]["retention_actions"][0]["target"] = "scripts/../../etc/passwd"
        self.assertIn("retro:path:traversal:target:L1:0", self._check(record))

    # 10: report/record ID mismatch
    def test_report_record_id_mismatch(self) -> None:
        report = _good_report().replace("R-20260726-example", "")
        self.assertIn("retro:id-mismatch:retrospective_id", self._check(report_text=report))

    # 11: report missing Attempt ID
    def test_report_missing_attempt_id(self) -> None:
        report = _good_report().replace("A1, A2", "A2")
        self.assertIn("retro:report-missing-id:attempt:A1", self._check(report_text=report))

    # 12: report missing Learning ID
    def test_report_missing_learning_id(self) -> None:
        report = _good_report().replace("L1: example claim", "example claim")
        self.assertIn("retro:report-missing-id:learning:L1", self._check(report_text=report))

    # 13: preventable + deterministic without Harness
    def test_preventable_deterministic_without_harness(self) -> None:
        record = _good_record()
        record["learnings"][0]["retention_actions"] = []
        self.assertIn("retro:closure:5.1:L1", self._check(record))

    # 14: repeated + preventable with docs-only close
    def test_repeated_preventable_docs_only(self) -> None:
        record = _good_record()
        record["recurrence"]["status"] = "repeated"
        record["learnings"][0]["retention_actions"] = [
            {"kind": "retrospective-only", "status": "not-applicable"}
        ]
        self.assertIn("retro:closure:5.2:L1", self._check(record))

    # 15: critical project-specific with Wiki-only
    def test_critical_project_specific_wiki_only(self) -> None:
        record = _good_record()
        record["learnings"][0]["criticality"] = "submit-blocking"
        record["learnings"][0]["retention_actions"] = [
            {"kind": "llm-wiki", "status": "not-applicable"}
        ]
        self.assertIn("retro:closure:5.3:L1", self._check(record))

    # 16: new-skill-candidate without absorption rationale
    def test_new_skill_candidate_without_absorption_rationale(self) -> None:
        record = _good_record()
        record["learnings"][0]["retention_actions"] = [
            {"kind": "new-skill-candidate", "status": "not-applicable"}
        ]
        record["learnings"][0]["existing_skill_absorption"] = {
            "skills_considered": [],
            "decision": "not-applicable",
            "rationale": "",
        }
        self.assertIn("retro:closure:5.4:L1", self._check(record))

    # 17: implemented target does not exist
    def test_implemented_target_missing(self) -> None:
        record = _good_record()
        record["learnings"][0]["retention_actions"][0]["target"] = "scripts/does_not_exist.py"
        self.assertIn("retro:action-target-missing:L1:0", self._check(record))

    # 18: planned action without tracking_ref
    def test_planned_action_missing_tracking_ref(self) -> None:
        record = _good_record()
        action = record["learnings"][0]["retention_actions"][0]
        action["status"] = "planned"
        action["tracking_ref"] = ""
        self.assertIn("retro:action-missing-tracking-ref:L1:0", self._check(record))

    # 19: Lint/Harness action without verification command
    def test_lint_harness_action_missing_verification_command(self) -> None:
        record = _good_record()
        record["learnings"][0]["retention_actions"][0]["verification_commands"] = []
        self.assertIn("retro:action-missing-verification:L1:0", self._check(record))

    # 20: observe-first missing signal/revisit condition
    def test_observe_first_missing_signal_and_revisit_condition(self) -> None:
        record = _good_record()
        record["learnings"][0]["retention_actions"] = [
            {
                "kind": "observe-first",
                "status": "planned",
                "artifact_path": "reports/observe/example.json",
                "tracking_ref": "track-1",
            }
        ]
        findings = self._check(record)
        self.assertIn("retro:closure:5.5:L1:0:signal", findings)
        self.assertIn("retro:closure:5.5:L1:0:revisit_condition", findings)

    # Extra: required top-level field missing (section 8, not separately
    # named in section 15 but part of the mechanical check list).
    def test_missing_top_level_field(self) -> None:
        record = _good_record()
        del record["outcome"]
        self.assertIn("retro:missing-field:outcome", self._check(record))

    # Extra: empty evidence_refs.
    def test_empty_evidence_refs(self) -> None:
        record = _good_record()
        record["attempts"][0]["evidence_refs"] = []
        self.assertIn("retro:empty-evidence-refs:attempt:A1", self._check(record))

    # Extra: fill-sentinel and symlink checks are reused (imported, not
    # copied) from artifact_checks_packs -- confirm the reuse is wired.
    def test_fill_sentinel_reused_from_packs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write_pack(root, _good_record())
            _write(pack / "notes.md", "remember: <fill>\n")
            findings = run_checks(root, pack, RETRO_SPEC, {})
        self.assertIn("retro:fill-sentinel:notes.md", findings)

    def test_symlink_reused_from_packs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write_pack(root, _good_record())
            os.symlink(pack / "record.json", pack / "link.json")
            findings = run_checks(root, pack, RETRO_SPEC, {})
        self.assertIn("retro:symlink-in-pack:link.json", findings)

    # Extra: report.md heading coverage (section 6 mandate beyond section
    # 8's literal bullet list; see the module docstring's design note).
    def test_missing_report_heading(self) -> None:
        report = _good_report().replace("## Closure\n\nsee retention actions\n", "")
        self.assertIn("retro:missing-heading:Closure", self._check(report_text=report))

    def test_unrecognized_shape_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pack = _write_pack(root, _good_record())
            with self.assertRaises(SystemExit):
                run_checks(root, pack, {"required_files": ["record.json", "report.md"]}, {})


class WiringTests(unittest.TestCase):
    def test_checker_resolves_via_lint_artifacts(self) -> None:
        try:
            from scripts import lint_artifacts
        except ImportError:  # pragma: no cover - direct execution
            import lint_artifacts  # type: ignore[no-redef]
        registry = {"artifacts": {"failure-retrospective": {"checker": "learning"}}}
        checkers = lint_artifacts.resolve_checkers(registry)
        self.assertIn("learning", checkers)
        self.assertTrue(callable(checkers["learning"]))


if __name__ == "__main__":
    unittest.main()
