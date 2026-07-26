"""Tests for scripts/init_artifact.py: multi-file pack support (the new
"failure-retrospective" kind) plus a regression check that the existing
single-file kinds are unaffected. Fixture style mirrors
tests/test_agent_run.py and tests/test_artifact_lint_packs.py: real temp
directories via tempfile.TemporaryDirectory, no mocking, functions
imported directly and called with an explicit repo_root rather than via
the real repository tree or a subprocess.

Per the task brief, the real failure-retrospective templates are owned by
a sibling workstream landing in the same wave. Each test scaffolds its own
tiny stand-in template fixtures under a temp repo_root instead of
depending on those real files existing yet; scripts/init_artifact.py
resolves template paths relative to the repo_root it is given, so this
requires no change to the production code path.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

try:
    from scripts.init_artifact import create_artifact, validate_slug
except ImportError:  # pragma: no cover - direct execution without repo root on sys.path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.init_artifact import create_artifact, validate_slug


RECORD_TEMPLATE = '{\n  "schema_version": 1,\n  "retrospective_id": "R-TEMPLATE"\n}\n'
REPORT_TEMPLATE = "# Failure Learning Record\n\n## Trigger and scope\n"
EXECPLAN_TEMPLATE = "# ExecPlan Template\n"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _scaffold_failure_retrospective_templates(root: Path) -> None:
    _write(root / ".agents/skills/failure-retrospective/templates/record.json", RECORD_TEMPLATE)
    _write(root / ".agents/skills/failure-retrospective/templates/report.md", REPORT_TEMPLATE)


def _pack_paths(root: Path, slug: str) -> tuple[Path, Path]:
    pack_dir = root / "reports/retrospectives" / slug
    return pack_dir / "record.json", pack_dir / "report.md"


class FailureRetrospectivePackTests(unittest.TestCase):
    def test_creates_both_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_failure_retrospective_templates(root)
            record_path, report_path = _pack_paths(root, "20260726-example")

            created = create_artifact(root, "failure-retrospective", "20260726-example")

            self.assertEqual(set(created), {record_path, report_path})
            self.assertEqual(record_path.read_text(encoding="utf-8"), RECORD_TEMPLATE)
            self.assertEqual(report_path.read_text(encoding="utf-8"), REPORT_TEMPLATE)

    def test_refuses_to_overwrite_non_empty_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_failure_retrospective_templates(root)
            record_path, report_path = _pack_paths(root, "20260726-example")
            # report.md (second in spec order) pre-exists with foreign,
            # non-empty content; record.json does not exist yet.
            _write(report_path, "pre-existing report, not from template\n")

            with self.assertRaises(FileExistsError):
                create_artifact(root, "failure-retrospective", "20260726-example")

            # No partial creation: record.json must not be left behind
            # once report.md's conflict aborts the invocation.
            self.assertFalse(record_path.exists())
            # The pre-existing, non-empty file is untouched, not clobbered.
            self.assertEqual(
                report_path.read_text(encoding="utf-8"),
                "pre-existing report, not from template\n",
            )

    def test_force_overwrites_both_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_failure_retrospective_templates(root)
            record_path, report_path = _pack_paths(root, "20260726-example")
            _write(record_path, "stale record\n")
            _write(report_path, "stale report\n")

            create_artifact(root, "failure-retrospective", "20260726-example", force=True)

            self.assertEqual(record_path.read_text(encoding="utf-8"), RECORD_TEMPLATE)
            self.assertEqual(report_path.read_text(encoding="utf-8"), REPORT_TEMPLATE)

    def test_no_partial_creation_when_second_target_is_a_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_failure_retrospective_templates(root)
            record_path, report_path = _pack_paths(root, "20260726-example")
            # Induced failure: report.md's target already exists as a
            # directory, not a file.
            report_path.mkdir(parents=True)

            with self.assertRaises(IsADirectoryError):
                create_artifact(root, "failure-retrospective", "20260726-example")

            self.assertFalse(record_path.exists())
            self.assertTrue(report_path.is_dir())

    def test_output_flag_rejected_for_pack_kind(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_failure_retrospective_templates(root)

            with self.assertRaises(ValueError):
                create_artifact(
                    root, "failure-retrospective", "20260726-example", output="custom.json"
                )

            self.assertFalse((root / "reports").exists())


class UnsafeSlugTests(unittest.TestCase):
    def test_parent_traversal_slug_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_slug("../x")

    def test_absolute_slug_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_slug("/abs")

    def test_embedded_separator_slug_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_slug("a/b")

    def test_unsafe_slug_fails_before_creating_anything(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_failure_retrospective_templates(root)

            with self.assertRaises(ValueError):
                create_artifact(root, "failure-retrospective", "../escape")

            self.assertFalse((root / "reports").exists())


class SingleFileKindRegressionTests(unittest.TestCase):
    def test_execplan_kind_still_works(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "plans/_template_execplan.md", EXECPLAN_TEMPLATE)

            created = create_artifact(root, "execplan", "my-plan")

            expected_path = root / "plans/my-plan.md"
            self.assertEqual(created, [expected_path])
            self.assertEqual(expected_path.read_text(encoding="utf-8"), EXECPLAN_TEMPLATE)


if __name__ == "__main__":
    unittest.main()
