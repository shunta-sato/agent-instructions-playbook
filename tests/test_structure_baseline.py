from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECK_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_structure.py"
DEFAULT_BASELINE_RELPATH = ".agents/structure-baseline.json"


def _entry(rule: str, path: str, value: int, limit: int) -> dict:
    """Build one baseline-entry dict without repeating four keys per test."""
    return {"rule": rule, "path": path, "value": value, "limit": limit}


def _write(root: Path, relpath: str, text: str) -> Path:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _write_baseline(root: Path, entries: list[dict], version: object = 1) -> Path:
    document = json.dumps({"version": version, "entries": entries})
    return _write(root, DEFAULT_BASELINE_RELPATH, document)


def _run(root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(CHECK_SCRIPT), *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def _git_track_all(root: Path) -> None:
    """Stage all files so the default ``git ls-files`` scan can see them."""
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)


class BaselineHelperTests(unittest.TestCase):
    """Black-box the real CLI, including cwd-relative filesystem behavior."""

    def test_no_baseline_present_preserves_text_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 500)
            result = _run(root, "src/parser.rs")
            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "FINDING source-file-lines src/parser.rs: 500 > 400", result.stdout
            )
            self.assertIn("structure-budget: 1 finding(s) in 1 files", result.stdout)
            self.assertNotIn("ACCEPTED-DEBT", result.stdout)
            self.assertNotIn("BASELINE-ERROR", result.stdout)

    def test_no_baseline_present_preserves_json_output_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 500)
            result = _run(root, "src/parser.rs", "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertIsInstance(payload, list)
            self.assertEqual(payload[0]["rule"], "source-file-lines")
            self.assertEqual(payload[0]["value"], 500)

    def test_exact_baseline_entry_is_accepted_debt_and_does_not_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 500)
            _write_baseline(
                root, [_entry("source-file-lines", "src/parser.rs", 500, 400)]
            )
            result = _run(root, "src/parser.rs", "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["findings"], [])
            self.assertEqual(payload["baseline_errors"], [])
            self.assertEqual(len(payload["accepted_debt"]), 1)
            self.assertEqual(payload["accepted_debt"][0]["value"], 500)

            text_result = _run(root, "src/parser.rs")
            self.assertEqual(text_result.returncode, 0)
            self.assertIn(
                "ACCEPTED-DEBT source-file-lines src/parser.rs", text_result.stdout
            )
            self.assertIn("accepted debt is not clean", text_result.stdout)

    def test_regression_worse_than_baseline_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 500)
            _write_baseline(
                root, [_entry("source-file-lines", "src/parser.rs", 450, 400)]
            )
            result = _run(root, "src/parser.rs", "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["findings"], [])
            self.assertEqual(payload["accepted_debt"], [])
            kinds = [issue["kind"] for issue in payload["baseline_errors"]]
            self.assertIn("regression", kinds)

    def test_stale_baseline_when_file_improved_but_still_over_limit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 450)
            _write_baseline(
                root, [_entry("source-file-lines", "src/parser.rs", 500, 400)]
            )
            result = _run(root, "src/parser.rs", "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            kinds = [issue["kind"] for issue in payload["baseline_errors"]]
            self.assertIn("stale-baseline", kinds)

    def test_stale_baseline_when_finding_fully_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 20)
            _write_baseline(
                root, [_entry("source-file-lines", "src/parser.rs", 500, 400)]
            )
            result = _run(root, "src/parser.rs", "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["findings"], [])
            kinds = [issue["kind"] for issue in payload["baseline_errors"]]
            self.assertIn("stale-baseline", kinds)

    def test_untouched_baseline_entry_is_neutral_on_partial_scan(self) -> None:
        """A valid entry for a file outside this invocation's scope must not
        turn an unrelated touched-file check into a failure (the bug this
        test guards against: reconciliation used to flag every unmatched
        entry as stale regardless of whether its file was even scanned).
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/legacy_big.rs", "fn f() {}\n" * 500)
            _write(root, "src/touched.rs", "fn g() {}\n" * 20)
            _write_baseline(
                root, [_entry("source-file-lines", "src/legacy_big.rs", 500, 400)]
            )
            result = _run(root, "src/touched.rs", "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["findings"], [])
            self.assertEqual(payload["baseline_errors"], [])
            self.assertEqual(payload["accepted_debt"], [])

    def test_full_default_scan_still_detects_stale_baseline_entry(self) -> None:
        """The neutral-when-unscanned behavior above must not weaken the
        full default scan: with no explicit paths, every git-tracked source
        file is in scope, so a stale entry anywhere is still caught.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/legacy_big.rs", "fn f() {}\n" * 20)
            _write_baseline(
                root, [_entry("source-file-lines", "src/legacy_big.rs", 500, 400)]
            )
            _git_track_all(root)
            result = _run(root, "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            kinds = [issue["kind"] for issue in payload["baseline_errors"]]
            self.assertIn("stale-baseline", kinds)

    def test_untouched_integrity_errors_fail_closed_unlike_stale_baseline(
        self,
    ) -> None:
        """Unlike scanned-scope staleness above, missing-path and
        threshold-mismatch are global document defects, never scope-limited:
        both must still fail closed for entries outside this invocation's
        scan, while a coexisting valid, untouched entry stays neutral.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/legacy_big.rs", "fn f() {}\n" * 500)
            _write(root, "src/mismatched.rs", "fn m() {}\n" * 500)
            _write(root, "src/touched.rs", "fn g() {}\n" * 20)
            _write_baseline(
                root,
                [
                    _entry("source-file-lines", "src/legacy_big.rs", 500, 400),
                    _entry("source-file-lines", "src/ghost.rs", 999, 400),
                    _entry("source-file-lines", "src/mismatched.rs", 500, 999),
                ],
            )
            result = _run(root, "src/touched.rs", "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            kinds = {issue["kind"] for issue in payload["baseline_errors"]}
            self.assertEqual(kinds, {"missing-path", "threshold-mismatch"})
            paths = {issue["path"] for issue in payload["baseline_errors"]}
            self.assertEqual(paths, {"src/ghost.rs", "src/mismatched.rs"})
            # The unrelated, untouched, otherwise-valid entry stays neutral:
            # not itself a baseline error, and not accepted debt either.
            self.assertEqual(payload["accepted_debt"], [])

    def test_duplicate_baseline_entries_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 500)
            _write_baseline(
                root,
                [
                    _entry("source-file-lines", "src/parser.rs", 500, 400),
                    _entry("source-file-lines", "src/parser.rs", 500, 400),
                ],
            )
            result = _run(root, "src/parser.rs", "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            kinds = [issue["kind"] for issue in payload["baseline_errors"]]
            self.assertIn("duplicate-entry", kinds)

    def test_malformed_schema_rejects_invalid_documents(self) -> None:
        cases = (
            ("missing-version", json.dumps({"entries": []})),
            ("boolean-version", json.dumps({"version": True, "entries": []})),
            ("float-version", json.dumps({"version": 1.0, "entries": []})),
            ("invalid-json", "{not valid json"),
        )
        for name, document in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                _write(root, "src/parser.rs", "fn f() {}\n" * 20)
                _write(root, DEFAULT_BASELINE_RELPATH, document)
                result = _run(root, "src/parser.rs", "--json")
                self.assertEqual(result.returncode, 1)
                payload = json.loads(result.stdout)
                kinds = [issue["kind"] for issue in payload["baseline_errors"]]
                self.assertIn("malformed-schema", kinds)

    def test_missing_path_entry_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 20)
            _write_baseline(
                root, [_entry("source-file-lines", "src/does_not_exist.rs", 500, 400)]
            )
            result = _run(root, "src/parser.rs", "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            kinds = [issue["kind"] for issue in payload["baseline_errors"]]
            self.assertIn("missing-path", kinds)

    def test_non_source_path_entry_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 20)
            _write(root, "README.md", "not source\n")
            _write_baseline(
                root, [_entry("source-file-lines", "README.md", 500, 400)]
            )
            result = _run(root, "src/parser.rs", "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            kinds = [issue["kind"] for issue in payload["baseline_errors"]]
            self.assertIn("missing-path", kinds)

    def test_unknown_rule_entry_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 20)
            _write_baseline(
                root, [_entry("totally-made-up-rule", "src/parser.rs", 500, 400)]
            )
            result = _run(root, "src/parser.rs", "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            kinds = [issue["kind"] for issue in payload["baseline_errors"]]
            self.assertIn("unknown-rule", kinds)

    def test_threshold_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 500)
            _write_baseline(
                root, [_entry("source-file-lines", "src/parser.rs", 500, 400)]
            )
            result = _run(root, "src/parser.rs", "--json", "--max-source-lines", "350")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            kinds = [issue["kind"] for issue in payload["baseline_errors"]]
            self.assertIn("threshold-mismatch", kinds)

    def test_new_finding_without_baseline_entry_still_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 500)
            _write(root, "src/other.rs", "fn g() {}\n" * 500)
            _write_baseline(
                root, [_entry("source-file-lines", "src/parser.rs", 500, 400)]
            )
            result = _run(root, "src/parser.rs", "src/other.rs", "--json")
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["baseline_errors"], [])
            self.assertEqual(len(payload["findings"]), 1)
            self.assertEqual(payload["findings"][0]["path"], "src/other.rs")
            self.assertEqual(len(payload["accepted_debt"]), 1)

    def test_explicit_baseline_override_path_is_used(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 500)
            _write(
                root,
                "custom/baseline.json",
                json.dumps(
                    {
                        "version": 1,
                        "entries": [
                            _entry("source-file-lines", "src/parser.rs", 500, 400)
                        ],
                    }
                ),
            )
            result = _run(
                root, "src/parser.rs", "--json", "--baseline", "custom/baseline.json"
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["baseline_path"], "custom/baseline.json")
            self.assertEqual(len(payload["accepted_debt"]), 1)

    def test_explicit_empty_baseline_is_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 20)
            result = _run(root, "src/parser.rs", "--baseline", "")
            self.assertEqual(result.returncode, 2)
            self.assertIn("usage error", result.stderr)

    def test_explicit_baseline_missing_file_is_usage_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/parser.rs", "fn f() {}\n" * 20)
            result = _run(root, "src/parser.rs", "--baseline", "does/not/exist.json")
            self.assertEqual(result.returncode, 2)
            self.assertIn("usage error", result.stderr)
            self.assertIn("does/not/exist.json", result.stderr)

    def test_json_output_distinguishes_categories_when_mixed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "src/accepted.rs", "fn f() {}\n" * 500)
            _write(root, "src/regressed.rs", "fn g() {}\n" * 500)
            _write(root, "src/new.rs", "fn h() {}\n" * 500)
            _write_baseline(
                root,
                [
                    _entry("source-file-lines", "src/accepted.rs", 500, 400),
                    _entry("source-file-lines", "src/regressed.rs", 450, 400),
                ],
            )
            result = _run(
                root, "src/accepted.rs", "src/regressed.rs", "src/new.rs", "--json"
            )
            self.assertEqual(result.returncode, 1)
            payload = json.loads(result.stdout)
            self.assertEqual({f["path"] for f in payload["findings"]}, {"src/new.rs"})
            self.assertEqual(
                {f["path"] for f in payload["accepted_debt"]}, {"src/accepted.rs"}
            )
            self.assertEqual(
                {i["path"] for i in payload["baseline_errors"]}, {"src/regressed.rs"}
            )
            # Accepted debt must never be reported as if it were clean.
            self.assertNotIn("clean", json.dumps(payload).lower())


if __name__ == "__main__":
    unittest.main()
