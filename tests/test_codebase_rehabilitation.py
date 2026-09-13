from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.run_evolution_evals import ROOT, SCENARIOS, load_scenario, run_sequence


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


inspector = load_module(
    "code_health_inspector",
    ROOT / ".agents/skills/codebase-rehabilitation/scripts/inspect_code_health.py",
)
reference = load_module("rehab_reference", ROOT / "tests/fixtures/preference_solution.py")


class InspectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        (self.root / "a.py").write_text("def first(value):\n    return value + 1\n")
        (self.root / "b.py").write_text("def second(value):\n    return value + 1\n")
        self.git("add", ".")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "seed")

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True)

    def scan(self):
        return inspector.inspect(self.root, ["."], "product")

    def test_exact_clone_is_diagnostic_not_a_score(self):
        result = self.scan()
        self.assertEqual(result["status"], "diagnostic-only")
        self.assertEqual(len(result["exact_clone_candidates"]), 1)
        self.assertNotIn("score", result)

    def test_different_literals_are_not_identical_rules(self):
        (self.root / "b.py").write_text("def second(value):\n    return value + 2\n")
        self.assertEqual(self.scan()["exact_clone_candidates"], [])

    def test_file_hash_binds_dirty_worktree(self):
        path = self.root / "a.py"
        path.write_text("def first(value):\n    return value - 1\n")
        result = self.scan()
        item = next(item for item in result["files"] if item["path"] == "a.py")
        self.assertEqual(item["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(result["head"], self.git("rev-parse", "HEAD").strip())

    def test_syntax_error_cannot_look_clean(self):
        (self.root / "a.py").write_text("def broken(:\n")
        self.assertEqual(self.scan()["status"], "incomplete")

    def test_deleted_tracked_file_is_incomplete(self):
        (self.root / "a.py").unlink()
        self.assertEqual(self.scan()["status"], "incomplete")

    def test_symlink_is_refused_without_reading_target(self):
        path = self.root / "a.py"
        path.unlink()
        path.symlink_to(self.root / "b.py")
        self.assertEqual(self.scan()["status"], "incomplete")

    def test_scope_escape_and_empty_paths_are_rejected(self):
        for paths in [["../outside"], [], [str(self.root / "a.py")]]:
            with self.assertRaises(ValueError):
                inspector.inspect(self.root, paths, "product")

    def test_untracked_only_selection_is_not_a_clean_result(self):
        (self.root / "new.py").write_text("print('new')\n")
        result = inspector.inspect(self.root, ["new.py"], "product")
        self.assertEqual(result["status"], "incomplete")

    def test_read_only_scan_never_imports_project(self):
        path = self.root / "a.py"
        path.write_text("from pathlib import Path\nPath('executed').touch()\nraise RuntimeError()\n")
        before = {p.name: p.read_bytes() for p in self.root.glob("*.py")}
        self.assertEqual(self.scan()["status"], "diagnostic-only")
        self.assertFalse((self.root / "executed").exists())
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.glob("*.py")})

    def test_cli_reports_missing_scope_nonzero(self):
        output = subprocess.run(
            [sys.executable, "-S", inspector.__file__, "--root", str(self.root),
             "--path", "missing", "--kind", "test"], text=True, capture_output=True,
        )
        self.assertNotEqual(output.returncode, 0)
        self.assertEqual(json.loads(output.stdout)["status"], "incomplete")


class RehabilitationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scenario = load_scenario("rehabilitation")
        self.write(self.scenario["files"])

    def write(self, files):
        for name, content in files.items():
            (self.root / name).write_text(content)

    def check(self, stage, oracle="rehabilitation_oracle.py"):
        return subprocess.run(
            [sys.executable, "-S", str(SCENARIOS / oracle), str(self.root), stage],
            capture_output=True, timeout=30,
        ).returncode

    def repair(self, normalize=False):
        self.write(reference.solution(normalize=normalize))
        for name in ["cli_store.py", "batch_store.py", "unused_compat.py"]:
            (self.root / name).unlink(missing_ok=True)
        (self.root / "public_v1.py").write_text(
            "# Published external consumer boundary, retained intentionally.\n"
            "from store import load as read_value\n"
        )

    def test_old_functionality_is_valid_but_retirement_is_pending(self):
        self.assertEqual(self.check("batch", "preferences_oracle.py"), 0)
        self.assertNotEqual(self.check("rehabilitate"), 0)

    def test_repair_then_fresh_followup_preserves_real_compatibility(self):
        self.repair()
        self.assertEqual(self.check("rehabilitate"), 0)
        self.assertNotEqual(self.check("rehab-normalize"), 0)
        self.repair(normalize=True)
        self.assertEqual(self.check("rehab-normalize"), 0)

    def test_indiscriminate_compatibility_removal_fails(self):
        self.repair()
        (self.root / "public_v1.py").unlink()
        self.assertNotEqual(self.check("rehabilitate"), 0)

    def test_retained_obsolete_alias_fails(self):
        self.repair()
        (self.root / "unused_compat.py").write_text("from store import load as read_old_value\n")
        self.assertNotEqual(self.check("rehabilitate"), 0)

    def test_optimized_interpreter_cannot_silence_acceptance_checks(self):
        self.repair()
        output = subprocess.run(
            [sys.executable, "-S", "-O", str(SCENARIOS / "rehabilitation_oracle.py"),
             str(self.root), "rehabilitate"], capture_output=True, text=True,
        )
        self.assertNotEqual(output.returncode, 0)
        self.assertIn("requires enabled assertions", output.stderr)

    def test_rehabilitation_sequence_uses_actual_previous_candidate(self):
        script = self.root / "fixture_adapter.py"
        solutions = {"rehabilitate": reference.solution(),
                     "rehab-normalize": reference.solution(normalize=True)}
        script.write_text(
            "import json,sys\nfrom pathlib import Path\n"
            "p=json.load(sys.stdin)\nw=Path(p['workspace'])\ns=p['stage_id']\n"
            f"solutions={solutions!r}\n"
            "if s=='rehab-normalize': assert (w/'repair-marker').exists()\n"
            "for name,content in solutions[s].items(): (w/name).write_text(content)\n"
            "for name in ['cli_store.py','batch_store.py','unused_compat.py']: (w/name).unlink(missing_ok=True)\n"
            "(w/'public_v1.py').write_text('# Public external API.\\nfrom store import load as read_value\\n')\n"
            "(w/'repair-marker').write_text('actual retained candidate')\n"
            "m={'resolved_model':p['requested_model'],'harness':p['requested_harness'],"
            "'harness_version':'fixture-only','team':p['requested_team'],"
            "'context_mode':'fresh','conversation_id':s}\n"
            "Path(p['metadata_path']).write_text(json.dumps(m))\n"
            "Path(p['trace_path']).write_text(json.dumps({'fixture_only':True,'stage':s})+'\\n')\n"
        )
        result = run_sequence(self.scenario, "selective", self.root / "trial",
                              [sys.executable, "-S", str(script)], "fixture-model", "fixture", [], None, 30)
        self.assertEqual(result["status"], "needs-behavior-review")
        self.assertEqual(result["stages"][0]["after"], result["stages"][1]["before"])


if __name__ == "__main__":
    unittest.main()
