from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "evals/function-design/scripts/grade_run.py"
SPEC = importlib.util.spec_from_file_location("grade_function_run", SCRIPT)
grader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(grader)


def metadata() -> dict:
    return {
        "run_id": "synthetic-self-test", "kind": "calibration", "variant": "core",
        "model": "not-a-model-run", "harness": "unittest", "effort": "not-applicable",
        "environment": "temporary fixture", "playbook_commit": "0" * 40,
        "instructions_sha256": "0" * 64, "trial": 1,
    }


def put(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class WorkspaceGradingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "trusted"
        self.corpus = self.root / "evals/function-design"
        self.fixture = self.corpus / "fixtures/predicate"
        self.workspace = Path(self.temp.name) / "candidate"
        put(self.corpus / "scenarios.json", json.dumps({"scenarios": [
            {"id": "predicate", "fixture": "fixtures/predicate"}
        ]}))
        put(self.corpus / "scripts/helper.py", "# Trusted fixture helper.\n")
        put(self.fixture / "task.md", "Return True at the inclusive boundary.\n")
        put(self.fixture / "src/predicate.py", "def ready(now, due):\n    return now > due\n")
        put(self.workspace / "src/predicate.py", "def ready(now, due):\n    return now >= due\n")
        put(self.fixture / "expected/good/tests/test_predicate.py", '''import unittest
from src.predicate import ready

class PredicateTests(unittest.TestCase):
    def test_inclusive_boundary(self):
        self.assertTrue(ready(2, 2))
        self.assertFalse(ready(1, 2))
''')
        put(self.fixture / "oracle.py", '''import subprocess
import sys
result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"],
                        cwd=sys.argv[1], capture_output=True, text=True)
print(result.stdout + result.stderr)
raise SystemExit(result.returncode)
''')

    def grade(self, **kwargs) -> dict:
        return grader.grade_run(self.root, "predicate", self.workspace, metadata(), **kwargs)

    def test_grades_code_and_preserves_the_candidate(self) -> None:
        before = grader.snapshot(self.workspace)
        report = self.grade()
        self.assertEqual(report["oracle_result"], "pass")
        self.assertEqual(report["source_delta"]["changed_files"], ["predicate.py"])
        self.assertEqual(report["source_delta"]["lines_added"], 1)
        self.assertEqual(grader.snapshot(self.workspace), before)
        self.assertNotIn("agent_wall_seconds", report)

    def test_candidate_tests_cannot_replace_acceptance_tests(self) -> None:
        put(self.workspace / "src/predicate.py", "def ready(now, due):\n    return False\n")
        put(self.workspace / "tests/test_fake.py", "# Candidate claims everything passed.\n")
        self.assertEqual(self.grade()["oracle_result"], "fail")

    def test_zero_tests_is_not_a_pass(self) -> None:
        put(self.fixture / "expected/good/tests/test_predicate.py", "import unittest\n")
        self.assertEqual(self.grade()["oracle_result"], "fail")

    def test_missing_acceptance_tests_is_an_error(self) -> None:
        shutil.rmtree(self.fixture / "expected/good/tests")
        with self.assertRaises(ValueError):
            self.grade()

    def test_unknown_scenario_is_an_error(self) -> None:
        with self.assertRaises(ValueError):
            grader.grade_run(self.root, "missing", self.workspace, metadata())

    def test_symlinked_source_is_rejected(self) -> None:
        (self.workspace / "src/link.py").symlink_to(self.fixture / "oracle.py")
        with self.assertRaises(ValueError):
            self.grade()

    def test_timeout_is_a_failed_result(self) -> None:
        put(self.fixture / "oracle.py", "import time\ntime.sleep(10)\n")
        self.assertEqual(self.grade(timeout=0.05)["oracle_result"], "fail")

    def test_evidence_identity_changes_with_code_or_tests(self) -> None:
        first = self.grade()
        with (self.workspace / "src/predicate.py").open("a") as handle:
            handle.write("\n")
        second = self.grade()
        self.assertNotEqual(first["source_sha256"], second["source_sha256"])
        self.assertNotEqual(first["judged_inputs_sha256"], second["judged_inputs_sha256"])
        self.assertEqual(first["trusted_tests_sha256"], second["trusted_tests_sha256"])

    def test_metadata_rejects_missing_identity_and_invalid_trials(self) -> None:
        for key, value in (("model", ""), ("trial", True), ("variant", "unknown"),
                           ("playbook_commit", "main"), ("instructions_sha256", "unknown")):
            with self.subTest(key=key):
                altered = copy.deepcopy(metadata())
                altered[key] = value
                with self.assertRaises(ValueError):
                    grader.validate_metadata(altered)

    def test_cli_writes_failure_report_and_refuses_overwrite(self) -> None:
        put(self.workspace / "src/predicate.py", "def ready(now, due):\n    return False\n")
        meta = Path(self.temp.name) / "metadata.json"
        out = Path(self.temp.name) / "result.json"
        put(meta, json.dumps(metadata()))
        args = ["--repo-root", str(self.root), "--scenario", "predicate",
                "--workspace", str(self.workspace), "--run-metadata", str(meta),
                "--out", str(out)]
        self.assertEqual(grader.main(args), 1)
        before = out.read_bytes()
        self.assertEqual(grader.main(args), 2)
        self.assertEqual(out.read_bytes(), before)


class ExistingFixtureCalibrationTests(unittest.TestCase):
    def test_existing_good_and_bad_oracles(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "evals/function-design/scripts/run_oracles.py")],
            cwd=ROOT, capture_output=True, text=True, timeout=90,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_real_workspace_path_accepts_all_existing_good_samples(self) -> None:
        corpus = ROOT / "evals/function-design"
        scenarios = json.loads((corpus / "scenarios.json").read_text())["scenarios"]
        for case in scenarios:
            with self.subTest(scenario=case["id"]):
                good = corpus / case["fixture"] / "expected/good"
                report = grader.grade_run(ROOT, case["id"], good, metadata())
                self.assertEqual(report["oracle_result"], "pass", report["oracle_output"])

    def test_noop_rejects_comment_narration_and_unused_abstraction(self) -> None:
        good = ROOT / "evals/function-design/fixtures/no-op-small-duplication/expected/good"
        additions = (
            "\n# Now handles everything safely and robustly.\n",
            "\ndef future_extension(value):\n    return value\n",
        )
        for addition in additions:
            with self.subTest(addition=addition), tempfile.TemporaryDirectory() as directory:
                candidate = Path(directory) / "candidate"
                shutil.copytree(good, candidate)
                source = next((candidate / "src").rglob("*.py"))
                with source.open("a") as handle:
                    handle.write(addition)
                report = grader.grade_run(ROOT, "no-op-small-duplication", candidate, metadata())
                self.assertEqual(report["oracle_result"], "fail")


if __name__ == "__main__":
    unittest.main()
