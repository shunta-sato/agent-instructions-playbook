from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.run_evolution_evals import SCENARIOS, ROOT, load_scenario, run_sequence

spec = importlib.util.spec_from_file_location(
    "preference_solution", ROOT / "tests/fixtures/preference_solution.py"
)
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)


class EvolutionOracleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, files):
        for name, content in files.items():
            (self.root / name).write_text(content)

    def check(self, stage):
        return subprocess.run(
            [sys.executable, "-S", str(SCENARIOS / "preferences_oracle.py"), str(self.root), stage],
            capture_output=True, timeout=45,
        ).returncode

    def test_original_seed_is_red(self):
        self.write(load_scenario("preferences")["files"])
        self.assertNotEqual(self.check("cli"), 0)

    def test_real_cli_batch_and_changed_rule(self):
        self.write(reference.solution())
        self.assertEqual(self.check("cli"), 0)
        self.assertEqual(self.check("batch"), 0)
        self.assertNotEqual(self.check("normalize"), 0)
        self.write(reference.solution(normalize=True))
        self.assertEqual(self.check("normalize"), 0)

    def test_success_message_without_persistence_is_rejected(self):
        self.write({"cli.py": "print('ok')\n", "batch.py": "print('{}')\n"})
        self.assertNotEqual(self.check("batch"), 0)

    def test_copy_left_behind_by_next_change_is_rejected(self):
        self.write(reference.solution(normalize=True))
        self.write({"old_store.py": reference.solution()["store.py"]})
        batch = self.root / "batch.py"
        batch.write_text(batch.read_text().replace("from store", "from old_store"))
        self.assertNotEqual(self.check("normalize"), 0)

    def test_losing_internal_whitespace_is_rejected(self):
        files = reference.solution(normalize=True)
        files["store.py"] = files["store.py"].replace("value.strip()", '"".join(value.split())')
        self.write(files)
        self.assertNotEqual(self.check("normalize"), 0)


class EvolutionRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scenario = load_scenario("preferences")

    def adapter(self, extra=""):
        script = self.root / "fixture_adapter.py"
        solutions = {"cli": reference.solution(), "batch": reference.solution(),
                     "normalize": reference.solution(normalize=True)}
        del solutions["cli"]["batch.py"]
        script.write_text(
            "import json,sys\nfrom pathlib import Path\n"
            "p=json.load(sys.stdin)\nw=Path(p['workspace'])\n"
            f"solutions={solutions!r}\n"
            "stage=p['stage_id']\n"
            "if stage!='cli': assert (w/'continuity.txt').read_text()=='preserved'\n"
            "(w/'continuity.txt').write_text('preserved')\n"
            "for name,content in solutions[stage].items(): (w/name).write_text(content)\n"
            "m={'resolved_model':p['requested_model'],'harness':p['requested_harness'],"
            "'harness_version':'fixture-only','team':p['requested_team'],"
            "'context_mode':'fresh','conversation_id':stage}\n"
            + extra + "\n"
            "Path(p['metadata_path']).write_text(json.dumps(m))\n"
            "Path(p['trace_path']).write_text(json.dumps({'fixture_only':True,'request':p})+'\\n')\n"
        )
        return [sys.executable, "-S", str(script)]

    def trial(self, extra="", arm="minimal"):
        return run_sequence(self.scenario, arm, self.root / "trial", self.adapter(extra),
                            "fixture-model", "fixture", [], None, 60)

    def test_continuation_preserves_code_and_does_not_leak_future(self):
        result = self.trial()
        self.assertEqual(result["status"], "needs-behavior-review")
        self.assertEqual(len(result["stages"]), 3)
        for previous, following in zip(result["stages"], result["stages"][1:]):
            self.assertEqual(previous["after"], following["before"])
        first = json.loads((self.root / "trial/cli/trace.jsonl").read_text())["request"]
        self.assertNotIn("batch.py", first["task"])
        self.assertNotIn("strip surrounding", first["task"])
        self.assertTrue(first["fresh_conversation"])
        last = json.loads((self.root / "trial/normalize/trace.jsonl").read_text())["request"]
        self.assertIn("Previously accepted", last["task"])

    def test_selective_arm_exposes_code_health(self):
        self.assertEqual(self.trial(arm="selective")["status"], "needs-behavior-review")
        self.assertTrue((self.root / "trial/workspace/.agents/skills/code-health/SKILL.md").is_file())

    def test_reused_conversation_stops_before_third_stage(self):
        result = self.trial("m['conversation_id']='same'")
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(len(result["stages"]), 2)
        self.assertFalse((self.root / "trial/normalize").exists())

    def test_wrong_team_does_not_count_as_measured_configuration(self):
        result = self.trial("m['team']=[{'role':'worker','model':'unrequested'}]")
        self.assertEqual(len(result["stages"]), 1)
        self.assertEqual(result["stages"][0]["functional"], "not-evaluated")

    def test_agent_failure_stops_sequence(self):
        result = self.trial("raise SystemExit(3)")
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(len(result["stages"]), 1)

    def test_contract_tampering_is_not_success(self):
        result = self.trial("(w/'AGENTS.md').write_text('checks optional')")
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("governing contract", result["stages"][0]["limit"])

    def test_functional_failure_stops_sequence(self):
        result = self.trial("(w/'cli.py').write_text('raise SystemExit(0)\\n')")
        self.assertEqual(len(result["stages"]), 1)
        self.assertEqual(result["stages"][0]["status"], "functional-failure")

    def test_existing_output_is_never_overwritten(self):
        (self.root / "trial").mkdir()
        with self.assertRaises(ValueError):
            self.trial()

    def test_path_traversal_is_rejected(self):
        with self.assertRaises(ValueError):
            load_scenario("../preferences")

    def test_cli_requires_real_sandbox_acknowledgment(self):
        command = [sys.executable, "-m", "scripts.run_evolution_evals", "--scenario", "preferences",
                   "--adapter-json", '["missing"]', "--model", "fixture", "--harness", "fixture",
                   "--output", str(self.root / "no-run")]
        output = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(output.returncode, 2)
        self.assertIn("not a sandbox", output.stderr)
        self.assertFalse((self.root / "no-run").exists())


if __name__ == "__main__":
    unittest.main()
