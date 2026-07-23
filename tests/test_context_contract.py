from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.generate_agent_index import _build_index_text
from scripts.update_skill_requires import (
    check_migrated_skill,
    collect_warnings,
    fix_migrated_skill,
    is_migrated,
    parse_tier_lists,
    process_skill,
    required_files,
    split_frontmatter,
)


def make_skill(root: Path, name: str, metadata_lines: list[str], files: dict[str, list[str]]) -> Path:
    """Create <root>/<name>/SKILL.md plus reference/script/template files.

    `files` maps subdir name ("references"/"scripts"/"templates") to the
    filenames to create under it.
    """
    skill_dir = root / name
    skill_dir.mkdir()
    lines = ["---", f"name: {name}", 'description: "Use for testing."', "metadata:"]
    lines += metadata_lines
    lines += ["---", "", "## Purpose", "", "Body.", ""]
    (skill_dir / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")
    for sub, names in files.items():
        subdir = skill_dir / sub
        subdir.mkdir()
        for fname in names:
            (subdir / fname).write_text("x", encoding="utf-8")
    return skill_dir / "SKILL.md"


def tiers_for(skill_md: Path) -> dict[str, list[str]]:
    frontmatter, _ = split_frontmatter(skill_md.read_text(encoding="utf-8"), skill_md)
    return parse_tier_lists(frontmatter)


class UnmigratedCompatibilityTests(unittest.TestCase):
    def test_legacy_skill_is_not_migrated_and_regenerates_full_requires(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(
                Path(tmp),
                "legacy-skill",
                ["  short-description: Legacy"],
                {"references": ["a.md", "b.md"], "scripts": ["run.py"]},
            )
            tiers = tiers_for(skill_md)
            self.assertFalse(is_migrated(tiers))
            _, expected = process_skill(skill_md)
            self.assertIn(
                "requires:\n    - references/a.md\n    - references/b.md\n    - scripts/run.py",
                expected,
            )


class CoverageRuleTests(unittest.TestCase):
    def test_uncovered_file_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(
                Path(tmp),
                "gap-skill",
                ["  resources:", "    - references/a.md"],
                {"references": ["a.md", "b.md"]},
            )
            tiers = tiers_for(skill_md)
            self.assertTrue(is_migrated(tiers))
            errors = check_migrated_skill("gap-skill/SKILL.md", tiers, required_files(skill_md.parent))
            self.assertTrue(any("references/b.md" in e and "not listed" in e for e in errors))

    def test_dangling_entry_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(
                Path(tmp),
                "dangling-skill",
                ["  resources:", "    - references/a.md", "    - references/gone.md"],
                {"references": ["a.md"]},
            )
            tiers = tiers_for(skill_md)
            errors = check_migrated_skill("dangling-skill/SKILL.md", tiers, required_files(skill_md.parent))
            self.assertTrue(any("gone.md" in e and "does not exist" in e for e in errors))

    def test_duplicate_across_tiers_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(
                Path(tmp),
                "dup-skill",
                ["  resources:", "    - references/a.md", "  requires:", "    - references/a.md"],
                {"references": ["a.md"]},
            )
            tiers = tiers_for(skill_md)
            errors = check_migrated_skill("dup-skill/SKILL.md", tiers, required_files(skill_md.parent))
            self.assertTrue(any("more than one tier" in e for e in errors))


class TierShapeRuleTests(unittest.TestCase):
    def test_scripts_file_listed_under_resources_is_a_shape_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(
                Path(tmp),
                "shape-skill",
                ["  resources:", "    - scripts/run.py"],
                {"scripts": ["run.py"]},
            )
            tiers = tiers_for(skill_md)
            errors = check_migrated_skill("shape-skill/SKILL.md", tiers, required_files(skill_md.parent))
            self.assertTrue(any("resources entry" in e and "must live under references/" in e for e in errors))

    def test_fully_covered_migrated_skill_has_no_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(
                Path(tmp),
                "clean-skill",
                ["  requires:", "    - references/a.md", "  commands:", "    - scripts/run.py"],
                {"references": ["a.md"], "scripts": ["run.py"]},
            )
            tiers = tiers_for(skill_md)
            errors = check_migrated_skill("clean-skill/SKILL.md", tiers, required_files(skill_md.parent))
            self.assertEqual(errors, [])

    def test_requires_over_budget_is_a_warning_not_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(
                Path(tmp),
                "warn-skill",
                [
                    "  requires:",
                    "    - references/a.md",
                    "    - references/b.md",
                    "    - references/c.md",
                ],
                {"references": ["a.md", "b.md", "c.md"]},
            )
            tiers = tiers_for(skill_md)
            errors = check_migrated_skill("warn-skill/SKILL.md", tiers, required_files(skill_md.parent))
            self.assertEqual(errors, [])
            warnings = collect_warnings(tiers, "warn-skill/SKILL.md")
            self.assertTrue(any("3 entries" in w for w in warnings))


class WriteFixTests(unittest.TestCase):
    def test_write_appends_unsorted_to_existing_and_newly_created_tier_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_md = make_skill(
                Path(tmp),
                "fix-skill",
                ["  resources:", "    - references/a.md"],
                {"references": ["a.md", "b.md"], "scripts": ["run.py"]},
            )
            text = skill_md.read_text(encoding="utf-8")
            fixed = fix_migrated_skill(text, skill_md)
            self.assertIn("# UNSORTED", fixed)
            self.assertIn("references/b.md", fixed)
            self.assertIn("references/a.md", fixed)
            self.assertIn("  commands:", fixed)
            self.assertIn("scripts/run.py", fixed)
            self.assertEqual(fix_migrated_skill(fixed, skill_md), fixed)


class VisibilityIndexTests(unittest.TestCase):
    def _write_skill(self, root: Path, name: str, visibility: str | None) -> None:
        skill_dir = root / ".agents" / "skills" / name
        skill_dir.mkdir(parents=True)
        vis_line = f"  visibility: {visibility}\n" if visibility else ""
        text = (
            "---\n"
            f"name: {name}\n"
            'description: "Use for testing."\n'
            "metadata:\n"
            f"  short-description: {name} short\n"
            f"{vis_line}"
            "---\n\n## Purpose\n\nBody.\n"
        )
        (skill_dir / "SKILL.md").write_text(text, encoding="utf-8")

    def test_explicit_and_template_skills_collapse_to_one_line_each(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_skill(root, "normal-skill", None)
            self._write_skill(root, "hidden-skill", "explicit-only")
            self._write_skill(root, "tpl-skill", "template")
            index = _build_index_text(repo_root=root, max_bytes=8192)
            self.assertIn("skill|normal-skill|", index)
            self.assertNotIn("skill|hidden-skill|", index)
            self.assertNotIn("skill|tpl-skill|", index)
            self.assertIn("skills-explicit|hidden-skill", index)
            self.assertIn("skills-template|tpl-skill", index)


if __name__ == "__main__":
    unittest.main()
