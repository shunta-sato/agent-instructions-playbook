from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from scripts.lint_command_docs import (
    collect_make_lint_commands,
    extract_readme_commands,
    find_drift,
    parse_makefile_targets,
)
from scripts.report_skill_inventory import (
    SkillInventory,
    build_report,
    main,
)
from scripts.skill_inventory_checks import (
    QUALITY_BAR_MINIMUMS,
    ratchet_findings,
    skill_warning_ids,
)


def _skill(
    name: str, visibility: str = "default", positive: int = 2, negative: int = 3,
    broad_flags: tuple[str, ...] = (),
) -> SkillInventory:
    """A minimal SkillInventory for warning-id tests, no file tree needed."""
    return SkillInventory(
        path=Path(f".agents/skills/{name}/SKILL.md"), directory=name, name=name,
        description="Use for testing.", description_length=16, line_count=10,
        reference_count=0, template_count=0, script_count=0, asset_count=0,
        example_count=0, eval_coverage_count=positive + negative,
        eval_should_trigger_count=positive, eval_should_not_trigger_count=negative,
        description_trigger_only_flags=[], broad_trigger_risk_flags=list(broad_flags),
        visibility=visibility,
    )


def _write_skill_tree(root: Path, name: str) -> None:
    skill_md = root / ".agents" / "skills" / name / "SKILL.md"
    skill_md.parent.mkdir(parents=True, exist_ok=True)
    skill_md.write_text(
        f"---\nname: {name}\ndescription: Use for testing.\nmetadata:\n"
        "  visibility: default\n---\nbody\n",
        encoding="utf-8",
    )
    (root / "evals" / "skill-triggers").mkdir(parents=True, exist_ok=True)


def _capture(fn, *args) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*args)
    return rc, buf.getvalue()


class QualityBarByVisibilityTests(unittest.TestCase):
    def test_default_visibility_requires_two_positive_three_negative(self) -> None:
        self.assertEqual(QUALITY_BAR_MINIMUMS["default"], (2, 3))
        short = skill_warning_ids(_skill("s", "default", positive=1, negative=2))
        self.assertTrue(any(s.startswith("quality-bar:positive-shortfall@") for s in short), short)
        self.assertTrue(any(s.startswith("quality-bar:negative-shortfall@") for s in short), short)
        met = skill_warning_ids(_skill("s", "default", positive=2, negative=3))
        self.assertNotIn("quality-bar:positive-shortfall", met)
        self.assertNotIn("quality-bar:negative-shortfall", met)

    def test_explicit_only_requires_one_positive_two_negative(self) -> None:
        self.assertEqual(QUALITY_BAR_MINIMUMS["explicit-only"], (1, 2))
        met = skill_warning_ids(_skill("s", "explicit-only", positive=1, negative=2))
        self.assertNotIn("quality-bar:positive-shortfall", met)
        self.assertNotIn("quality-bar:negative-shortfall", met)
        short = skill_warning_ids(_skill("s", "explicit-only", positive=0, negative=1))
        self.assertTrue(any(s.startswith("quality-bar:positive-shortfall@") for s in short), short)
        self.assertTrue(any(s.startswith("quality-bar:negative-shortfall@") for s in short), short)

    def test_template_is_exempt_regardless_of_counts(self) -> None:
        ids = skill_warning_ids(_skill("s", "template", positive=0, negative=0))
        self.assertFalse(any(s.startswith("quality-bar:positive-shortfall") for s in ids), ids)
        self.assertFalse(any(s.startswith("quality-bar:negative-shortfall") for s in ids), ids)

    def test_broad_trigger_id_drops_line_number(self) -> None:
        ids = skill_warning_ids(_skill("s", broad_flags=("whenever:line 7",)))
        self.assertIn("broad-trigger:whenever", ids)


class RatchetTests(unittest.TestCase):
    # .resolve() matches repo_root_from_args()'s contract (macOS /var ->
    # /private/var symlink otherwise breaks build_report's relative_to()).

    def test_new_warning_not_in_baseline_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            _write_skill_tree(root, "skill-a")
            report = build_report(root, ".agents/skills", "evals/skill-triggers", baseline={})
        self.assertTrue(report["ratchet"]["new_warnings"])

    def test_baselined_warning_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            _write_skill_tree(root, "skill-a")
            unbaselined = build_report(root, ".agents/skills", "evals/skill-triggers")
            ids = unbaselined["skill_warning_ids"]["skill-a"]
            report = build_report(
                root, ".agents/skills", "evals/skill-triggers", baseline={"skill-a": ids}
            )
        self.assertEqual(report["ratchet"]["new_warnings"], [])

    def test_stale_baseline_is_reported_not_failed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            _write_skill_tree(root, "skill-a")
            unbaselined = build_report(root, ".agents/skills", "evals/skill-triggers")
            ids = unbaselined["skill_warning_ids"]["skill-a"] + ["totally-fake-id"]
            report = build_report(
                root, ".agents/skills", "evals/skill-triggers", baseline={"skill-a": ids}
            )
        self.assertEqual(report["ratchet"]["new_warnings"], [])
        self.assertIn("skill-a: totally-fake-id", report["ratchet"]["stale_baseline"])

    def test_write_baseline_then_check_cli_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill_tree(root, "skill-a")
            baseline_path = root / "baseline.json"
            write_argv = [
                "--repo-root", str(root), "--write-baseline", "--baseline-path", str(baseline_path),
            ]
            rc, _ = _capture(main, write_argv)
            self.assertEqual(rc, 0)
            self.assertTrue(baseline_path.is_file())
            check_argv = ["--repo-root", str(root), "--check", "--baseline-path", str(baseline_path)]
            rc, out = _capture(main, check_argv)
        self.assertEqual(rc, 0)
        self.assertIn("new_warnings=0", out)


class CommandDocsDriftTests(unittest.TestCase):
    def test_missing_from_readme_is_detected(self) -> None:
        # Both scripts referenced here exist for real, so only the missing-
        # from-README direction is exercised (the README-listed script's
        # stale-file check stays clean).
        makefile_text = (
            "lint-static:\n"
            "\t$(PYTHON) scripts/report_skill_inventory.py --check\n"
            "\t$(PYTHON) scripts/check_context_budget.py\n"
        )
        readme_text = "## Validation\n\n- `python scripts/report_skill_inventory.py --check`\n"
        targets = parse_makefile_targets(makefile_text)
        make_commands = collect_make_lint_commands(targets)
        readme_commands = extract_readme_commands(readme_text)
        missing, stale, unwired = find_drift(make_commands, readme_commands)
        self.assertEqual(missing, ["scripts/check_context_budget.py"])
        self.assertEqual(stale, [])
        self.assertEqual(unwired, [])

    def test_stale_readme_entry_for_deleted_script_is_detected(self) -> None:
        missing, stale, unwired = find_drift(
            [],
            [
                "scripts/report_skill_inventory.py --check",
                "scripts/this_script_does_not_exist_ABC123.py",
            ],
        )
        self.assertEqual(missing, [])
        self.assertEqual(stale, ["scripts/this_script_does_not_exist_ABC123.py"])
        # The existing-but-unrun entry lands in the third direction instead.
        self.assertEqual(unwired, ["scripts/report_skill_inventory.py --check"])

    def test_readme_entry_with_existing_script_unrun_by_make_is_detected(self) -> None:
        missing, stale, unwired = find_drift(
            ["scripts/check_context_budget.py"],
            [
                "scripts/check_context_budget.py",
                "scripts/report_skill_inventory.py --check",
            ],
        )
        self.assertEqual(missing, [])
        self.assertEqual(stale, [])
        self.assertEqual(unwired, ["scripts/report_skill_inventory.py --check"])

    def test_tolerates_unsplit_bare_lint_target(self) -> None:
        targets = parse_makefile_targets("lint:\n\t$(PYTHON) scripts/only_check.py\n")
        self.assertEqual(collect_make_lint_commands(targets), ["scripts/only_check.py"])


if __name__ == "__main__":
    unittest.main()


class QualityBarRatchetOrderingTests(unittest.TestCase):
    """F1: a baselined shortfall covers equal-or-better counts only — a
    regression to fewer eval cases mints an uncovered id and fires."""

    def test_regression_below_baselined_count_fires(self) -> None:
        result = ratchet_findings(
            {"skill-a": ["quality-bar:negative-shortfall@0"]},
            {"skill-a": ["quality-bar:negative-shortfall@2"]},
        )
        self.assertEqual(
            result["new_warnings"], ["skill-a: quality-bar:negative-shortfall@0"]
        )

    def test_improvement_above_baselined_count_passes(self) -> None:
        result = ratchet_findings(
            {"skill-a": ["quality-bar:negative-shortfall@2"]},
            {"skill-a": ["quality-bar:negative-shortfall@1"]},
        )
        self.assertEqual(result["new_warnings"], [])

    def test_non_quality_bar_ids_stay_exact_membership(self) -> None:
        result = ratchet_findings(
            {"skill-a": ["broad-trigger:whenever"]},
            {"skill-a": ["broad-trigger:always"]},
        )
        self.assertEqual(
            result["new_warnings"], ["skill-a: broad-trigger:whenever"]
        )
