from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import check_research_evidence as cre
from scripts import research_ledger as rl
from scripts import research_run

DISCONFIRM = {"metric": "err", "comparator": "<", "threshold": 0.1}

# --- builders ----------------------------------------------------------------
def build_chain(records_data: list[dict]) -> list[dict]:
    """Attach a valid research hash chain over a list of record bodies."""
    out: list[dict] = []
    prev = None
    for data in records_data:
        record = json.loads(json.dumps(data))  # deep copy
        record["chain"] = {"prev": prev}
        record["chain"]["hash"] = rl.compute_hash(record)
        prev = record["chain"]["hash"]
        out.append(record)
    return out


def make_prereg(
    eid: str,
    registered_at: str,
    digest: str,
    command: str = "run",
    axis: str = "",
    direction: str = "",
) -> dict:
    record = {
        "schema_version": 1,
        "record_type": rl.PREREGISTER,
        "experiment_id": eid,
        "registered_at": registered_at,
        "mode": "research",
        "hypothesis": "h",
        "disconfirm": dict(DISCONFIRM),
        "command": command,
        "command_digest": digest,
        "git_head": "no-git",
        "dirty_files": [],
    }
    if axis:
        record["variation_axis"] = axis
    if direction:  # omitted → pre-F2 grandfathered evidence
        record["direction_if_supported"] = direction
    return record


def make_result(eid: str, started_at: str, digest: str, metrics, mult: int = 0) -> dict:
    return {
        "schema_version": 1,
        "record_type": rl.RESULT,
        "experiment_id": eid,
        "started_at": started_at,
        "finished_at": started_at,
        "command_digest": digest,
        "exit_code": 0,
        "metrics": metrics,
        "outcome": rl.derive_outcome(DISCONFIRM, metrics),
        "run_dir": "research/runs/x",
        "exploration_multiplicity": mult,
        "derived_from_exploration": mult > 0,
    }


def make_claim(
    cid: str,
    evidence: list[str],
    n: int,
    direction: str = "improves",
    metric: str = "err",
    basis: list[dict] | None = None,
    direction_basis: list[dict] | None = None,
) -> dict:
    record = {
        "schema_version": 1,
        "record_type": rl.CLAIM,
        "claim_id": cid,
        "created_at": "2026-01-03T00:00:00+00:00",
        "effect": "faster",
        "direction": direction,
        "metric": metric,
        "configurations": ["seed=42"],
        "evidence": evidence,
        "sources": [],
        "n": n,
    }
    if basis is not None:  # omitted → a grandfathered pre-S3 claim record
        record["outcome_basis"] = basis
    if direction_basis is not None:  # present → a post-F2 claim (enforce direction)
        record["direction_basis"] = direction_basis
    return record


def write_ledger(path: Path, records: list[dict]) -> None:
    for record in records:
        rl.append_jsonl(path, record)


def run_cli(argv: list[str]) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = research_run.main(argv)
    return rc, out.getvalue()

# --- (C) claim citing nonexistent / incomplete experiment --------------------
class ClaimIntegrityTests(unittest.TestCase):
    def test_claim_subcommand_refuses_unknown_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            rc, _ = run_cli([
                "--repo-root", tmp, "--ledger", str(ledger), "claim", "--metric", "err",
                "--evidence", "E-9999",
            ])
        self.assertEqual(rc, 1)

    def test_forged_claim_record_fails_check(self) -> None:
        records = build_chain([make_claim("C-0001", ["E-9999"], 1)])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertTrue(any(f.startswith("claim-evidence-invalid:") for f in findings), findings)

# --- (F) laundering ----------------------------------------------------------
class LaunderingTests(unittest.TestCase):
    CMD = (
        sys.executable
        + " -c \"import json,os; open(os.path.join(os.environ['RESEARCH_RUN_DIR'],"
        + "'result.json'),'w').write(json.dumps({'err':0.05}))\""
    )

    def test_exploration_multiplicity_and_derived_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            run_cli(base + ["explore", "--command", self.CMD])
            run_cli(base + ["explore", "--command", self.CMD])
            run_cli(base + [
                "register", "--hypothesis", "h", "--metric", "err",
                "--comparator", "<", "--threshold", "0.1", "--command", self.CMD,
            ])
            run_cli(base + ["execute", "--experiment-id", "E-0001"])
            records = rl.load_research_records(ledger)
            result = rl.find_result(records, "E-0001")
        self.assertEqual(result["exploration_multiplicity"], 2)
        self.assertTrue(result["derived_from_exploration"])

    def test_byte_identical_evidence_collapses_to_n_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            for _ in range(2):
                # comparator ">" keeps err=0.05 "supported"; byte-identical registrations exercise
                # the n-collapse regardless of claim category.
                run_cli(base + [
                    "register", "--hypothesis", "h", "--metric", "err",
                    "--comparator", ">", "--threshold", "0.1", "--command", self.CMD,
                ])
            run_cli(base + ["execute", "--experiment-id", "E-0001"])
            run_cli(base + ["execute", "--experiment-id", "E-0002"])
            rc, out = run_cli(base + [
                "claim", "--metric", "err",
                "--evidence", "E-0001", "--evidence", "E-0002",
            ])
            records = rl.load_research_records(ledger)
            claim = next(r for r in records if r["record_type"] == rl.CLAIM)
            gate = cre.run_ledger_mode(ledger, Path(tmp))
        self.assertEqual(rc, 0)
        self.assertEqual(claim["n"], 1)
        self.assertEqual(gate, 0)

    # B2: a paren-free command runs via shell=False + shlex.split; parens live in the probe below.
    # Also emits a matching axis_effective (B4): proves a matching value counts normally.
    SEED_PROBE = ("import sys, os, json\nv = int(sys.argv[1].split('=')[1])\n"
                  "open(os.environ['RESEARCH_RUN_DIR'] + '/result.json', 'w')."
                  "write(json.dumps({'seed': v, 'axis_effective': v}))\n")

    def test_genuine_seed_pair_yields_n_two_via_true_argv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "probe.py").write_text(self.SEED_PROBE, encoding="utf-8")
            ledger = root / "ledger.jsonl"
            base = ["--repo-root", str(root), "--ledger", str(ledger)]
            for seed in (1, 2):
                run_cli(base + [
                    "register", "--hypothesis", "h", "--metric", "seed", "--comparator", ">=",
                    "--threshold", "0", "--command", f"{sys.executable} probe.py --seed={seed}",
                    "--variation-axis", f"seed={seed}"])
                run_cli(base + ["execute", "--experiment-id", f"E-000{seed}"])
            records = rl.load_research_records(ledger)
            metrics = [rl.find_result(records, f"E-000{s}")["metrics"] for s in (1, 2)]
        self.assertEqual(metrics, [{"seed": 1, "axis_effective": 1}, {"seed": 2, "axis_effective": 2}])
        self.assertEqual(rl.claim_n(records, ["E-0001", "E-0002"]), 2)

    def test_axis_less_compound_command_still_registers_and_executes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            run_cli(base + ["register", "--hypothesis", "h", "--metric", "err", "--comparator", "<",
                            "--threshold", "0.1", "--command", self.CMD + " && echo done"])
            rc, _ = run_cli(base + ["execute", "--experiment-id", "E-0001"])
        self.assertEqual(rc, 0)

# --- shared git helper (also imported by test_research_os_ledger) -----------
def _git_init(root: Path) -> None:
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)

# --- (S3) semantic claim binding ---------------------------------------------
class ClaimBindingTests(unittest.TestCase):
    def _register_execute(self, base, metric, comparator) -> None:
        run_cli(base + [
            "register", "--hypothesis", "h", "--metric", metric,
            "--comparator", comparator, "--threshold", "0.1", "--command", LaunderingTests.CMD,
        ])
        run_cli(base + ["execute", "--experiment-id", "E-0001"])

    def _claim(self, base, metric):
        return run_cli(base + ["claim", "--metric", metric, "--evidence", "E-0001"])

    def test_metric_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = ["--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl")]
            self._register_execute(base, "err", ">")  # err=0.05 !> 0.1 → supported
            rc, _ = self._claim(base, "latency")
        self.assertEqual(rc, 1)

    def test_not_evaluable_evidence_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = ["--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl")]
            self._register_execute(base, "ghost", "<")  # ghost absent → not-evaluable
            rc, _ = self._claim(base, "ghost")
        self.assertEqual(rc, 1)

    def test_disconfirmed_evidence_now_accepted_as_disconfirmed(self) -> None:
        # B1/B5: no caller-supplied direction to reject against disconfirmed evidence —
        # the claim is accepted and machine-derives category "disconfirmed" (all-disconfirmed).
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "l.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            self._register_execute(base, "err", "<")  # err=0.05 < 0.1 → disconfirmed
            rc, _ = self._claim(base, "err")
            self.assertEqual(rc, 0)
            claim = next(r for r in rl.load_research_records(ledger) if r["record_type"] == rl.CLAIM)
        self.assertEqual(claim["derived_category"], rl.CATEGORY_DISCONFIRMED)

    def test_checker_catches_forged_basis(self) -> None:
        # Result is disconfirmed, but the forged claim's outcome_basis fabricates "supported".
        records = build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.05}),
            make_claim("C-0001", ["E-0001"], 1, basis=[{"experiment_id": "E-0001", "outcome": "supported"}]),
        ])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertTrue(any(f.startswith("claim-basis-mismatch:") for f in findings), findings)

# --- (S4) conservative claim n from variation axes ---------------------------
class ClaimNTests(unittest.TestCase):
    def _pair(self, eid, digest, axis="", command="run"):
        return [
            make_prereg(eid, "2026-01-01T00:00:00+00:00", digest, command=command, axis=axis),
            make_result(eid, "2026-01-02T00:00:00+00:00", digest, {"err": 0.5}),
        ]

    def test_distinct_digests_without_axis_collapse_to_one(self) -> None:
        records = self._pair("E-0001", "d1") + self._pair("E-0002", "d2")
        self.assertEqual(rl.claim_n(records, ["E-0001", "E-0002"]), 1)

    def test_true_seed_variation_counts_two(self) -> None:
        # R3: commands identical except the seed token → one template, distinct values → n=2.
        records = (self._pair("E-0001", "d1", "seed=1", "run --seed=1")
                   + self._pair("E-0002", "d2", "seed=2", "run --seed=2"))
        self.assertEqual(rl.claim_n(records, ["E-0001", "E-0002"]), 2)

    def test_reviewer_counterexample_non_axis_diff_collapses_to_one(self) -> None:
        # R3: axes seed=1/seed=2 but commands ALSO differ at a non-axis position → collapse to n=1.
        records = (self._pair("E-0001", "d1", "seed=1", "run --seed=1 --output run1.json")
                   + self._pair("E-0002", "d2", "seed=2", "run --seed=2 --output run2.json"))
        n, note = rl.claim_n_and_note(records, ["E-0001", "E-0002"])
        self.assertEqual(n, 1)
        self.assertIn("non-axis position", note)

    def test_duplicate_axis_values_collapse(self) -> None:
        # Same value AND same raw command → not pairwise distinct → n=1.
        records = (self._pair("E-0001", "d1", "seed=1", "run --seed=1")
                   + self._pair("E-0002", "d2", "seed=1", "run --seed=1"))
        self.assertEqual(rl.claim_n(records, ["E-0001", "E-0002"]), 1)

    def test_whitespace_and_quoting_variant_same_value_collapses_to_one(self) -> None:
        # (a): raw-command noise (extra space / quoting) must not inflate n — only
        # distinct AXIS VALUES count, regardless of raw-command differences.
        records = (self._pair("E-0001", "d1", "seed=1", "python p.py --seed=1")
                   + self._pair("E-0002", "d2", "seed=1", "python  p.py --seed='1'"))
        self.assertEqual(rl.claim_n(records, ["E-0001", "E-0002"]), 1)

    def test_mixed_axis_keys_collapse_to_one(self) -> None:
        # Different knobs (seed vs batch) are not comparable configurations.
        records = (self._pair("E-0001", "d1", "seed=1", "run --seed=1")
                   + self._pair("E-0002", "d2", "batch=2", "run --batch=2"))
        n, note = rl.claim_n_and_note(records, ["E-0001", "E-0002"])
        self.assertEqual(n, 1)
        self.assertIn("mixes axis keys", note)

    def test_forged_axis_value_under_other_option_collapses_to_one(self) -> None:
        # Q2 reviewer bypass, hand-forged: axes seed=1/seed=2 are bound to --output, not --seed.
        records = (self._pair("E-0001", "d1", "seed=1", "python p.py --seed=0 --output=1")
                   + self._pair("E-0002", "d2", "seed=2", "python p.py --seed=0 --output=2"))
        n, note = rl.claim_n_and_note(records, ["E-0001", "E-0002"])
        self.assertEqual(n, 1)
        self.assertIn("non-axis position", note)

# --- (F3) register-time variation_axis verification --------------------------
class RegisterAxisTests(unittest.TestCase):
    def _register(self, tmp: str, axis: str, command: str) -> tuple[int, str]:
        return run_cli([
            "--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl"),
            "register", "--hypothesis", "h", "--metric", "err",
            "--comparator", "<", "--threshold", "0.1", "--command", command,
            "--variation-axis", axis,
        ])

    def test_non_conforming_axis_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc, _ = self._register(tmp, "no-equals-sign", "run --seed 7")
        self.assertEqual(rc, 1)

    def test_axis_value_absent_from_command_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc, _ = self._register(tmp, "seed=42", "run --seed 7")
        self.assertEqual(rc, 1)

    def test_conforming_axis_present_in_command_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            rc, _ = self._register(tmp, "seed=7", "run --seed=7")
        self.assertEqual(rc, 0)

    def test_short_value_accidental_substring_refused(self) -> None:
        # R3: "7" is a substring of token "77" but not a whole token, so it is not accepted.
        with tempfile.TemporaryDirectory() as tmp:
            rc, _ = self._register(tmp, "seed=7", "run --seed 77")
        self.assertEqual(rc, 1)

    def test_bare_argv_token_value_accepted(self) -> None:
        # R3: the value as its own argv token also qualifies.
        with tempfile.TemporaryDirectory() as tmp:
            rc, _ = self._register(tmp, "seed=7", "run --seed 7")
        self.assertEqual(rc, 0)

    def test_value_bound_to_other_option_refused(self) -> None:
        # Q2 reviewer bypass: axis seed=1/seed=2 whose value 1/2 is bound to --output, not --seed.
        for axis, command in (("seed=1", "python p.py --seed=0 --output=1"),
                              ("seed=2", "python p.py --seed=0 --output=2")):
            with tempfile.TemporaryDirectory() as tmp:
                rc, _ = self._register(tmp, axis, command)
            self.assertEqual(rc, 1, (axis, command))

    def test_true_seed_binding_accepted(self) -> None:  # the genuine variation the bypass imitates
        with tempfile.TemporaryDirectory() as tmp:
            rc, _ = self._register(tmp, "seed=1", "python p.py --seed=1 --output=out")
        self.assertEqual(rc, 0)

    def test_shell_metacharacter_bypass_refused(self) -> None:
        # B2: an axis value bound only inside a shell-metacharacter tail (a real separate command).
        for axis, command in (("seed=1", "python p.py --seed=0; echo --seed=1"),
                              ("seed=2", "python p.py --seed=0; echo --seed=2")):
            with tempfile.TemporaryDirectory() as tmp:
                rc, _ = self._register(tmp, axis, command)
            self.assertEqual(rc, 1, (axis, command))

    def test_wrapper_and_terminator_bypass_refused(self) -> None:
        # B(b): a shell/interpreter -c/-e wrapper consumes the token as its own arg ($0/script),
        # and a token stranded after a bare '--' terminator is positional — refuse both.
        for axis, command in (
            ("seed=1", "bash -c ./probe --seed=1"),
            ("seed=1", "python3 -c 'pass' --seed=1"),
            ("seed=1", "probe -- --seed=1"),
        ):
            with tempfile.TemporaryDirectory() as tmp:
                rc, _ = self._register(tmp, axis, command)
            self.assertEqual(rc, 1, (axis, command))


if __name__ == "__main__":
    unittest.main()
