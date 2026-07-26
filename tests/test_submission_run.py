"""Tests for scripts/submission_run.py's ``record`` subcommand (Wave 2 of the
lint-migration program; design record: plans/20260726-submission-evidence.md).
Fixture style mirrors tests/test_check_structure_modes.py (real git repos in a
tempdir, --working-tree / --diff-range dispatch exercised end-to-end); digest
and schema assertions are made directly against the built record dict, the
way tests/test_agent_run.py asserts against ``build_run_record``'s output."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.submission_run import add_record_parser, build_record, main


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


def _record_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    add_record_parser(subparsers)
    return parser.parse_args(["record", *argv])


def _capture(argv: list[str]) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = main(argv)
    return rc, buf.getvalue()


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class WorkingTreeCaptureTests(unittest.TestCase):
    def test_added_modified_deleted_renamed_files_captured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _write(root, "src/keep.py", "y = 1\n")
            _write(root, "src/renameme.py", "old\n")
            _commit_all(root, "base")

            _write(root, "src/app.py", "x = 2\n")  # modified
            _write(root, "src/added.py", "new\n")  # untracked/added
            (root / "src" / "keep.py").unlink()  # deleted
            subprocess.run(["git", "-C", str(root), "mv", "src/renameme.py", "src/renamed.py"], check=True, capture_output=True)

            args = _record_args(["--repo-root", str(root), "--working-tree", "--gate-decision", "submit"])
            _, record = build_record(args)

        by_path = {entry["path"]: entry["sha256"] for entry in record["changed_files"]}
        self.assertEqual(
            by_path,
            {
                "src/app.py": _sha("x = 2\n"),
                "src/added.py": _sha("new\n"),
                "src/keep.py": None,
                "src/renamed.py": _sha("old\n"),
                "src/renameme.py": None,
            },
        )
        self.assertEqual(record["base_ref"], "")

    def test_unchanged_tree_reports_no_changed_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            args = _record_args(["--repo-root", str(root), "--working-tree", "--gate-decision", "submit"])
            _, record = build_record(args)
        self.assertEqual(record["changed_files"], [])


class DiffRangeCaptureTests(unittest.TestCase):
    def test_added_modified_deleted_files_captured_between_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _write(root, "src/keep.py", "y = 1\n")
            _commit_all(root, "base")

            _write(root, "src/app.py", "x = 2\n")
            _write(root, "src/added.py", "new\n")
            (root / "src" / "keep.py").unlink()
            _commit_all(root, "change")

            args = _record_args(["--repo-root", str(root), "--diff-range", "HEAD~1..HEAD", "--gate-decision", "no-submit"])
            _, record = build_record(args)

        by_path = {entry["path"]: entry["sha256"] for entry in record["changed_files"]}
        self.assertEqual(
            by_path,
            {
                "src/app.py": _sha("x = 2\n"),
                "src/added.py": _sha("new\n"),
                "src/keep.py": None,
            },
        )
        self.assertEqual(record["base_ref"], "HEAD~1")

    def test_renamed_file_captured_as_deleted_origin_plus_added_destination(self) -> None:
        # --no-renames pairing (mirrors research_gate.py): a rename shows up as
        # its origin (deleted) and its destination (added), not collapsed away.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/renameme.py", "old\n")
            _commit_all(root, "base")
            subprocess.run(["git", "-C", str(root), "mv", "src/renameme.py", "src/renamed.py"], check=True, capture_output=True)
            _commit_all(root, "rename")

            args = _record_args(["--repo-root", str(root), "--diff-range", "HEAD~1..HEAD", "--gate-decision", "submit"])
            _, record = build_record(args)

        by_path = {entry["path"]: entry["sha256"] for entry in record["changed_files"]}
        self.assertEqual(by_path, {"src/renameme.py": None, "src/renamed.py": _sha("old\n")})

    def test_diff_range_without_dotdot_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            args = _record_args(["--repo-root", str(root), "--diff-range", "HEAD", "--gate-decision", "submit"])
            with self.assertRaises(ValueError):
                build_record(args)


class LedgerSelfExclusionTests(unittest.TestCase):
    def test_ledger_path_never_appears_in_changed_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, ".agents/runs/agent-runs.jsonl", '{"prior":"line"}\n')
            _commit_all(root, "base")
            # Simulate the ledger already being dirty (e.g. a prior un-committed
            # append) alongside one genuine change -- the ledger must still be
            # excluded, unconditionally, from THIS record's changed_files.
            with (root / ".agents/runs/agent-runs.jsonl").open("a", encoding="utf-8") as fh:
                fh.write('{"another":"line"}\n')
            _write(root, "src/new_file.py", "z = 1\n")

            args = _record_args(["--repo-root", str(root), "--working-tree", "--gate-decision", "submit"])
            _, record = build_record(args)

        paths = {entry["path"] for entry in record["changed_files"]}
        self.assertNotIn(".agents/runs/agent-runs.jsonl", paths)
        self.assertIn("src/new_file.py", paths)


class RecordSchemaTests(unittest.TestCase):
    def test_pinned_fields_are_present_and_well_formed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            _write(root, "src/app.py", "x = 2\n")

            args = _record_args([
                "--repo-root", str(root),
                "--working-tree",
                "--validation-result", "make verify", "0",
                "--cited-run", "20260726T000000Z-prior-run-abcd1234",
                "--triggered-branch", "structure-review=reports/structure.md",
                "--gate-decision", "submit",
                "--notes", "open risk noted",
            ])
            _, record = build_record(args)

        self.assertEqual(
            set(record.keys()),
            {
                "schema_version", "record_type", "run_id", "created_at", "branch",
                "base_ref", "head_commit", "changed_files", "validation",
                "cited_runs", "triggered_branches", "gate_decision", "notes",
            },
        )
        self.assertEqual(record["schema_version"], 1)
        self.assertEqual(record["record_type"], "submission_evidence")
        self.assertTrue(record["run_id"])
        self.assertTrue(record["created_at"])
        self.assertEqual(record["branch"], "main")
        self.assertRegex(record["head_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(
            record["validation"],
            {"commands": [{"cmd": "make verify", "exit_code": 0, "passed": True}]},
        )
        self.assertEqual(record["cited_runs"], ["20260726T000000Z-prior-run-abcd1234"])
        self.assertEqual(
            record["triggered_branches"],
            [{"branch": "structure-review", "artifact": "reports/structure.md"}],
        )
        self.assertEqual(record["gate_decision"], "submit")
        self.assertEqual(record["notes"], "open risk noted")

    def test_malformed_triggered_branch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            args = _record_args([
                "--repo-root", str(root), "--working-tree",
                "--triggered-branch", "missing-equals-sign",
                "--gate-decision", "submit",
            ])
            with self.assertRaises(ValueError):
                build_record(args)

    def test_blank_cited_run_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            args = _record_args([
                "--repo-root", str(root), "--working-tree",
                "--cited-run", "   ",
                "--gate-decision", "submit",
            ])
            with self.assertRaises(ValueError):
                build_record(args)


class AppendabilityTests(unittest.TestCase):
    def test_new_record_appends_without_disturbing_existing_ledger_lines(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            ledger = root / ".agents" / "runs" / "agent-runs.jsonl"
            ledger.parent.mkdir(parents=True, exist_ok=True)
            ledger.write_text('{"record_type":"agent_run","run_id":"prior"}\n', encoding="utf-8")

            _write(root, "src/added.py", "new\n")
            rc, _ = _capture(["record", "--repo-root", str(root), "--working-tree", "--gate-decision", "submit"])

            lines = ledger.read_text(encoding="utf-8").splitlines()

        self.assertEqual(rc, 0)
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0]), {"record_type": "agent_run", "run_id": "prior"})
        second = json.loads(lines[1])
        self.assertEqual(second["record_type"], "submission_evidence")


class GitFailureTests(unittest.TestCase):
    def test_working_tree_mode_fails_closed_when_not_a_git_repo(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc, _ = _capture(["record", "--repo-root", tmp, "--working-tree", "--gate-decision", "submit"])
        self.assertEqual(rc, 1)

    def test_diff_range_mode_fails_closed_on_unresolvable_range(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            _write(root, "src/app.py", "x = 1\n")
            _commit_all(root, "base")
            rc, _ = _capture([
                "record", "--repo-root", str(root),
                "--diff-range", "bogus-ref..also-bogus-ref",
                "--gate-decision", "submit",
            ])
        self.assertEqual(rc, 1)

    def test_working_tree_and_diff_range_are_mutually_exclusive(self) -> None:
        with self.assertRaises(SystemExit):
            _record_args(["--working-tree", "--diff-range", "HEAD~1..HEAD", "--gate-decision", "submit"])


if __name__ == "__main__":
    unittest.main()
