from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_behavior_eval import grade_decision, main

MARKER = "ZZZ-BEHAVIOR-MARKER-QQQ"
GATE_BODY = (
    "## How to use\n\n0) Open `references/fixture-gate.md`.\n\n"
    "## Output expectation\n\n- Start with: `Verdict: pass` or `Verdict: fail`.\n"
)
PLAIN_BODY = (
    "## How to use\n\n0) Open `references/fixture-plain.md`. Open\n"
    "   `references/fixture-plain-extra.md` only when the scenario needs extra depth.\n\n"
    "## Output expectation\n\n- State the classification with a one-line justification.\n"
)


def _capture(fn, *args) -> tuple[int, str]:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*args)
    return rc, buf.getvalue()


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_skill(root: Path, name: str, requires: list[str], resources: list[str], body: str) -> None:
    meta = [f"  short-description: {name}"]
    if requires:
        meta += ["  requires:"] + [f"    - {r}" for r in requires]
    if resources:
        meta += ["  resources:"] + [f"    - {r}" for r in resources]
    fm = ["---", f"name: {name}", f'description: "{name} fixture."', "metadata:"] + meta + ["---"]
    _write(root / ".agents" / "skills" / name / "SKILL.md", "\n".join(fm) + "\n\n" + body)
    for rel in requires + resources:
        _write(root / ".agents" / "skills" / name / rel, f"{rel} reference body.\n")


def _build_fixture_repo(root: Path) -> Path:
    # A gate-style skill (documented `Start with:` marker) + a plain skill (no marker, 1 requires + 1 resource).
    _write_skill(root, "fixture-gate-skill", ["references/fixture-gate.md"], [], GATE_BODY)
    _write_skill(
        root, "fixture-plain-skill", ["references/fixture-plain.md"],
        ["references/fixture-plain-extra.md"], PLAIN_BODY,
    )
    gate = {
        "version": 1, "skill": "fixture-gate-skill",
        "cases": [{
            "id": "gate-case-pass", "prompt": "Evaluate scenario A.",
            "given": ["fact one", "fact two"], "expected_decision": "pass",
            "expected_findings": ["reason alpha"],
            "expected_output_contains": ["alpha", MARKER],
        }],
    }
    plain = {
        "version": 1, "skill": "fixture-plain-skill",
        "cases": [{
            "id": "plain-case-classify", "prompt": "Classify scenario B.",
            "given": ["fact three"], "expected_decision": "H",
            "expected_findings": [], "expected_output_contains": ["beta"],
        }],
    }
    _write(root / "evals" / "skill-behavior" / "gate.json", json.dumps(gate))
    _write(root / "evals" / "skill-behavior" / "plain.json", json.dumps(plain))
    return root


class BuildDeterminismTests(unittest.TestCase):
    def test_build_is_deterministic_one_pack_per_case(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _build_fixture_repo(Path(tmp) / "repo")
            out1, out2 = Path(tmp) / "out1", Path(tmp) / "out2"
            for out in (out1, out2):
                rc, _ = _capture(main, ["build", "--repo-root", str(root), "--out", str(out)])
                self.assertEqual(rc, 0)
            names = sorted(p.name for p in out1.iterdir())
            self.assertEqual(names, ["gate-case-pass.md", "manifest.json", "plain-case-classify.md"])
            self.assertEqual(names, sorted(p.name for p in out2.iterdir()))
            for name in names:
                self.assertEqual((out1 / name).read_text(), (out2 / name).read_text())
            manifest = json.loads((out1 / "manifest.json").read_text())
            self.assertEqual(sorted(c["id"] for c in manifest["cases"]), ["gate-case-pass", "plain-case-classify"])
            self.assertTrue(all(c["lines"] > 0 for c in manifest["cases"]))
            # regression: the resource condition must be the full wrapped
            # sentence, not the physical line it happens to sit on.
            plain_pack = (out1 / "plain-case-classify.md").read_text(encoding="utf-8")
            self.assertIn("needs extra depth", plain_pack)


class NoExpectationLeakTests(unittest.TestCase):
    def test_packs_never_contain_expectation_fields_or_marker_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _build_fixture_repo(Path(tmp) / "repo")
            out = Path(tmp) / "packs"
            rc, _ = _capture(main, ["build", "--repo-root", str(root), "--out", str(out)])
            self.assertEqual(rc, 0)
            pack_text = "\n".join(p.read_text(encoding="utf-8") for p in sorted(out.glob("*.md")))
            for field in ("expected_decision", "expected_findings", "expected_output_contains"):
                self.assertNotIn(field, pack_text)
            self.assertNotIn(MARKER, pack_text)
            self.assertNotIn(MARKER, (out / "manifest.json").read_text(encoding="utf-8"))


class DecisionGradingTests(unittest.TestCase):
    def test_marker_match_mismatch_and_missing_marker_line(self) -> None:
        self.assertTrue(grade_decision("Gate decision: submit\n\n0 findings\n", "submit", "Gate decision:"))
        self.assertTrue(grade_decision("Gate decision: no-submit\n\nfindings\n", "no-submit", "Gate decision:"))
        # "no-submit" contains "submit" as a substring; exact-remainder
        # matching must not let that hide a decision that was actually wrong.
        self.assertFalse(grade_decision("Gate decision: no-submit\n\nfindings\n", "submit", "Gate decision:"))
        self.assertFalse(grade_decision("Some other text entirely.\n", "submit", "Gate decision:"))

    def test_fallback_to_first_line_when_skill_documents_no_marker(self) -> None:
        self.assertTrue(grade_decision("Tier: H - money/billing tie-break applies.\n", "H", None))
        self.assertFalse(grade_decision("Tier: S - ordinary business logic.\n", "H", None))


MANIFEST_CASES = [
    {"id": "gate-case-pass", "skill": "fixture-gate-skill"},
    {"id": "plain-case-classify", "skill": "fixture-plain-skill"},
]


def _grade(root: Path, tmp: Path, responses: dict[str, str]) -> tuple[int, dict]:
    packs, out = tmp / "packs", tmp / "graded.json"
    _write(packs / "manifest.json", json.dumps({"variant": "fixture", "commit": "deadbeef", "cases": MANIFEST_CASES}))
    responses_dir = tmp / "responses"
    for cid, text in responses.items():
        _write(responses_dir / f"{cid}.txt", text)
    rc, _ = _capture(
        main,
        ["grade", "--packs", str(packs), "--responses", str(responses_dir), "--out", str(out), "--repo-root", str(root)],
    )
    return rc, json.loads(out.read_text())


class GradingTests(unittest.TestCase):
    def test_output_contains_findings_and_missing_response(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = _build_fixture_repo(tmp / "repo")
            rc, graded = _grade(root, tmp, {"gate-case-pass": "Verdict: pass\n\nreason alpha applies here.\n"})
            self.assertEqual(rc, 0)
            self.assertEqual(graded["cases_graded"], 1)
            self.assertEqual(graded["ungraded"], [{"id": "plain-case-classify", "reason": "response_missing"}])
            case = graded["cases"][0]
            self.assertTrue(case["decision_match"])
            self.assertEqual(case["output_contains"], {"total": 2, "matched": 1, "missing": [MARKER]})
            self.assertEqual(case["findings"], {"total": 1, "matched": 1})
            self.assertLess(graded["output_contains_rate"], 1.0)

    def test_empty_response_file_is_ungraded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            root = _build_fixture_repo(tmp / "repo")
            rc, graded = _grade(root, tmp, {"gate-case-pass": "   \n\n"})
            self.assertEqual(rc, 0)
            self.assertEqual(graded["ungraded"][0], {"id": "gate-case-pass", "reason": "response_empty"})


class ReportShapeTests(unittest.TestCase):
    def test_report_has_summary_table_and_ranked_worst_cases(self) -> None:
        graded = {
            "variant": "v1", "commit": "abc123", "cases_total": 2, "cases_graded": 2,
            "decision_accuracy": 0.5, "output_contains_rate": 1.0, "findings_ratio_mean": 0.5,
            "ungraded": [],
            "cases": [
                {"id": "case-a", "decision_match": False,
                 "output_contains": {"total": 2, "matched": 1, "missing": ["x"]},
                 "findings": {"total": 1, "matched": 0}},
                {"id": "case-b", "decision_match": True,
                 "output_contains": {"total": 1, "matched": 1, "missing": []},
                 "findings": {"total": 0, "matched": 0}},
            ],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "graded.json"
            path.write_text(json.dumps(graded), encoding="utf-8")
            rc, out = _capture(main, ["report", "--graded", str(path), "--format", "md"])
            rc2, out2 = _capture(main, ["report", "--graded", str(path), "--format", "md"])
            self.assertEqual(rc, 0)
            self.assertEqual(out, out2)  # deterministic
            self.assertIn("# Behavior Eval Report", out)
            self.assertIn("| Metric | v1 |", out)
            self.assertIn("Decision accuracy | 50.0%", out)
            self.assertIn("## Worst cases (v1)", out)
            self.assertLess(out.index("case-a"), out.index("case-b"))


if __name__ == "__main__":
    unittest.main()
