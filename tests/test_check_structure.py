from __future__ import annotations

import argparse
import tempfile
import unittest
from pathlib import Path

from scripts.check_structure import (
    check_file,
    is_entrypoint,
    rust_inline_test_line_indices,
)


def make_args(**overrides: int) -> argparse.Namespace:
    defaults = {
        "max_source_lines": 400,
        "max_entrypoint_lines": 150,
        "max_inline_test_lines": 200,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


class RustInlineTestDetectionTests(unittest.TestCase):
    def test_counts_lines_inside_cfg_test_module(self) -> None:
        lines = [
            "fn add(a: i32, b: i32) -> i32 { a + b }",
            "",
            "#[cfg(test)]",
            "mod tests {",
            "    use super::*;",
            "    #[test]",
            "    fn adds() { assert_eq!(add(1, 2), 3); }",
            "}",
            "fn after() {}",
        ]
        indices = rust_inline_test_line_indices(lines)
        self.assertEqual(indices, set(range(2, 8)))

    def test_no_cfg_test_yields_empty(self) -> None:
        lines = ["fn main() {", "    println!(\"hi\");", "}"]
        self.assertEqual(rust_inline_test_line_indices(lines), set())


class EntrypointDetectionTests(unittest.TestCase):
    def test_main_rs_and_bin_are_entrypoints(self) -> None:
        self.assertTrue(is_entrypoint(Path("src/main.rs")))
        self.assertTrue(is_entrypoint(Path("src/bin/tool.rs")))
        self.assertTrue(is_entrypoint(Path("pkg/__main__.py")))
        self.assertFalse(is_entrypoint(Path("src/lib.rs")))
        self.assertFalse(is_entrypoint(Path("src/parser.rs")))


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

    def test_oversized_source_file_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "src/parser.rs", "fn f() {}\n" * 500)
            findings = check_file(path, make_args())
            self.assertEqual([f.rule for f in findings], ["source-file-lines"])

    def test_fat_entrypoint_is_flagged(self) -> None:
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

    def test_inline_test_accumulation_is_flagged(self) -> None:
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
            self.assertEqual(
                rules,
                ["entrypoint-logic-lines", "inline-test-lines", "source-file-lines"],
            )


if __name__ == "__main__":
    unittest.main()
