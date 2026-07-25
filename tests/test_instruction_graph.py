from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts.lint_instruction_graph import collect_findings, main


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_skill(
    root: Path,
    name: str,
    body: str,
    requires: list[str] | None = None,
    commands: list[str] | None = None,
    extra_files: dict[str, str] | None = None,
) -> Path:
    fm = ["---", f"name: {name}", 'description: "Use for testing."', "metadata:"]
    for field, items in (("requires", requires), ("commands", commands)):
        if items:
            fm.append(f"  {field}:")
            fm += [f"    - {item}" for item in items]
    fm.append("---")
    skill_md = root / ".agents" / "skills" / name / "SKILL.md"
    _write(skill_md, "\n".join(fm) + "\n\n" + body + "\n")
    for rel, content in (extra_files or {}).items():
        _write(skill_md.parent / rel, content)
    return skill_md


@contextlib.contextmanager
def _tmp_root():
    with tempfile.TemporaryDirectory() as tmp:
        yield Path(tmp)


def _capture_main(root: Path) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = main(["--repo-root", str(root)])
    return rc, buf.getvalue()


def _rules(root: Path) -> list[str]:
    return [f.rule for f in collect_findings(root)]


class DanglingSkillRefTests(unittest.TestCase):
    def test_unknown_dollar_skill_is_flagged(self) -> None:
        with _tmp_root() as root:
            _write_skill(root, "alpha", "See `$nonexistent-skill` for details.")
            self.assertIn("dangling-skill-ref", _rules(root))

    def test_known_dollar_skill_passes(self) -> None:
        with _tmp_root() as root:
            _write_skill(root, "alpha", "See `$beta` for details.")
            _write_skill(root, "beta", "Nothing to see here.")
            self.assertNotIn("dangling-skill-ref", _rules(root))

    def test_dollar_skill_ref_inside_fence_is_ignored(self) -> None:
        with _tmp_root() as root:
            body = "Example output:\n\n```markdown\nUse `$made-up-skill` here.\n```\n"
            _write_skill(root, "alpha", body)
            self.assertNotIn("dangling-skill-ref", _rules(root))


class DanglingPathTests(unittest.TestCase):
    def test_missing_reference_path_is_flagged(self) -> None:
        with _tmp_root() as root:
            _write_skill(root, "alpha", "See `references/missing.md` for details.")
            self.assertIn("dangling-path", _rules(root))

    def test_existing_reference_path_passes(self) -> None:
        with _tmp_root() as root:
            _write_skill(
                root, "alpha", "See `references/present.md` for details.",
                requires=["references/present.md"],
                extra_files={"references/present.md": "# Present\n"},
            )
            self.assertNotIn("dangling-path", _rules(root))

    def test_placeholder_and_output_artifact_tokens_are_ignored(self) -> None:
        with _tmp_root() as root:
            body = (
                "See `docs/<area>/<topic>.md`, `references/*.md`, "
                "`plans/{slug}.md`, `plans/N.md`, and `auto_review.json` "
                "for the pattern."
            )
            _write_skill(root, "alpha", body)
            self.assertNotIn("dangling-path", _rules(root))


class DanglingAnchorTests(unittest.TestCase):
    def test_unresolvable_numeric_anchor_is_flagged(self) -> None:
        with _tmp_root() as root:
            _write_skill(
                root, "alpha", "Full rule: `references/foo.md` §9.",
                requires=["references/foo.md"],
                extra_files={"references/foo.md": "# Foo\n\n## 1) Something\n"},
            )
            self.assertIn("dangling-anchor", _rules(root))

    def test_resolvable_numeric_anchor_passes(self) -> None:
        with _tmp_root() as root:
            _write_skill(
                root, "alpha", "Full rule: `references/foo.md` §1.",
                requires=["references/foo.md"],
                extra_files={"references/foo.md": "# Foo\n\n## 1) Something\n"},
            )
            self.assertNotIn("dangling-anchor", _rules(root))

    def test_word_anchor_matches_line_marker(self) -> None:
        with _tmp_root() as root:
            _write_skill(
                root, "alpha", "Full rule: `references/foo.md` §sweep rule.",
                requires=["references/foo.md"],
                extra_files={"references/foo.md": "Sweep rule: do the whole pass.\n"},
            )
            self.assertNotIn("dangling-anchor", _rules(root))

    def test_bare_section_number_without_preceding_path_is_out_of_scope(self) -> None:
        with _tmp_root() as root:
            _write_skill(root, "alpha", "Apply the §9 criteria from this section.")
            self.assertNotIn("dangling-anchor", _rules(root))

    def test_cross_skill_bare_name_anchor_resolves(self) -> None:
        with _tmp_root() as root:
            _write_skill(root, "alpha", "See `beta` §2 Comments for detail.")
            _write_skill(
                root, "beta", "intro",
                requires=["references/beta.md"],
                extra_files={"references/beta.md": "# Beta\n\n## 2. Comments\n"},
            )
            self.assertNotIn("dangling-anchor", _rules(root))


class BadCommandTests(unittest.TestCase):
    def test_missing_and_wrong_extension_commands_are_flagged(self) -> None:
        with _tmp_root() as root:
            _write_skill(
                root, "alpha", "Run it.",
                commands=["scripts/missing.py", "scripts/tool.txt"],
                extra_files={"scripts/tool.txt": "not a script"},
            )
            findings = _rules(root)
            self.assertEqual(findings.count("bad-command"), 2)

    def test_existing_py_command_passes(self) -> None:
        with _tmp_root() as root:
            _write_skill(
                root, "alpha", "Run it.",
                commands=["scripts/tool.py"],
                extra_files={"scripts/tool.py": "print('hi')\n"},
            )
            self.assertNotIn("bad-command", _rules(root))


class BaselineSuppressionTests(unittest.TestCase):
    def test_baselined_finding_passes_but_new_finding_fails(self) -> None:
        with _tmp_root() as root:
            _write_skill(root, "alpha", "See `$nonexistent-skill` for details.")
            baseline = {
                "baseline": [
                    {
                        "rule": "dangling-skill-ref",
                        "location": ".agents/skills/alpha/SKILL.md:7",
                        "detail": "$nonexistent-skill",
                        "reason": "test fixture",
                    }
                ]
            }
            _write(root / "scripts" / "instruction_graph_baseline.json", json.dumps(baseline))
            rc, output = _capture_main(root)
            self.assertEqual(rc, 0)
            self.assertIn("pass", output)

    def test_finding_not_in_baseline_fails(self) -> None:
        with _tmp_root() as root:
            _write_skill(root, "alpha", "See `$nonexistent-skill` for details.")
            _write(root / "scripts" / "instruction_graph_baseline.json", json.dumps({"baseline": []}))
            rc, output = _capture_main(root)
            self.assertEqual(rc, 1)
            self.assertIn("dangling-skill-ref", output)


if __name__ == "__main__":
    unittest.main()
