"""Round-7 (threads 3595822872/3595823226): F1 predicate integer precision, F2 claim --source
injection, F3 the unified axis_binding n/label/note primitive, F4 the structured axis-command
parser. Round-8 (threads 3604143957/3604144113): A1 axis_effective required for n>1, A2
env-dash-option grammar + exec robustness, A3 metric-name injection, A4 big-int overflow.
Sibling files were at/near the 400-line budget; shared builders imported from test_research_os."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from scripts import check_research_evidence as cre
from scripts import research_ledger as rl
from scripts import research_run as rr
from tests.test_research_os import (
    _git_init, build_chain, make_claim, make_prereg, make_result, run_cli,
)


# --- F1: predicate integer precision at the 2**53 float-rounding boundary ----
class PredicateIntegerPrecisionTests(unittest.TestCase):
    """normalized_predicate must NOT float()-cast: 2**53 and 2**53+1 both round to the same
    double, so casting would wrongly collapse two distinct thresholds/bounds into one."""

    BIG, BIG_PLUS_1 = 2**53, 2**53 + 1

    def test_threshold_precision_not_collapsed(self) -> None:
        a = {"metric": "err", "comparator": "<", "threshold": self.BIG}
        b = {"metric": "err", "comparator": "<", "threshold": self.BIG_PLUS_1}
        self.assertNotEqual(rl.normalized_predicate(a), rl.normalized_predicate(b))

    def test_equivalence_bounds_precision_not_collapsed(self) -> None:
        a = {"type": rl.PREDICATE_EQUIVALENCE, "metric": "err", "lower": 0, "upper": self.BIG}
        b = {"type": rl.PREDICATE_EQUIVALENCE, "metric": "err", "lower": 0, "upper": self.BIG_PLUS_1}
        self.assertNotEqual(rl.normalized_predicate(a), rl.normalized_predicate(b))

    def test_int_and_equal_valued_float_threshold_still_equal(self) -> None:
        a = {"metric": "err", "comparator": "<", "threshold": 20}
        b = {"metric": "err", "comparator": "<", "threshold": 20.0}
        self.assertEqual(rl.normalized_predicate(a), rl.normalized_predicate(b))

    def test_predicate_identity_errors_refuses_2_53_boundary_aggregation(self) -> None:
        prereg1 = make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1")
        prereg1["disconfirm"] = {"metric": "err", "comparator": "<", "threshold": self.BIG}
        prereg2 = make_prereg("E-0002", "2026-01-01T00:00:00+00:00", "d2")
        prereg2["disconfirm"] = {"metric": "err", "comparator": "<", "threshold": self.BIG_PLUS_1}
        records = build_chain([prereg1, prereg2])
        self.assertTrue(rl.predicate_identity_errors(records, ["E-0001", "E-0002"]))


# --- F2: claim --source Markdown/free-text injection -------------------------
class SourceInjectionTests(unittest.TestCase):
    INJECTION = "probe.py\n\n## C-FAKE\nmodel improved 99%"

    def _register_and_execute(self, base: list[str]) -> None:
        from tests.test_research_os import LaunderingTests
        run_cli(base + ["register", "--hypothesis", "h", "--metric", "err", "--comparator", "<",
                        "--threshold", "0.1", "--command", LaunderingTests.CMD])
        run_cli(base + ["execute", "--experiment-id", "E-0001"])

    def test_injection_source_refused_at_claim_time(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = ["--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl")]
            self._register_and_execute(base)
            rc, _ = run_cli(base + ["claim", "--metric", "err", "--evidence", "E-0001",
                                    "--source", self.INJECTION])
        self.assertEqual(rc, 1)

    def test_valid_path_and_url_sources_accepted_and_never_rendered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "l.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            self._register_and_execute(base)
            rc, _ = run_cli(base + ["claim", "--metric", "err", "--evidence", "E-0001",
                                    "--source", "experiments/probe.py",
                                    "--source", "https://example.com/paper"])
            self.assertEqual(rc, 0)
            records = rl.load_research_records(ledger)
            claim = next(r for r in records if r["record_type"] == rl.CLAIM)
            self.assertEqual(claim["sources"], ["experiments/probe.py", "https://example.com/paper"])
            rendered = rl.render_claims(records)
        self.assertNotIn("sources:", rendered)
        self.assertNotIn("experiments/probe.py", rendered)

    def test_forged_ledger_newline_source_flagged(self) -> None:
        prereg = make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1")
        result = make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.05})
        claim = {
            "schema_version": 1, "record_type": rl.CLAIM, "claim_id": "C-0001",
            "created_at": "2026-01-03T00:00:00+00:00", "metric": "err", "evidence": ["E-0001"],
            "outcome_basis": [{"experiment_id": "E-0001", "outcome": "disconfirmed"}],
            "sources": [self.INJECTION], "n": 1,
        }
        records = build_chain([prereg, result, claim])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertTrue(any(f.startswith("claim-source-invalid:") for f in findings), findings)

    def test_validate_source_unit(self) -> None:
        self.assertTrue(rr.validate_source(self.INJECTION))
        self.assertEqual(rr.validate_source("experiments/probe.py"), [])
        self.assertEqual(rr.validate_source("https://example.com/x"), [])
        self.assertTrue(rr.validate_source("#not-a-path"))


# --- F4: parse_axis_command + the structured wrapper/-c/-e/duplicate contract -
class ParseAxisCommandTests(unittest.TestCase):
    def test_plain_command_no_env_prefix(self) -> None:
        env, argv = rl.parse_axis_command("python3 probe.py --seed=1")
        self.assertEqual(env, [])
        self.assertEqual(argv, ["python3", "probe.py", "--seed=1"])

    def test_env_var_prefix_peeled(self) -> None:
        env, argv = rl.parse_axis_command("CUDA_VISIBLE_DEVICES=0 python3 probe.py --seed=1")
        self.assertEqual(env, [("CUDA_VISIBLE_DEVICES", "0")])
        self.assertEqual(argv, ["python3", "probe.py", "--seed=1"])

    def test_env_wrapper_is_transparent(self) -> None:
        # `env bash -c ...`: parse_axis_command passes through the harmless `env` and stops
        # at `bash`, so the wrapper check downstream sees the REAL wrapper (bash -c).
        env, argv = rl.parse_axis_command("env bash -c 'python3 probe.py' --seed=1")
        self.assertEqual(env, [])
        self.assertEqual(argv[0], "bash")


class RegistrationRefusesShellBypassesTests(unittest.TestCase):
    def _register(self, tmp: str, axis: str, command: str) -> tuple[int, str]:
        return run_cli([
            "--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl"),
            "register", "--hypothesis", "h", "--metric", "err",
            "--comparator", "<", "--threshold", "0.1", "--command", command,
            "--variation-axis", axis,
        ])

    def test_env_bash_c_repro_refused_at_registration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc, _ = self._register(tmp, "seed=1", "env bash -c 'python3 probe.py' --seed=1")
        self.assertEqual(rc, 1)

    def test_bash_xc_combined_flag_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc, _ = self._register(tmp, "seed=1", "bash -xc './probe.py' --seed=1")
        self.assertEqual(rc, 1)

    def test_duplicate_axis_key_in_command_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc, _ = self._register(tmp, "seed=1", "run --seed=1 --seed=2")
        self.assertEqual(rc, 1)

    def test_env_dash_option_refused_at_registration(self) -> None:
        # A2 (thread 4113 P2): ``env -u UNUSED ...`` must not silently become argv[0]="-u".
        with tempfile.TemporaryDirectory() as tmp:
            rc, _ = self._register(tmp, "seed=1", "env -u UNUSED /usr/bin/python3 probe.py --seed=1")
        self.assertEqual(rc, 1)


class ForgedLedgerBypassCollapsesToOneTests(unittest.TestCase):
    def test_env_bash_c_forged_ledger_collapses_to_n_one(self) -> None:
        cmd1 = "env bash -c 'python3 probe.py' --seed=1"
        cmd2 = "env bash -c 'python3 probe.py' --seed=2"
        records = build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1", command=cmd1, axis="seed=1"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.5}),
            make_prereg("E-0002", "2026-01-03T00:00:00+00:00", "d2", command=cmd2, axis="seed=2"),
            make_result("E-0002", "2026-01-04T00:00:00+00:00", "d2", {"err": 0.5}),
        ])
        n, note = rl.claim_n_and_note(records, ["E-0001", "E-0002"])
        self.assertEqual(n, 1)
        self.assertIn("not structurally bound", note)

    def test_env_dash_option_forged_ledger_collapses_to_n_one(self) -> None:
        # A2: hand-forged past the (now-refusing) CLI, the same command still can't bind an axis.
        cmd1 = "env -u UNUSED /usr/bin/python3 probe.py --seed=1"
        cmd2 = "env -u UNUSED /usr/bin/python3 probe.py --seed=2"
        records = build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1", command=cmd1, axis="seed=1"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.5}),
            make_prereg("E-0002", "2026-01-03T00:00:00+00:00", "d2", command=cmd2, axis="seed=2"),
            make_result("E-0002", "2026-01-04T00:00:00+00:00", "d2", {"err": 0.5}),
        ])
        n, note = rl.claim_n_and_note(records, ["E-0001", "E-0002"])
        self.assertEqual(n, 1)
        self.assertIn("not structurally bound", note)


class EnvPrefixExecutionTests(unittest.TestCase):
    # A probe FILE (not inline -c, for the same simple-command reason as the sibling axis tests).
    PROBE = ("import os, sys, json\n"
             "v = int(sys.argv[1].split('=')[1])\n"
             "open(os.environ['RESEARCH_RUN_DIR'] + '/result.json', 'w').write(json.dumps("
             "{'seed': v, 'axis_effective': v, 'cuda': os.environ.get('CUDA_VISIBLE_DEVICES')}))\n")

    def test_env_prefixed_axis_command_executes_and_env_reaches_probe(self) -> None:
        # CUDA_VISIBLE_DEVICES=0 python3 probe.py --seed=1 must run the REAL probe under
        # shell=False (axis binds to its true argv) with the env assignment reaching it — not
        # raise FileNotFoundError trying to exec "CUDA_VISIBLE_DEVICES=0" as argv[0].
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "probe.py").write_text(self.PROBE, encoding="utf-8")
            ledger = root / "l.jsonl"
            base = ["--repo-root", str(root), "--ledger", str(ledger)]
            cmd = f"CUDA_VISIBLE_DEVICES=0 {sys.executable} probe.py --seed=1"
            rc_reg, _ = run_cli(base + [
                "register", "--hypothesis", "h", "--metric", "seed", "--comparator", ">=",
                "--threshold", "0", "--command", cmd, "--variation-axis", "seed=1"])
            self.assertEqual(rc_reg, 0)
            rc_exec, _ = run_cli(base + ["execute", "--experiment-id", "E-0001"])
            result = rl.find_result(rl.load_research_records(ledger), "E-0001")
        self.assertEqual(rc_exec, 0)
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["metrics"]["cuda"], "0")


# --- F3: axis_binding is the ONE source for n, labels, and note --------------
class AxisBindingLabelConsistencyTests(unittest.TestCase):
    """The C-0002-style legacy/unbound axis (real command has no args at all) re-derives to
    the neutral label, never raw text, and n/label counts can never disagree."""

    def test_unbound_legacy_axis_renders_unverified_configuration(self) -> None:
        records = build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1", command="python3 probe.py",
                        axis="log_path=fixture-a/app.log; repeats=3,median"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.5}),
        ])
        binding = rl.axis_binding(records, ["E-0001"])
        self.assertEqual(binding["n"], 1)
        self.assertEqual(binding["labels"], ["unverified configuration"])
        self.assertFalse(binding["valid"])

    def test_valid_multi_axis_labels_match_n(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "probe.py").write_text(
                "import sys, os, json\nv = int(sys.argv[1].split('=')[1])\n"
                "open(os.environ['RESEARCH_RUN_DIR'] + '/result.json', 'w').write(json.dumps("
                "{'seed': v, 'axis_effective': v}))\n", encoding="utf-8")
            ledger = root / "l.jsonl"
            base = ["--repo-root", str(root), "--ledger", str(ledger)]
            for seed in (1, 2):
                run_cli(base + [
                    "register", "--hypothesis", "h", "--metric", "seed", "--comparator", ">=",
                    "--threshold", "0", "--command", f"{sys.executable} probe.py --seed={seed}",
                    "--variation-axis", f"seed={seed}"])
                run_cli(base + ["execute", "--experiment-id", f"E-000{seed}"])
            binding = rl.axis_binding(rl.load_research_records(ledger), ["E-0001", "E-0002"])
        self.assertEqual(binding["n"], 2)
        self.assertEqual(len(binding["labels"]), binding["n"])
        self.assertEqual(binding["labels"], ["seed=1", "seed=2"])


class RealLedgersRerenderTests(unittest.TestCase):
    """Both real claims views re-render clean of the legacy unbound-axis string, and
    --check-ledger still passes (grandfathering: not an error)."""

    def _rerender(self, ledger_rel: str) -> str:
        repo_root = Path(__file__).resolve().parents[1]
        return rl.render_claims(rl.load_research_records(repo_root / ledger_rel))

    def test_canonical_ledger_c0002_no_longer_shows_legacy_axis_text(self) -> None:
        rendered = self._rerender(rl.LEDGER_REL)
        self.assertNotIn("corrected-predicate-of-E-0003", rendered)
        self.assertIn("configurations: unverified configuration", rendered)

    def test_sort_probe_ledger_c0001_no_longer_shows_legacy_axis_text(self) -> None:
        rendered = self._rerender("experiments/sort-degradation-probe/ledger.jsonl")
        self.assertNotIn("swap_fraction=0.01", rendered)
        self.assertIn("configurations: unverified configuration", rendered)

    def test_check_ledger_still_passes_both_real_ledgers(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        for ledger_rel in (rl.LEDGER_REL, "experiments/sort-degradation-probe/ledger.jsonl"):
            ledger = repo_root / ledger_rel
            records = rl.load_research_records(ledger)
            findings = cre.check_ledger(records, repo_root, ledger)
            self.assertEqual(findings, [], (ledger_rel, findings))

# --- (A2) exec-setup failure is a clean recorded failure, never a traceback --
class ExecSetupErrorTests(unittest.TestCase):
    def test_exec_setup_error_is_clean_not_a_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "l.jsonl"
            base = ["--repo-root", str(root), "--ledger", str(ledger)]
            cmd = "/nonexistent/binary --seed=1"
            rc_reg, _ = run_cli(base + [
                "register", "--hypothesis", "h", "--metric", "seed", "--comparator", ">=",
                "--threshold", "0", "--command", cmd, "--variation-axis", "seed=1"])
            self.assertEqual(rc_reg, 0)
            rc_exec, _ = run_cli(base + ["execute", "--experiment-id", "E-0001"])
            result = rl.find_result(rl.load_research_records(ledger), "E-0001")
        self.assertEqual(rc_exec, 0)  # the CLI subcommand itself completes cleanly, no traceback
        self.assertNotEqual(result["exit_code"], 0)  # but the recorded execution failed
        self.assertEqual(result["outcome"], "not-evaluable")

# --- (A1) axis_effective is REQUIRED for n>1 ----------------------------------
class AxisEffectiveRequiredForNGreaterThanOneTests(unittest.TestCase):
    """thread 4113 P1: a probe that ignores argv must NOT inflate n; axis_effective must confirm."""
    IGNORES_ARGV_PROBE = ("import os, json\n"
                           "open(os.environ['RESEARCH_RUN_DIR'] + '/result.json', 'w')."
                           "write(json.dumps({'score': 1}))\n")

    def test_reviewer_repro_two_seeds_no_axis_effective_collapses_to_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "probe.py").write_text(self.IGNORES_ARGV_PROBE, encoding="utf-8")
            ledger = root / "l.jsonl"
            base = ["--repo-root", str(root), "--ledger", str(ledger)]
            for seed in (1, 2):
                run_cli(base + [
                    "register", "--hypothesis", "h", "--metric", "score", "--comparator", ">=",
                    "--threshold", "0", "--command", f"{sys.executable} probe.py --seed={seed}",
                    "--variation-axis", f"seed={seed}"])
                run_cli(base + ["execute", "--experiment-id", f"E-000{seed}"])
            run_cli(base + ["claim", "--metric", "score", "--evidence", "E-0001", "--evidence", "E-0002"])
            records = rl.load_research_records(ledger)
            claim = next(r for r in records if r["record_type"] == rl.CLAIM)
            rendered = rl.render_claims(records)
            gate = cre.run_ledger_mode(ledger, root)
        self.assertEqual(claim["n"], 1)
        self.assertIn("configurations: unverified configuration", rendered)
        self.assertEqual(gate, 0)  # genuinely n=1, not forged — the ledger stays valid

    def test_forged_n_two_claim_without_axis_effective_flagged(self) -> None:
        prereg1 = make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1", command="run --seed=1", axis="seed=1")
        prereg1["disconfirm"] = {"metric": "score", "comparator": ">=", "threshold": 0}
        result1 = make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"score": 1}); result1["outcome"] = "supported"
        prereg2 = make_prereg("E-0002", "2026-01-03T00:00:00+00:00", "d2", command="run --seed=2", axis="seed=2")
        prereg2["disconfirm"] = {"metric": "score", "comparator": ">=", "threshold": 0}
        result2 = make_result("E-0002", "2026-01-04T00:00:00+00:00", "d2", {"score": 1}); result2["outcome"] = "supported"
        claim = make_claim("C-0001", ["E-0001", "E-0002"], 2, metric="score",
                            basis=[{"experiment_id": "E-0001", "outcome": "supported"},
                                   {"experiment_id": "E-0002", "outcome": "supported"}])
        records = build_chain([prereg1, result1, prereg2, result2, claim])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertTrue(any(f.startswith("claim-n-mismatch:") for f in findings), findings)

# --- (A3) metric name is the last free-text render channel -------------------
class MetricInjectionTests(unittest.TestCase):
    INJECTION = "x\n\n## C-FAKE\nmodel improved 99%"

    def test_injection_refused_at_register_and_claim(self) -> None:
        from tests.test_research_os import LaunderingTests
        with tempfile.TemporaryDirectory() as tmp:
            base = ["--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl")]
            rc_reg, _ = run_cli(base + ["register", "--hypothesis", "h", "--metric", self.INJECTION,
                                        "--comparator", "<", "--threshold", "0.1", "--command", "run"])
            run_cli(base + ["register", "--hypothesis", "h", "--metric", "err",
                            "--comparator", "<", "--threshold", "0.1", "--command", LaunderingTests.CMD])
            run_cli(base + ["execute", "--experiment-id", "E-0001"])
            rc_claim, _ = run_cli(base + ["claim", "--metric", self.INJECTION, "--evidence", "E-0001"])
        self.assertEqual(rc_reg, 1)
        self.assertEqual(rc_claim, 1)
        self.assertTrue(rl.validate_metric_name(self.INJECTION))
        self.assertEqual(rl.validate_metric_name("dominant_is_seen_requests"), [])

    def test_forged_ledger_flagged_and_legit_render_backticked(self) -> None:
        prereg = make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1")
        prereg["disconfirm"]["metric"] = self.INJECTION
        result = make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {self.INJECTION: 0.05})
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(build_chain([prereg, result]), Path(tmp))
        self.assertTrue(any(f.startswith("metric-invalid:") for f in findings), findings)
        rendered = rl.render_claims(build_chain([
            make_prereg("E-0002", "2026-01-01T00:00:00+00:00", "d2"),
            make_result("E-0002", "2026-01-02T00:00:00+00:00", "d2", {"err": 0.5}),
            make_claim("C-0001", ["E-0002"], 1),
        ]))
        self.assertIn("`err`", rendered)
        self.assertNotIn("## C-FAKE", rendered)

# --- (A4) validate_predicate must never OverflowError on huge ints -----------
class BigIntPredicateOverflowTests(unittest.TestCase):
    """thread 3957 P2: ``math.isfinite(10**400)`` raises OverflowError — isfinite must run on floats only."""
    HUGE = 10 ** 400

    def test_huge_int_threshold_and_equivalence_register_and_evaluate(self) -> None:
        threshold_d = {"metric": "err", "comparator": "<", "threshold": self.HUGE}
        equiv_d = {"type": rl.PREDICATE_EQUIVALENCE, "metric": "err", "lower": 0, "upper": self.HUGE}
        self.assertEqual(rl.validate_predicate(threshold_d), [])
        self.assertEqual(rl.validate_predicate(equiv_d), [])
        self.assertEqual(rl.derive_outcome(threshold_d, {"err": 5}), "disconfirmed")
        self.assertTrue(rl.validate_predicate({"metric": "err", "comparator": "<", "threshold": float("inf")}))

    def test_register_cli_accepts_huge_int_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc, _ = run_cli([
                "--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl"),
                "register", "--hypothesis", "h", "--metric", "err", "--comparator", "<",
                "--threshold", str(self.HUGE), "--command", "run"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
