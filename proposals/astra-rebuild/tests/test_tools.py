from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


installer = load("installer", "scripts/install.py")
catalog = load("catalog", "scripts/validate_catalog.py")
evidence = load("evidence", "skills/experiment-evidence/scripts/validate_record.py")
evals = load("eval_runner", "scripts/run_evals.py")


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.target = Path(self.temp.name) / "project with spaces"
        self.target.mkdir()
        subprocess.run(["git", "init", "-q", str(self.target)], check=True)

    def test_selects_only_requested_pack_and_deduplicates(self):
        result = installer.select_skills(ROOT, ["research"], ["experiment-evidence"])
        self.assertEqual(result, ["experiment-evidence", "research-exploration", "research-synthesis"])

    def test_unknown_and_traversal_names_fail(self):
        for packs, names in ((["unknown"], []), ([], ["../x"]), ([], ["unknown"])):
            with self.subTest(packs=packs, names=names), self.assertRaises(ValueError):
                installer.select_skills(ROOT, packs, names)

    def test_install_is_selective_and_idempotent(self):
        installer.install(ROOT, self.target, ["contract-change"])
        skills = self.target / ".agents/skills"
        self.assertEqual([p.name for p in skills.iterdir()], ["contract-change"])
        self.assertEqual(installer.install(ROOT, self.target, ["contract-change"]), [])
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertFalse((self.target / ".claude").exists())

    def test_dry_run_writes_nothing(self):
        before = sorted(p.relative_to(self.target) for p in self.target.rglob("*"))
        self.assertTrue(installer.install(ROOT, self.target, ["contract-change"], dry_run=True, init_contract=True))
        self.assertEqual(before, sorted(p.relative_to(self.target) for p in self.target.rglob("*")))

    def test_contract_creation_is_explicit(self):
        installer.install(ROOT, self.target, [], init_contract=True)
        self.assertEqual((self.target / "AGENTS.md").read_bytes(), (ROOT / "templates/AGENTS.md").read_bytes())

    def test_preflights_all_collisions_before_writing(self):
        dest = self.target / ".agents/skills/research-synthesis"
        dest.mkdir(parents=True)
        (dest / "user.txt").write_text("keep")
        with self.assertRaises(ValueError):
            installer.install(ROOT, self.target, ["contract-change", "research-synthesis"])
        self.assertFalse((self.target / ".agents/skills/contract-change").exists())
        self.assertEqual((dest / "user.txt").read_text(), "keep")

    def test_existing_instruction_refuses_without_partial_install(self):
        (self.target / "AGENTS.md").write_text("user policy")
        with self.assertRaises(ValueError):
            installer.install(ROOT, self.target, ["contract-change"], init_contract=True)
        self.assertEqual((self.target / "AGENTS.md").read_text(), "user policy")
        self.assertFalse((self.target / ".agents").exists())

    def test_preserves_third_party_skill(self):
        third = self.target / ".agents/skills/third-party"
        third.mkdir(parents=True)
        (third / "SKILL.md").write_text("user data")
        installer.install(ROOT, self.target, ["contract-change"])
        self.assertEqual((third / "SKILL.md").read_text(), "user data")

    def test_rejects_symlink_parents(self):
        outside = Path(self.temp.name) / "outside"
        outside.mkdir()
        (self.target / ".agents").symlink_to(outside)
        with self.assertRaises(ValueError):
            installer.install(ROOT, self.target, ["contract-change"])
        self.assertEqual(list(outside.iterdir()), [])

    def test_rejects_legacy_directory_link(self):
        parent = self.target / ".agents"
        parent.mkdir()
        (parent / "skills").symlink_to(ROOT / "skills")
        with self.assertRaises(ValueError):
            installer.install(ROOT, self.target, ["contract-change"])

    def test_rejects_dangling_skill_link(self):
        dest = self.target / ".agents/skills"
        dest.mkdir(parents=True)
        (dest / "contract-change").symlink_to("missing")
        with self.assertRaises(ValueError):
            installer.install(ROOT, self.target, ["contract-change"])
        self.assertTrue((dest / "contract-change").is_symlink())

    def test_rejects_nested_workdir(self):
        nested = self.target / "src"
        nested.mkdir()
        with self.assertRaises(ValueError):
            installer.install(ROOT, nested, ["contract-change"])

    def test_cli_requires_explicit_selection(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/install.py"), str(self.target)], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.target / ".agents").exists())

    def test_rolls_back_only_owned_links_on_io_failure(self):
        original = Path.symlink_to
        count = 0
        def failing(path, target, **kwargs):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("simulated write failure")
            return original(path, target, **kwargs)
        with mock.patch.object(Path, "symlink_to", failing), self.assertRaises(OSError):
            installer.install(ROOT, self.target, ["contract-change", "research-synthesis"])
        self.assertFalse((self.target / ".agents/skills/contract-change").is_symlink())


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "result.txt").write_text("measured result\n")
        self.identity = {key: f"actual-{key}" for key in evidence.IDENTITY_KEYS}
        self.contract = {"version": 1, "use_id": "device-budget", "identity": self.identity,
                         "conditions": [{"id": "deadline", "obligation": "required", "source": "approved request",
                                         "criterion": "p99 <= 10ms", "method": "target-workload-run"}]}
        self.record = {"version": 1, "use_id": "device-budget", "identity": copy.deepcopy(self.identity),
                       "contract_sha256": "a" * 64,
                       "results": [{"id": "deadline", "status": "pass", "method": "target-workload-run",
                                    "artifacts": [{"path": "result.txt", "sha256": evidence.digest(self.root / "result.txt")}]}]}

    def check(self):
        return evidence.validate(self.contract, self.record, self.root, "a" * 64)

    def test_valid_record(self):
        self.assertEqual(self.check(), [])

    def test_each_identity_dimension_invalidates_proof(self):
        for key in self.identity:
            with self.subTest(key=key):
                original = self.record["identity"][key]
                self.record["identity"][key] = "different"
                self.assertTrue(self.check())
                self.record["identity"][key] = original

    def test_host_evidence_cannot_match_target_contract(self):
        self.record["identity"]["target"] = "host"
        self.assertTrue(self.check())

    def test_missing_required_result_blocks(self):
        self.record["results"] = []
        self.assertTrue(self.check())

    def test_required_status_cannot_be_waived_by_caveat(self):
        for status in ("fail", "not-measured", "not-applicable"):
            with self.subTest(status=status):
                self.record["results"][0].update(status=status, limits="provisional / no hardware")
                self.assertTrue(self.check())

    def test_optional_target_may_remain_unmet(self):
        self.contract["conditions"][0]["obligation"] = "target"
        self.record["results"][0].update(status="not-measured", artifacts=[])
        self.assertEqual(self.check(), [])

    def test_record_cannot_downgrade_obligation(self):
        self.record["results"][0]["obligation"] = "target"
        self.assertTrue(self.check())

    def test_digest_mismatch_detects_stale_result(self):
        (self.root / "result.txt").write_text("different result")
        self.assertTrue(self.check())

    def test_missing_artifact_cannot_pass(self):
        (self.root / "result.txt").unlink()
        self.assertTrue(self.check())

    def test_pass_requires_evidence(self):
        self.record["results"][0]["artifacts"] = []
        self.assertTrue(self.check())

    def test_method_mismatch(self):
        self.record["results"][0]["method"] = "host-only-test"
        self.assertTrue(self.check())

    def test_contract_digest_mismatch(self):
        self.record["contract_sha256"] = "b" * 64
        self.assertTrue(self.check())

    def test_use_scope_mismatch(self):
        self.record["use_id"] = "different-release"
        self.assertTrue(self.check())

    def test_duplicate_and_unknown_ids(self):
        self.record["results"].append(copy.deepcopy(self.record["results"][0]))
        self.assertTrue(self.check())
        self.record["results"][1]["id"] = "unknown"
        self.assertTrue(self.check())

    def test_out_of_scope_requires_reason(self):
        self.contract["conditions"][0]["obligation"] = "out-of-scope"
        self.record["results"][0]["status"] = "not-applicable"
        self.assertTrue(self.check())
        self.contract["conditions"][0]["reason"] = "outside this separately approved use"
        self.assertEqual(self.check(), [])

    def test_rejects_traversal_absolute_and_symlink_paths(self):
        (self.root / "link.txt").symlink_to(self.root / "result.txt")
        for path in ("../result.txt", "/etc/passwd", "C:/secret", "..\\secret", "link.txt"):
            with self.subTest(path=path):
                self.record["results"][0]["artifacts"][0]["path"] = path
                self.assertTrue(self.check())

    def test_malformed_json_types_fail_closed(self):
        self.record["results"][0]["status"] = []
        self.assertTrue(self.check())
        self.contract["conditions"][0]["obligation"] = {}
        self.assertTrue(self.check())
        self.assertTrue(evidence.validate([], self.record, self.root, "a" * 64))


class CatalogMutationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "catalog"
        self.root.mkdir()
        for directory in ("skills", "docs", "evals", "templates"):
            shutil.copytree(ROOT / directory, self.root / directory, ignore=shutil.ignore_patterns("__pycache__", "historical"))
        shutil.copyfile(ROOT / "packs.json", self.root / "packs.json")
        self.path = self.root / "skills/contract-change/SKILL.md"

    def test_hidden_required_load_graph_is_rejected(self):
        self.path.write_text(self.path.read_text().replace("---\n\n#", "metadata:\n  requires:\n    - other.md\n---\n\n#", 1))
        self.assertTrue(catalog.validate(self.root))

    def test_duplicate_frontmatter_is_rejected(self):
        self.path.write_text(self.path.read_text().replace("name: contract-change", "name: contract-change\nname: contract-change"))
        self.assertTrue(catalog.validate(self.root))

    def test_missing_reference_is_rejected(self):
        self.path.write_text(self.path.read_text() + "\n[Missing](references/missing.md)\n")
        self.assertTrue(catalog.validate(self.root))

    def test_reference_escape_is_rejected(self):
        self.path.write_text(self.path.read_text() + "\n[Outside](../../other.md)\n")
        self.assertTrue(catalog.validate(self.root))

    def test_missing_migration_destination_is_rejected(self):
        data = json.loads((self.root / "docs/migration-map.json").read_text())
        data["entries"][0]["destination"] = "missing.md"
        (self.root / "docs/migration-map.json").write_text(json.dumps(data))
        self.assertTrue(catalog.validate(self.root))

    def test_unknown_pack_member_is_rejected(self):
        data = json.loads((self.root / "packs.json").read_text())
        data["packs"]["research"].append("unknown-skill")
        (self.root / "packs.json").write_text(json.dumps(data))
        self.assertTrue(catalog.validate(self.root))

    def test_fixture_escape_is_rejected(self):
        data = json.loads((self.root / "evals/cases.json").read_text())
        data["cases"][0]["fixture"] = "../../templates"
        (self.root / "evals/cases.json").write_text(json.dumps(data))
        self.assertTrue(catalog.validate(self.root))


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.case = json.loads((ROOT / "evals/cases.json").read_text())["cases"][0]

    def test_catalog_validates_without_model_execution(self):
        self.assertEqual(catalog.validate(ROOT), [])

    def test_minimal_workspace_has_no_skills_or_oracle(self):
        workspace = self.root / "workspace"
        before = evals.prepare(ROOT, self.case, workspace, "minimal", None)
        self.assertEqual(before, evals.tree_digest(workspace))
        self.assertFalse((workspace / ".agents").exists())
        self.assertFalse((workspace / "oracles").exists())
        self.assertTrue((workspace / "app.py").exists())

    def test_selected_specialists_are_copied_not_linked(self):
        case = copy.deepcopy(self.case)
        case["skills"] = ["contract-change"]
        workspace = self.root / "workspace"
        evals.prepare(ROOT, case, workspace, "specialists", None)
        package = workspace / ".agents/skills/contract-change"
        self.assertTrue((package / "SKILL.md").exists())
        self.assertFalse(package.is_symlink())

    def test_baseline_is_explicit_and_cannot_overwrite_fixture(self):
        baseline = self.root / "baseline"
        baseline.mkdir()
        (baseline / "AGENTS.md").write_text("old policy")
        (baseline / "app.py").write_text("replace product")
        with self.assertRaises(ValueError):
            evals.prepare(ROOT, self.case, self.root / "workspace", "baseline", baseline)
        self.assertNotEqual((self.root / "workspace/app.py").read_text(), "replace product")

    def test_snapshot_digest_changes_with_content(self):
        path = self.root / "file.txt"
        path.write_text("one")
        first = evals.tree_digest(self.root)
        path.write_text("two")
        self.assertNotEqual(first, evals.tree_digest(self.root))

    def test_snapshot_ignores_git_and_python_cache(self):
        (self.root / "file.txt").write_text("content")
        first = evals.tree_digest(self.root)
        for name in (".git", "__pycache__"):
            (self.root / name).mkdir()
            (self.root / name / "noise").write_text("not part of the input")
        self.assertEqual(first, evals.tree_digest(self.root))

    def test_snapshot_rejects_symlink(self):
        (self.root / "linked").symlink_to(ROOT / "AGENTS.md")
        with self.assertRaises(ValueError):
            evals.tree_digest(self.root)

    def test_dry_run_requires_no_adapter_or_model(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/run_evals.py"), "--case", "small-fix"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertFalse(json.loads(result.stdout)["execute"])

    def test_unknown_case_rejected(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/run_evals.py"), "--case", "unknown"], capture_output=True)
        self.assertNotEqual(result.returncode, 0)

    def test_fake_adapter_is_not_behavioral_qualification(self):
        workspace = self.root / "workspace"
        before = evals.prepare(ROOT, self.case, workspace, "minimal", None)
        adapter = self.root / "fake.py"
        # Exercise the protocol, not an LLM. Oracle execution is also delegated.
        adapter.write_text('import json,sys\nr=json.load(sys.stdin)\nprint(json.dumps({"status":"completed","model":"FAKE-NOT-ASTRA","exit_code":0}))\n')
        result = evals.run_case(ROOT, self.case, workspace, self.root / "receipt",
                               [sys.executable, str(adapter)], "requested-model", "minimal", 5, before)
        self.assertEqual(result["reported_model"], "FAKE-NOT-ASTRA")
        self.assertTrue(result["oracle_pass"])
        self.assertEqual(result["review_status"], "pending")
        self.assertIsNone(result["usage"])

    def test_failed_adapter_cannot_pass_oracle(self):
        workspace = self.root / "workspace"
        before = evals.prepare(ROOT, self.case, workspace, "minimal", None)
        result = evals.run_case(ROOT, self.case, workspace, self.root / "receipt",
                               [sys.executable, "-c", "raise SystemExit(9)"], "model", "minimal", 5, before)
        self.assertTrue(result["adapter_error"])
        self.assertIsNone(result["oracle_pass"])

    def test_timeout_cannot_pass(self):
        workspace = self.root / "workspace"
        before = evals.prepare(ROOT, self.case, workspace, "minimal", None)
        result = evals.run_case(ROOT, self.case, workspace, self.root / "receipt",
                               [sys.executable, "-c", "import time; time.sleep(1)"], "model", "minimal", 0.05, before)
        self.assertTrue(result["adapter_error"])

    def test_oracle_failure_is_recorded(self):
        workspace = self.root / "workspace"
        before = evals.prepare(ROOT, self.case, workspace, "minimal", None)
        adapter = self.root / "fake.py"
        adapter.write_text('import json,sys\nr=json.load(sys.stdin)\nprint(json.dumps({"status":"completed","model":"FAKE","exit_code":1}))\n')
        result = evals.run_case(ROOT, self.case, workspace, self.root / "receipt",
                               [sys.executable, str(adapter)], "model", "minimal", 5, before)
        self.assertFalse(result["oracle_pass"])

    def test_product_oracles_accept_known_good_implementations(self):
        sources = {
            "small-fix": "def take(items, count):\n    if count < 0: raise ValueError()\n    return items[:count]\n",
            "complete-feature": "def parse_port(value):\n    if not isinstance(value, str) or not value or any(c not in '0123456789' for c in value): raise ValueError()\n    result = int(value)\n    if not 1 <= result <= 65535: raise ValueError()\n    return result\n",
            "bounded-resources": "from collections import deque\nclass Recorder:\n    def __init__(self, capacity):\n        if type(capacity) is not int or capacity <= 0: raise ValueError()\n        self.events = deque(maxlen=capacity)\n    def append(self, event): self.events.append(event)\n    def snapshot(self): return list(self.events)\n",
            "break-allowed": "def sum_amounts(values):\n    return sum(values)\n",
        }
        cases = json.loads((ROOT / "evals/cases.json").read_text())["cases"]
        for case in cases:
            if case["oracle"]:
                with self.subTest(case=case["id"]):
                    workspace = self.root / case["id"]
                    evals.prepare(ROOT, case, workspace, "minimal", None)
                    (workspace / "app.py").write_text(sources[case["id"]])
                    if case["id"] == "break-allowed":
                        (workspace / "client.py").write_text("from app import sum_amounts\ndef invoice(values): return sum_amounts(values)\n")
                    result = subprocess.run([sys.executable, str(ROOT / "evals/oracles" / case["oracle"]), str(workspace)], capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stderr)

    def test_product_oracles_reject_original_bugs(self):
        cases = json.loads((ROOT / "evals/cases.json").read_text())["cases"]
        for case in cases:
            if case["oracle"]:
                with self.subTest(case=case["id"]):
                    # Only trusted, checked-in fixtures are executed locally here.
                    workspace = self.root / case["id"]
                    evals.prepare(ROOT, case, workspace, "minimal", None)
                    result = subprocess.run([sys.executable, str(ROOT / "evals/oracles" / case["oracle"]), str(workspace)], capture_output=True)
                    self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
