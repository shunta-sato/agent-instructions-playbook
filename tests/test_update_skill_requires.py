from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.update_skill_requires import process_skill, required_files

SKILL_TEXT = """---
name: sample-skill
description: "Use when sampling."
metadata:
  short-description: Sample
---

## Purpose

Sample body.
"""


def make_skill(tmp: str, with_refs: bool) -> Path:
    skill_dir = Path(tmp) / "sample-skill"
    skill_dir.mkdir()
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(SKILL_TEXT, encoding="utf-8")
    if with_refs:
        (skill_dir / "references").mkdir()
        (skill_dir / "references" / "b.md").write_text("b", encoding="utf-8")
        (skill_dir / "references" / "a.md").write_text("a", encoding="utf-8")
        (skill_dir / "templates").mkdir()
        (skill_dir / "templates" / "t.md").write_text("t", encoding="utf-8")
    return skill_md


class RequiredFilesTests(unittest.TestCase):
    def test_lists_reference_and_template_files_sorted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(tmp, with_refs=True)
            self.assertEqual(
                required_files(skill_md.parent),
                ["references/a.md", "references/b.md", "templates/t.md"],
            )

    def test_empty_without_subdirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(tmp, with_refs=False)
            self.assertEqual(required_files(skill_md.parent), [])


class ProcessSkillTests(unittest.TestCase):
    def test_inserts_requires_under_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(tmp, with_refs=True)
            _, expected = process_skill(skill_md)
            self.assertIn(
                "metadata:\n  short-description: Sample\n  requires:\n"
                "    - references/a.md\n    - references/b.md\n    - templates/t.md\n---",
                expected,
            )
            self.assertIn("## Purpose", expected)

    def test_idempotent_after_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(tmp, with_refs=True)
            _, expected = process_skill(skill_md)
            skill_md.write_text(expected, encoding="utf-8")
            current, expected_again = process_skill(skill_md)
            self.assertEqual(current, expected_again)

    def test_no_requires_block_when_no_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(tmp, with_refs=False)
            current, expected = process_skill(skill_md)
            self.assertEqual(current, expected)
            self.assertNotIn("requires:", expected)

    def test_stale_entry_is_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(tmp, with_refs=True)
            stale = SKILL_TEXT.replace(
                "  short-description: Sample",
                "  short-description: Sample\n  requires:\n    - references/gone.md",
            )
            skill_md.write_text(stale, encoding="utf-8")
            _, expected = process_skill(skill_md)
            self.assertNotIn("gone.md", expected)
            self.assertIn("references/a.md", expected)


if __name__ == "__main__":
    unittest.main()
