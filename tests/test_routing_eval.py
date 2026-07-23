from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_routing_eval import main

MARKER_SKILL = "zzz-nonexistent-marker-skill-QQQ"


def _capture(fn, *args) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*args)
    return rc, buf.getvalue()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _skill(root: Path, name: str, description: str, requires=None, visibility=None) -> None:
    meta = [f"  short-description: {name}"]
    if visibility:
        meta.append(f"  visibility: {visibility}")
    if requires:
        meta.append("  requires:")
        meta += [f"    - {r}" for r in requires]
    fm = ["---", f"name: {name}", f'description: "{description}"', "metadata:"] + meta + ["---"]
    _write(root / ".agents" / "skills" / name / "SKILL.md", "\n".join(fm) + f"\n\n## {name}\n")


def _skill_with_ref(root: Path, name: str, description: str) -> None:
    _skill(root, name, description, requires=[f"references/{name}.md"])
    _write(root / ".agents" / "skills" / name / "references" / f"{name}.md", f"{name} reference body.\n")


def _build_fixture_repo(root: Path) -> Path:
    """Fixture-tree style of test_context_budget.py: a minimal but complete checkout."""
    _write(root / "AGENTS.md", "# AGENTS.md\n\nFixture bootstrap text.\n")
    _skill_with_ref(root, "dev-workflow", "Use for delivery-mode changes.")
    _skill_with_ref(root, "quality-gate", "Use before every submission.")
    _skill(root, "alpha-skill", "Use for alpha work.")
    _skill(root, "hidden-skill", "Use for hidden work.", visibility="explicit-only")
    cases = {
        "version": 1,
        "cases": [
            {
                "id": "case-1",
                "prompt": "Do some alpha work here.",
                "should_trigger": ["alpha-skill"],
                "should_not_trigger": ["hidden-skill"],
            },
            {
                "id": "case-2",
                "prompt": "Do some hidden work here.",
                "should_trigger": ["hidden-skill"],
                "should_not_trigger": ["alpha-skill", MARKER_SKILL],
            },
        ],
    }
    _write(root / "evals" / "skill-triggers" / "fixture.json", json.dumps(cases))
    return root


class BuildDeterminismTests(unittest.TestCase):
    def test_build_is_deterministic_and_covers_every_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _build_fixture_repo(Path(tmp) / "repo")
            out1, out2 = Path(tmp) / "out1", Path(tmp) / "out2"
            for out in (out1, out2):
                rc, _ = _capture(main, ["build", "--repo-root", str(root), "--out", str(out), "--batch-size", "1"])
                self.assertEqual(rc, 0)
            names = sorted(p.name for p in out1.iterdir())
            self.assertEqual(names, ["batch-01.md", "batch-02.md", "manifest.json"])
            self.assertEqual(names, sorted(p.name for p in out2.iterdir()))
            for name in names:
                self.assertEqual((out1 / name).read_text(), (out2 / name).read_text())
            manifest = json.loads((out1 / "manifest.json").read_text())
            self.assertEqual(sorted(c["id"] for c in manifest["cases"]), ["case-1", "case-2"])
            self.assertGreater(manifest["discovery_surface"]["lines"], 0)
            self.assertGreater(manifest["discovery_surface"]["chars"], 0)


class NoExpectationLeakTests(unittest.TestCase):
    def test_packs_never_contain_expectation_fields_or_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _build_fixture_repo(Path(tmp) / "repo")
            out = Path(tmp) / "packs"
            rc, _ = _capture(main, ["build", "--repo-root", str(root), "--out", str(out)])
            self.assertEqual(rc, 0)
            pack_text = "\n".join(p.read_text(encoding="utf-8") for p in sorted(out.glob("*.md")))
            self.assertNotIn("should_trigger", pack_text)
            self.assertNotIn("should_not_trigger", pack_text)
            self.assertNotIn(MARKER_SKILL, pack_text)
            manifest_text = (out / "manifest.json").read_text(encoding="utf-8")
            self.assertNotIn("should_trigger", manifest_text)
            self.assertNotIn(MARKER_SKILL, manifest_text)


CASE_BATCHES = [{"id": "case-1", "batch": "batch-01"}, {"id": "case-2", "batch": "batch-02"}]


def _grade(root: Path, tmp: Path, batch_files: dict[str, str]) -> tuple[int, dict]:
    """Write a manifest.json (referencing fixture-repo case-1/case-2) plus the given
    raw response batch files, then run `grade` and return (exit_code, graded dict)."""
    packs, responses, out = tmp / "packs", tmp / "responses", tmp / "graded.json"
    manifest = {"variant": "fixture", "commit": "deadbeef", "cases": CASE_BATCHES,
                "discovery_surface": {"lines": 10, "chars": 100}}
    _write(packs / "manifest.json", json.dumps(manifest))
    for name, content in batch_files.items():
        _write(responses / name, content)
    rc, _ = _capture(
        main,
        ["grade", "--packs", str(packs), "--responses", str(responses), "--out", str(out), "--repo-root", str(root)],
    )
    return rc, json.loads(out.read_text())


class GradingTests(unittest.TestCase):
    def test_recall_miss_unknown_skill_and_missing_batch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = _build_fixture_repo(tmp / "repo")
            # case-1 misses the expected alpha-skill and offers an unknown skill;
            # batch-02 is never produced, so case-2 must be reported ungraded.
            batch = json.dumps([{"id": "case-1", "skills": ["not-a-real-skill"]}])
            rc, graded = _grade(root, tmp, {"batch-01.json": batch})
            self.assertEqual(rc, 0)
            self.assertEqual(graded["cases_graded"], 1)
            want = {"id": "case-2", "batch": "batch-02", "reason": "batch_missing"}
            self.assertEqual(graded["ungraded"][0], want)
            case1 = graded["cases"][0]
            self.assertEqual(case1["misses"], ["alpha-skill"])
            self.assertEqual(case1["unknown"], ["not-a-real-skill"])
            self.assertLess(graded["recall"], 1.0)

    def test_precision_violation_and_corrupt_batch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = _build_fixture_repo(tmp / "repo")
            # case-1 selects the should_not_trigger skill: a precision violation.
            batch1 = json.dumps([{"id": "case-1", "skills": ["alpha-skill", "hidden-skill"]}])
            rc, graded = _grade(root, tmp, {"batch-01.json": batch1, "batch-02.json": "{not valid json"})
            self.assertEqual(rc, 0)
            self.assertEqual(graded["ungraded"][0]["reason"], "batch_corrupt")
            self.assertEqual(graded["cases"][0]["violations"], ["hidden-skill"])
            self.assertLess(graded["compliance"], 1.0)
            self.assertEqual(graded["confusion"], {"hidden-skill": 1})


class ReportShapeTests(unittest.TestCase):
    def test_report_has_summary_table_and_ranked_worst_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            graded = {
                "variant": "v1",
                "commit": "abc123",
                "cases_total": 2,
                "cases_graded": 2,
                "recall": 0.5,
                "compliance": 1.0,
                "co_fire_mean": 0.5,
                "co_fire_p90": 1.0,
                "surface": {"lines": 10, "chars": 100},
                "confusion": {},
                "unknown_skills": {},
                "ungraded": [],
                "cases": [
                    {"id": "case-a", "selected": [], "misses": ["alpha-skill"], "violations": [], "unknown": [], "co_fire_count": 0},
                    {"id": "case-b", "selected": ["alpha-skill"], "misses": [], "violations": [], "unknown": [], "co_fire_count": 1},
                ],
            }
            path = Path(tmp) / "graded.json"
            path.write_text(json.dumps(graded), encoding="utf-8")
            rc, out = _capture(main, ["report", "--graded", str(path), "--format", "md"])
            rc2, out2 = _capture(main, ["report", "--graded", str(path), "--format", "md"])
            self.assertEqual(rc, 0)
            self.assertEqual(out, out2)  # deterministic
            self.assertIn("# Routing Eval Report", out)
            self.assertIn("| Metric | v1 |", out)
            self.assertIn("Should-trigger recall | 50.0%", out)
            self.assertIn("## Worst cases (v1)", out)
            self.assertLess(out.index("case-a"), out.index("case-b"))


if __name__ == "__main__":
    unittest.main()
