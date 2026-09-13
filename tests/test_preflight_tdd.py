"""Offline discovery/installer and real CLI oracle regressions, not agent evals."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.install_skills import install, selection

ROOT = Path(__file__).resolve().parents[1]
NEW_SKILLS = ('preflight-engineering', 'agentic-tdd')


class PreflightDiscoveryTests(unittest.TestCase):
    def test_core_exposes_both_skills(self):
        core = json.loads((ROOT / 'profiles.json').read_text())['profiles']['core']
        for name in NEW_SKILLS:
            self.assertIn(name, core)
        self.assertEqual(len(core), len(set(core)))

    def test_both_skills_can_be_selected_without_other_profiles(self):
        self.assertEqual(selection(ROOT, [], list(NEW_SKILLS)), sorted(NEW_SKILLS))

    def test_real_native_mirrors(self):
        for name in NEW_SKILLS:
            mirror = ROOT / '.claude/skills' / name
            self.assertTrue(mirror.is_symlink(), name)
            self.assertEqual(mirror.resolve(), ROOT / '.agents/skills' / name)

    def test_installation_does_not_overwrite_project_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            subprocess.run(['git', 'init', '-q', str(target)], check=True, capture_output=True)
            (target / 'AGENTS.md').write_text('Existing project authority must remain.\n')
            result = install(target, ROOT, list(NEW_SKILLS), 'both')
            self.assertEqual(len(result['links']), 4)
            self.assertEqual((target / 'AGENTS.md').read_text(), 'Existing project authority must remain.\n')
            for prefix in ('.agents/skills', '.claude/skills'):
                for name in NEW_SKILLS:
                    self.assertTrue((target / prefix / name / 'SKILL.md').is_file())

    def test_dispositions_retain_value_without_old_tdd_alias(self):
        items = json.loads((ROOT / 'docs/skill-disposition.json').read_text())['skills']
        mapping = {item['old']: item for item in items}
        self.assertEqual(mapping['preflight-engineering']['disposition'], 'rewritten')
        self.assertEqual(mapping['preflight-engineering']['destination'], 'preflight-engineering')
        self.assertEqual(mapping['test-driven-development']['destination'], 'agentic-tdd')
        self.assertFalse((ROOT / '.agents/skills/test-driven-development').exists())

    def test_consumer_template_matches_bundled_onboarding_asset(self):
        self.assertEqual((ROOT / 'templates/AGENTS.md').read_bytes(),
                         (ROOT / '.agents/skills/repo-onboarding/templates/AGENTS.md').read_bytes())


class PreflightOracleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name)
        cases = json.loads((ROOT / 'evals/cases.json').read_text())['cases']
        self.case = next(c for c in cases if c['id'] == 'preflight-e2e-persistence')
        for name, content in self.case['files'].items():
            (self.workspace / name).write_text(content)
        self.solution = (ROOT / 'tests/fixtures/preflight_e2e_solution.py').read_text()

    def cli(self, *args):
        return subprocess.run([sys.executable, 'app.py', *args], cwd=self.workspace,
                              text=True, capture_output=True, timeout=5)

    def configure(self):
        (self.workspace / 'settings.json').write_bytes(
            (self.workspace / 'settings.example.json').read_bytes())

    def oracle(self):
        return subprocess.run([sys.executable, str(ROOT / 'evals/oracles/preflight_e2e.py'),
                               str(self.workspace)], capture_output=True, text=True, timeout=20)

    def test_missing_environment_is_not_feature_red_or_green(self):
        result = self.cli('health')
        self.assertEqual(result.returncode, 3)
        self.assertIn('ENV_NOT_READY', result.stderr)
        self.assertNotEqual(self.oracle().returncode, 0)

    def test_readiness_can_pass_while_acceptance_is_red(self):
        self.configure()
        self.assertEqual(self.cli('health').stdout, 'ready\n')
        self.assertEqual(self.cli('set', 'evening').returncode, 0)
        self.assertNotEqual(self.cli('get').stdout, 'evening\n')
        self.assertNotEqual(self.oracle().returncode, 0)

    def test_real_persistence_solution_passes(self):
        self.configure()
        (self.workspace / 'app.py').write_text(self.solution)
        result = self.oracle()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_success_output_without_actual_persistence_fails(self):
        self.configure()
        fake = self.solution.replace("store.write_text(json.dumps({'value': sys.argv[2]}), encoding='utf-8')", 'pass')
        self.assertNotEqual(fake, self.solution)
        (self.workspace / 'app.py').write_text(fake)
        self.assertNotEqual(self.oracle().returncode, 0)

    def test_oracle_rejects_lossy_whitespace_handling(self):
        self.configure()
        lossy = self.solution.replace("{'value': sys.argv[2]}", "{'value': sys.argv[2].strip()}")
        self.assertNotEqual(lossy, self.solution)
        (self.workspace / 'app.py').write_text(lossy)
        self.assertNotEqual(self.oracle().returncode, 0)

    def test_oracle_rejects_skipped_exit_zero(self):
        self.configure()
        (self.workspace / 'app.py').write_text("print('SKIPPED: no tests discovered')\n")
        self.assertNotEqual(self.oracle().returncode, 0)


if __name__ == '__main__':
    unittest.main()
