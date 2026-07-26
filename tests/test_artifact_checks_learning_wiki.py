"""Tests for scripts/artifact_checks_learning_wiki.py: the LLM Wiki shape of
the `learning` checker (spec section 15 "LLM Wiki" list, one test each, plus
one extra for the duplicate-link rule named in the skill reference doc).
Split from tests/test_artifact_checks_learning.py per the task brief (named
pairing with the checker module split). Fixture style mirrors
tests/test_artifact_lint_packs.py (temp dirs, spec dicts constructed
inline)."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from scripts.artifact_checks_learning_wiki import run_checks
except ImportError:  # pragma: no cover - direct execution without repo root on sys.path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from scripts.artifact_checks_learning_wiki import run_checks

# Mirrors the registry sample in the binding spec (section 8) exactly.
WIKI_SPEC = {
    "checker": "learning",
    "detect_dir": ".agent/wiki",
    "required_files": ["README.md", "index.md"],
    "forbid_fill_sentinel": True,
    "forbid_symlinks": True,
}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _good_entry() -> str:
    return (
        "# Component A knowledge\n\n"
        "Status: active\n"
        "Confidence: confirmed\n"
        "Last verified: 2026-07-20\n"
        "Revisit when: the component API changes\n\n"
        "## Scope\n\ndetails\n\n"
        "## Project knowledge\n\ndetails\n\n"
        "## Applies when\n\ndetails\n\n"
        "## Does not apply when\n\ndetails\n\n"
        "## Operational consequence\n\ndetails\n\n"
        "## Evidence\n\ndetails\n\n"
        "## Confidence\n\ndetails\n\n"
        "## Freshness\n\ndetails\n\n"
        "## Promoted learning\n\nnot-applicable\n"
    )


def _write_wiki(root: Path, entry_text: str | None = None, index_text: str | None = None) -> Path:
    wiki = root / ".agent" / "wiki"
    _write(wiki / "README.md", "# LLM Wiki\n\nProject-specific knowledge, one page per component.\n")
    _write(wiki / "component-a.md", _good_entry() if entry_text is None else entry_text)
    _write(wiki / "index.md", "# Wiki Index\n\n- [Component A](component-a.md)\n" if index_text is None else index_text)
    return wiki


class LlmWikiCheckerTests(unittest.TestCase):
    def _check(self, entry_text=None, index_text=None):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wiki = _write_wiki(root, entry_text, index_text)
            return run_checks(root, wiki, WIKI_SPEC, {})

    # 1: normal entry passes
    def test_good_entry_passes(self) -> None:
        self.assertEqual(self._check(), [])

    # 2: required heading missing
    def test_missing_required_heading(self) -> None:
        entry = _good_entry().replace("## Freshness\n\ndetails\n\n", "")
        self.assertIn("wiki:heading:component-a.md:Freshness", self._check(entry_text=entry))

    # 3: orphan entry (not linked from index.md)
    def test_orphan_entry(self) -> None:
        self.assertIn(
            "wiki:orphan:component-a.md",
            self._check(index_text="# Wiki Index\n\nno entries linked yet.\n"),
        )

    # 4: index dead link
    def test_index_dead_link(self) -> None:
        index = "# Wiki Index\n\n- [Component A](component-a.md)\n- [Ghost](ghost.md)\n"
        self.assertIn("wiki:dead-link:index.md:ghost.md", self._check(index_text=index))

    # 5: symlink (reused from artifact_checks_packs)
    def test_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wiki = _write_wiki(root)
            os.symlink(wiki / "component-a.md", wiki / "link.md")
            findings = run_checks(root, wiki, WIKI_SPEC, {})
        self.assertIn("wiki:symlink-in-pack:link.md", findings)

    # 6: `<fill>` sentinel (reused from artifact_checks_packs)
    def test_fill_sentinel(self) -> None:
        entry = _good_entry().replace("## Scope\n\ndetails\n\n", "## Scope\n\n<fill>\n\n")
        self.assertIn("wiki:fill-sentinel:component-a.md", self._check(entry_text=entry))

    # 7: invalid Status
    def test_invalid_status(self) -> None:
        entry = _good_entry().replace("Status: active\n", "Status: retired\n")
        self.assertIn("wiki:invalid-value:component-a.md:status", self._check(entry_text=entry))

    # 8: invalid Confidence
    def test_invalid_confidence(self) -> None:
        entry = _good_entry().replace("Confidence: confirmed\n", "Confidence: maybe\n")
        self.assertIn("wiki:invalid-value:component-a.md:confidence", self._check(entry_text=entry))

    # 9: Last verified missing
    def test_last_verified_missing(self) -> None:
        entry = _good_entry().replace("Last verified: 2026-07-20\n", "")
        self.assertIn("wiki:missing-field:component-a.md:last-verified", self._check(entry_text=entry))

    # 10: Revisit when missing
    def test_revisit_when_missing(self) -> None:
        entry = _good_entry().replace("Revisit when: the component API changes\n", "")
        self.assertIn("wiki:missing-field:component-a.md:revisit-when", self._check(entry_text=entry))

    # Extra: Last verified present but not YYYY-MM-DD shaped.
    def test_last_verified_bad_shape(self) -> None:
        entry = _good_entry().replace("Last verified: 2026-07-20\n", "Last verified: July 2026\n")
        self.assertIn("wiki:invalid-value:component-a.md:last-verified", self._check(entry_text=entry))

    # Extra: duplicate links in index.md (spec section 7 operating rules:
    # "orphan entries, dead links, and duplicate links are lint findings").
    def test_duplicate_link(self) -> None:
        index = (
            "# Wiki Index\n\n"
            "- [Component A](component-a.md)\n"
            "- [Component A again](component-a.md)\n"
        )
        self.assertIn("wiki:duplicate-link:component-a.md", self._check(index_text=index))

    # Extra: required_files reuse (README.md/index.md via artifact_checks_packs).
    def test_required_file_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wiki = root / ".agent" / "wiki"
            _write(wiki / "component-a.md", _good_entry())
            findings = run_checks(root, wiki, WIKI_SPEC, {})
        self.assertIn("wiki:missing-file:README.md", findings)
        self.assertIn("wiki:missing-file:index.md", findings)


class RecursiveEntryTests(unittest.TestCase):
    def test_nested_entry_is_checked(self) -> None:
        # F9: a subdirectory page must not silently escape the entry contract.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wiki = root / ".agent" / "wiki"
            (wiki / "sub").mkdir(parents=True)
            (wiki / "README.md").write_text("# Wiki\n")
            (wiki / "index.md").write_text("# Index\n\n- [p](sub/page.md)\n")
            (wiki / "sub" / "page.md").write_text("# Page\n\nStatus: bogus\n")
            findings = run_checks(root, wiki, WIKI_SPEC, {})
        self.assertTrue(any("sub/page.md" in f for f in findings), findings)


class OrderedHeadingTests(unittest.TestCase):
    def test_reversed_section_order_is_a_finding(self) -> None:
        # Codex C5: set membership must not accept a reversed entry.
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wiki = root / ".agent" / "wiki"
            wiki.mkdir(parents=True)
            (wiki / "README.md").write_text("# Wiki\n")
            (wiki / "index.md").write_text("# Index\n\n- [e](entry.md)\n")
            body = (
                "# T\n\n## Promoted learning\nx\n\n## Freshness\n"
                "Status: active\nConfidence: confirmed\nLast verified: 2026-07-27\nRevisit when: x\n\n"
                "## Confidence\nx\n\n## Evidence\nx\n\n## Operational consequence\nx\n\n"
                "## Does not apply when\nx\n\n## Applies when\nx\n\n"
                "## Project knowledge\nx\n\n## Scope\nx\n"
            )
            (wiki / "entry.md").write_text(body)
            findings = run_checks(root, wiki, WIKI_SPEC, {})
        self.assertTrue(any(f.startswith("wiki:heading:entry.md:") for f in findings), findings)


if __name__ == "__main__":
    unittest.main()
