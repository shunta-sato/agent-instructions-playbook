from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.install_skills import install, selection, ROOT
from scripts.validate_playbook import validate
from scripts.run_task_evals import run_process, run_trial

spec = importlib.util.spec_from_file_location('evidence_checker', ROOT / '.agents/skills/embedded-runtime-evidence/scripts/verify_evidence.py')
evidence = importlib.util.module_from_spec(spec)
spec.loader.exec_module(evidence)


class CatalogTests(unittest.TestCase):
    def test_current_catalog(self):
        self.assertEqual(validate(), [])

    def test_default_is_selective(self):
        self.assertEqual(selection(ROOT, [], []), ['agentic-tdd','boundary-migration','bug-investigation-and-rca','decision-analysis','preflight-engineering','repo-onboarding','workflow-contracts'])
        self.assertEqual(selection(ROOT, [], ['ui-design']), ['ui-design'])

    def test_explicit_profiles_deduplicate(self):
        names=selection(ROOT,['embedded','backend'],[])
        self.assertEqual(names.count('runtime-performance'),1)
        self.assertNotIn('ui-design',names)

    def test_unknown_selection_rejected(self):
        for profiles,skills in [(['missing'],[]),([],['dev-workflow']),([],['../README'])]:
            with self.assertRaises(ValueError): selection(ROOT,profiles,skills)


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.target=Path(self.tmp.name)/'project';self.target.mkdir()
        subprocess.run(['git','init','-q',str(self.target)],check=True,capture_output=True)

    def test_idempotent_native_selection(self):
        first=install(self.target,ROOT,['ui-design'],'both')
        self.assertEqual(first,install(self.target,ROOT,['ui-design'],'both'))
        self.assertTrue((self.target/'.agents/skills/ui-design').is_symlink())
        self.assertTrue((self.target/'.claude/skills/ui-design').is_symlink())
        self.assertFalse((self.target/'AGENTS.md').exists())

    def test_change_selection_removes_only_owned(self):
        install(self.target,ROOT,['ui-design'],'codex')
        third=self.target/'.agents/skills/third-party';third.mkdir()
        install(self.target,ROOT,['auth-session'],'codex')
        self.assertFalse((self.target/'.agents/skills/ui-design').exists())
        self.assertTrue(third.is_dir())
        self.assertTrue((self.target/'.agents/skills/auth-session').is_symlink())

    def test_dry_run_no_mutation(self):
        install(self.target,ROOT,['ui-design'],'both',True)
        self.assertEqual([p.name for p in self.target.iterdir()],['.git'])

    def test_collision_preflight_no_partial_install(self):
        path=self.target/'.agents/skills/ui-design';path.mkdir(parents=True)
        with self.assertRaises(ValueError): install(self.target,ROOT,['auth-session','ui-design'],'codex')
        self.assertFalse((self.target/'.agents/skills/auth-session').exists())
        self.assertTrue(path.is_dir())

    def test_legacy_aggregate_link_refused(self):
        (self.target/'.agents').mkdir()
        (self.target/'.agents/skills').symlink_to(ROOT/'.agents/skills',target_is_directory=True)
        with self.assertRaises(ValueError): install(self.target,ROOT,['ui-design'],'codex')
        self.assertTrue((ROOT/'.agents/skills/ui-design/SKILL.md').is_file())

    def test_parent_symlink_refused(self):
        outside=Path(self.tmp.name)/'outside';outside.mkdir()
        (self.target/'.agents').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(ValueError): install(self.target,ROOT,['ui-design'],'codex')
        self.assertEqual(list(outside.iterdir()),[])

    def test_modified_managed_link_refused(self):
        install(self.target,ROOT,['ui-design'],'codex')
        path=self.target/'.agents/skills/ui-design';path.unlink();path.mkdir()
        (path/'mine.txt').write_text('preserve')
        with self.assertRaises(ValueError): install(self.target,ROOT,['auth-session'],'codex')
        self.assertEqual((path/'mine.txt').read_text(),'preserve')

    def test_invalid_manifest_refused(self):
        manifest=self.target/'.playbook-install.json'
        for payload in [[],{'schema_version':1},{'schema_version':2,'links':{'../victim':'/tmp/victim'}}]:
            manifest.write_text(json.dumps(payload))
            with self.assertRaises(ValueError): install(self.target,ROOT,['ui-design'],'codex')

    def test_invalid_direct_api_name_refused(self):
        with self.assertRaises(ValueError): install(self.target,ROOT,['../../escape'],'codex')

    def test_missing_source_refused(self):
        with self.assertRaises(ValueError): install(self.target,ROOT,['not-a-skill'],'codex')

    def test_worktree_git_file_supported(self):
        (self.target/'seed').write_text('seed')
        subprocess.run(['git','-C',str(self.target),'add','.'],check=True)
        subprocess.run(['git','-C',str(self.target),'-c','user.name=Test','-c','user.email=t@example.invalid','-c','commit.gpgsign=false','commit','-qm','seed'],check=True)
        linked=Path(self.tmp.name)/'linked'
        subprocess.run(['git','-C',str(self.target),'worktree','add','-q','-b','fixture',str(linked)],check=True)
        self.assertTrue((linked/'.git').is_file())
        install(linked,ROOT,['ui-design'],'codex')
        self.assertTrue((linked/'.agents/skills/ui-design').is_symlink())

    def test_write_failure_restores_owned_links(self):
        install(self.target,ROOT,['ui-design'],'codex')
        before=(self.target/'.playbook-install.json').read_bytes()
        original=Path.symlink_to
        def fail_new(path,*args,**kwargs):
            if path.name=='auth-session': raise OSError('injected write failure')
            return original(path,*args,**kwargs)
        with patch.object(Path,'symlink_to',fail_new):
            with self.assertRaises(OSError): install(self.target,ROOT,['auth-session'],'codex')
        self.assertEqual((self.target/'.playbook-install.json').read_bytes(),before)
        self.assertTrue((self.target/'.agents/skills/ui-design').is_symlink())


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
        (self.root/'measurement.txt').write_text('raw observation')
        identity={k:f'known-{k}' for k in evidence.IDENTITY_FIELDS}
        self.contract={'schema_version':1,'requirements':[dict(identity,id='latency',obligation='required',criterion='accepted deadline',source='product-contract')]}
        self.results={'schema_version':1,'results':[dict(identity,id='latency',status='pass',artifacts=[{'path':'measurement.txt','sha256':hashlib.sha256(b'raw observation').hexdigest()}])]}

    def test_consistent(self): self.assertEqual(evidence.verify(self.contract,self.results,self.root),[])
    def test_required_missing(self):
        self.results['results']=[];self.assertTrue(evidence.verify(self.contract,self.results,self.root))
    def test_required_unmeasured(self):
        self.results['results'][0]['status']='not-measured';self.assertTrue(evidence.verify(self.contract,self.results,self.root))
    def test_optional_missing_is_allowed(self):
        self.contract['requirements'][0]['obligation']='target';self.results['results']=[]
        self.assertEqual(evidence.verify(self.contract,self.results,self.root),[])
    def test_optional_failed_is_allowed(self):
        self.contract['requirements'][0]['obligation']='target';self.results['results'][0]['status']='fail'
        self.assertEqual(evidence.verify(self.contract,self.results,self.root),[])
    def test_each_identity_mismatch(self):
        for key in evidence.IDENTITY_FIELDS:
            changed=copy.deepcopy(self.results);changed['results'][0][key]='other'
            self.assertTrue(evidence.verify(self.contract,changed,self.root),key)
    def test_tampered_artifact(self):
        (self.root/'measurement.txt').write_text('changed');self.assertTrue(evidence.verify(self.contract,self.results,self.root))
    def test_absent_artifact(self):
        (self.root/'measurement.txt').unlink();self.assertTrue(evidence.verify(self.contract,self.results,self.root))
    def test_path_traversal(self):
        self.results['results'][0]['artifacts'][0]['path']='../escape'
        self.assertTrue(evidence.verify(self.contract,self.results,self.root))
    def test_symlink_refused(self):
        (self.root/'alias').symlink_to(self.root/'measurement.txt')
        self.results['results'][0]['artifacts'][0]['path']='alias'
        self.assertTrue(evidence.verify(self.contract,self.results,self.root))
    def test_duplicate_ids(self):
        self.results['results'].append(self.results['results'][0])
        self.assertTrue(evidence.verify(self.contract,self.results,self.root))
    def test_missing_contract_source(self):
        self.contract['requirements'][0]['source']=''
        self.assertTrue(evidence.verify(self.contract,self.results,self.root))
    def test_unexpected_result(self):
        extra=copy.deepcopy(self.results['results'][0]);extra['id']='invented'
        self.results['results'].append(extra);self.assertTrue(evidence.verify(self.contract,self.results,self.root))
    def test_pass_without_artifact(self):
        self.results['results'][0]['artifacts']=[];self.assertTrue(evidence.verify(self.contract,self.results,self.root))


class TaskEvaluationTests(unittest.TestCase):
    def test_nonzero_and_missing_executable(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(run_process([sys.executable,'-c','raise SystemExit(3)'],Path(tmp),None,3)['exit_code'],3)
            self.assertEqual(run_process(['/no/such/program'],Path(tmp),None,3)['status'],'launch-failed')

    def test_timeout_does_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=run_process([sys.executable,'-c','import time; time.sleep(20)'],Path(tmp),None,.05)
            self.assertEqual(r['status'],'timeout')

    def fake_trial(self,root:Path,fix:bool,metadata:bool=True):
        script=root/'fake.py'
        script.write_text('''import json,sys
from pathlib import Path
p=json.load(sys.stdin)
'''+("Path(p['workspace'],'app.py').write_text('def slug(value):\\n    return value.strip().lower()\\n')\n" if fix else '')+('''Path(p['metadata_path']).write_text(json.dumps({'resolved_model':'fixture-model','harness':'fixture','harness_version':'test'}))
Path(p['trace_path']).write_text(json.dumps({'type':'fixture-only'})+'\\n')
''' if metadata else ''))
        case=json.loads((ROOT/'evals/cases.json').read_text())['cases'][0]
        return run_trial(case,'minimal',root/'trial',[sys.executable,str(script)],'fixture-model','fixture',None,5)

    def test_fake_success_is_still_behavior_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=self.fake_trial(Path(tmp),True)
            self.assertEqual(result['functional'],'pass')
            self.assertEqual(result['status'],'needs-behavior-review')

    def test_agent_exit_zero_is_not_functional_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.fake_trial(Path(tmp),False)['functional'],'fail')

    def test_missing_metadata_never_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.fake_trial(Path(tmp),True,False)['status'],'incomplete')

    def test_all_oracles_reject_original_and_accept_real_solution(self):
        solutions={
          'tiny-fix':{'app.py':'def slug(value):\n    return value.strip().lower()\n'},
          'complete-feature':{'app.py':'import sys\ntry:\n    total=sum(int(s) for s in sys.stdin if s.strip())\nexcept ValueError:\n    print("invalid integer",file=sys.stderr);sys.exit(1)\nprint(total)\n'},
          'preflight-e2e-persistence':{'app.py':(ROOT/'tests/fixtures/preflight_e2e_solution.py').read_text(),'settings.json':'{\"store\": \"state.json\"}\n'},
          'contract-replacement':{'app.py':'def double_value(value):\n    return value*2\n','callers.py':'from app import double_value\ndef call(value):\n    return double_value(value)\n'}
        }
        for case in json.loads((ROOT/'evals/cases.json').read_text())['cases']:
            if not case['oracle']: continue
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                for name,content in case['files'].items(): (root/name).write_text(content)
                cmd=[sys.executable,str(ROOT/'evals/oracles'/case['oracle']),str(root)]
                self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0,case['id'])
                for name,content in solutions[case['id']].items(): (root/name).write_text(content)
                self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0,case['id'])


if __name__=='__main__': unittest.main()
