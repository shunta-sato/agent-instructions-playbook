from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from scripts.check_context_budget import (
    BUDGET_COMMON,
    REACH_BUDGET_LINES,
    SKILL_MD_SOFT_MAX_LINES,
    check_common_path,
    check_skill,
    main,
)


def _capture(fn, *args) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*args)
    return rc, buf.getvalue()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_skill(
    root: Path, name: str, requires: list[str], extra_body_lines: int, ref_lines: dict[str, int]
) -> Path:
    """Write <root>/.agents/skills/<name>/SKILL.md with a `requires` block
    plus `extra_body_lines` filler lines, and each `ref_lines` entry as a
    file with that many lines."""
    fm = ["---", f"name: {name}", 'description: "Use for testing."', "metadata:"]
    if requires:
        fm.append("  requires:")
        fm += [f"    - {r}" for r in requires]
    fm.append("---")
    body = "\n".join(f"line {i}" for i in range(extra_body_lines))
    skill_md = root / ".agents" / "skills" / name / "SKILL.md"
    _write(skill_md, "\n".join(fm) + "\n" + body + "\n")
    for rel, n in ref_lines.items():
        _write(skill_md.parent / rel, "\n".join(f"x{i}" for i in range(n)) + "\n")
    return skill_md


def _base_common_path(root: Path) -> None:
    """AGENTS.md + minimal dev-workflow/quality-gate, well under budget."""
    _write(root / "AGENTS.md", "line\n" * 10)
    for name in ("dev-workflow", "quality-gate"):
        _write_skill(root, name, [], 5, {})


class CommonPathBudgetTests(unittest.TestCase):
    def test_over_budget_common_path_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root / "AGENTS.md", "line\n" * (BUDGET_COMMON + 50))
            findings = check_common_path(root)
        self.assertEqual([f.rule for f in findings], ["common-path-budget"])

    def test_under_budget_common_path_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _base_common_path(root)
            self.assertEqual(check_common_path(root), [])


class RequiresCountBudgetTests(unittest.TestCase):
    def test_more_than_two_requires_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_md = _write_skill(
                root,
                "many-requires",
                ["references/a.md", "references/b.md", "references/c.md"],
                10,
                {"references/a.md": 5, "references/b.md": 5, "references/c.md": 5},
            )
            findings = check_skill(skill_md, root)
        self.assertIn("requires-count", [f.rule for f in findings])


class SkillMdLinesBudgetTests(unittest.TestCase):
    def test_oversized_skill_md_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_md = _write_skill(root, "long-skill", [], SKILL_MD_SOFT_MAX_LINES + 20, {})
            findings = check_skill(skill_md, root)
        self.assertIn("skill-md-lines", [f.rule for f in findings])


class ReachBudgetTests(unittest.TestCase):
    def test_requires_files_push_reach_over_budget(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_md = _write_skill(
                root,
                "heavy-skill",
                ["references/a.md", "references/b.md"],
                20,
                {"references/a.md": REACH_BUDGET_LINES, "references/b.md": REACH_BUDGET_LINES},
            )
            findings = check_skill(skill_md, root)
        self.assertIn("reach-budget", [f.rule for f in findings])


class PassingTreeTests(unittest.TestCase):
    def test_clean_tree_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _base_common_path(root)
            _write_skill(root, "other-skill", ["references/a.md"], 20, {"references/a.md": 20})
            rc, output = _capture(main, ["--repo-root", str(root)])
        self.assertEqual(rc, 0)
        self.assertIn("context-budget: pass", output)

    def test_dirty_tree_exits_one_and_reports_all_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _base_common_path(root)
            _write_skill(
                root,
                "bad-skill",
                ["references/a.md", "references/b.md", "references/c.md"],
                SKILL_MD_SOFT_MAX_LINES + 20,
                {"references/a.md": 5, "references/b.md": 5, "references/c.md": 5},
            )
            rc, output = _capture(main, ["--repo-root", str(root)])
        self.assertEqual(rc, 1)
        self.assertIn("requires-count", output)
        self.assertIn("skill-md-lines", output)


if __name__ == "__main__":
    unittest.main()
