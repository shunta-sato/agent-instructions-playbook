from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path

from scripts.check_structure import (
    check_file,
    is_entrypoint,
    load_structure_waivers,
    partition_waived_findings,
    rust_inline_test_line_indices,
)


def make_args(**overrides: int | str) -> argparse.Namespace:
    defaults: dict[str, int | str] = {
        "mode": "strict",
        "max_source_lines": 400,
        "max_entrypoint_lines": 150,
        "max_inline_test_lines": 200,
        "hard_source_lines": 1500,
        "hard_entrypoint_lines": 400,
        "hard_inline_test_lines": 800,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


class RustInlineTestDetectionTests(unittest.TestCase):
    def test_counts_lines_inside_cfg_test_module(self) -> None:
        lines = [
            "fn add(a: i32, b: i32) -> i32 { a + b }", "", "#[cfg(test)]",
            "mod tests {", "    use super::*;", "    #[test]",
            "    fn adds() { assert_eq!(add(1, 2), 3); }", "}", "fn after() {}",
        ]
        self.assertEqual(rust_inline_test_line_indices(lines), set(range(2, 8)))

    def test_no_cfg_test_yields_empty(self) -> None:
        self.assertEqual(rust_inline_test_line_indices(["fn main() {}"]), set())


class EntrypointDetectionTests(unittest.TestCase):
    def test_main_rs_and_bin_are_entrypoints(self) -> None:
        self.assertTrue(is_entrypoint(Path("src/main.rs")))
        self.assertTrue(is_entrypoint(Path("src/bin/tool.rs")))
        self.assertTrue(is_entrypoint(Path("pkg/__main__.py")))
        self.assertFalse(is_entrypoint(Path("src/lib.rs")))


class CheckFileTests(unittest.TestCase):
    def _write(self, tmp: str, name: str, text: str) -> Path:
        path = Path(tmp) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_clean_small_file_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "src/parser.rs", "fn parse() {}\n" * 20)
            self.assertEqual(check_file(path, make_args()), [])

    def test_strict_mode_flags_advisory_threshold_as_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "src/parser.rs", "fn f() {}\n" * 500)
            findings = check_file(path, make_args())
            self.assertEqual([(f.rule, f.severity) for f in findings], [("source-file-lines", "blocking")])

    def test_feature_mode_reports_advisory_without_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "src/parser.rs", "fn f() {}\n" * 700)
            findings = check_file(path, make_args(mode="feature", max_source_lines=600))
            self.assertEqual([(f.rule, f.severity) for f in findings], [("source-file-lines", "advisory")])

    def test_feature_mode_hard_guardrail_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "src/parser.rs", "fn f() {}\n" * 1600)
            findings = check_file(path, make_args(mode="feature", max_source_lines=600))
            self.assertEqual([(f.rule, f.severity) for f in findings], [("source-file-lines", "blocking")])
            self.assertEqual(findings[0].limit, 1500)

    def test_fat_entrypoint_is_flagged_in_strict_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "src/main.rs", "let x = 1;\n" * 200)
            findings = check_file(path, make_args())
            self.assertIn("entrypoint-logic-lines", [f.rule for f in findings])

    def test_entrypoint_logic_excludes_inline_tests_and_comments(self) -> None:
        body = "fn main() { run(); }\n" + "// comment\n" * 50
        tests = "#[cfg(test)]\nmod tests {\n" + "    fn t() {}\n" * 100 + "}\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "src/main.rs", body + tests)
            findings = check_file(path, make_args())
            self.assertNotIn("entrypoint-logic-lines", [f.rule for f in findings])

    def test_inline_test_accumulation_is_flagged_in_strict_mode(self) -> None:
        tests = "#[cfg(test)]\nmod tests {\n" + "    fn t() {}\n" * 250 + "}\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "src/main.rs", "fn main() {}\n" + tests)
            findings = check_file(path, make_args())
            self.assertIn("inline-test-lines", [f.rule for f in findings])

    def test_monolithic_main_rs_scenario_flags_all_three(self) -> None:
        logic = "fn work() { do_it(); }\n" * 300
        tests = "#[cfg(test)]\nmod tests {\n" + "    fn t() {}\n" * 250 + "}\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "src/main.rs", logic + tests)
            rules = sorted(f.rule for f in check_file(path, make_args()))
            self.assertEqual(rules, ["entrypoint-logic-lines", "inline-test-lines", "source-file-lines"])


class StructureWaiverTests(unittest.TestCase):
    def _write(self, tmp: str, name: str, text: str) -> Path:
        path = Path(tmp) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def _write_policy(self, tmp: str, structure_waivers: list[dict]) -> None:
        policy_path = Path(tmp) / ".agents" / "project-policy.yml"
        policy_path.parent.mkdir(parents=True, exist_ok=True)
        policy_path.write_text(json.dumps({"schema_version": 1, "structure_waivers": structure_waivers}), encoding="utf-8")

    def test_waived_path_produces_no_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_policy(tmp, [{"path": "experiments/", "reason": "disposable probe code"}])
            path = self._write(tmp, "experiments/probe.py", "x = 1\n" * 1600)
            findings = check_file(path, make_args(mode="feature", max_source_lines=600))
            kept, waived = partition_waived_findings(findings, root, load_structure_waivers(root))
            self.assertEqual(kept, [])
            self.assertEqual(waived, [("experiments/probe.py", "disposable probe code")])

    def test_non_waived_path_still_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_policy(tmp, [{"path": "experiments/", "reason": "disposable probe code"}])
            path = self._write(tmp, "src/parser.py", "x = 1\n" * 1600)
            findings = check_file(path, make_args(mode="feature", max_source_lines=600))
            kept, waived = partition_waived_findings(findings, root, load_structure_waivers(root))
            self.assertEqual(len(kept), 1)
            self.assertEqual(waived, [])


if __name__ == "__main__":
    unittest.main()
