from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_api_removal import DEFAULT_ALLOWED_PREFIXES, sweep


class SweepTests(unittest.TestCase):
    def _write(self, tmp: str, name: str, text: str) -> Path:
        path = Path(tmp) / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_surviving_symbol_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "src/lib.rs", "pub fn old_api() {}\n")
            hits = sweep([path], ["old_api"], DEFAULT_ALLOWED_PREFIXES)
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0][0], "old_api")

    def test_word_boundary_prevents_substring_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "src/lib.rs", "pub fn old_api_v2() {}\n")
            self.assertEqual(sweep([path], ["old_api"], DEFAULT_ALLOWED_PREFIXES), [])

    def test_ledger_and_changelog_paths_are_exempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = self._write(
                tmp, ".agents/design-ledger/function-boundaries.md", "replaced old_api\n"
            )
            changelog = self._write(tmp, "CHANGELOG.md", "removed old_api\n")
            self.assertEqual(
                sweep([ledger, changelog], ["old_api"], DEFAULT_ALLOWED_PREFIXES), []
            )

    def test_multiple_symbols_and_clean_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "src/lib.rs", "pub fn new_api() {}\n")
            self.assertEqual(
                sweep([path], ["old_api", "legacy_helper"], DEFAULT_ALLOWED_PREFIXES), []
            )


if __name__ == "__main__":
    unittest.main()
