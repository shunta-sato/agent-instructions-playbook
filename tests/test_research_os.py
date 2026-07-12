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
                "--repo-root", tmp, "--ledger", str(ledger), "claim",
                "--effect", "x", "--direction", "improves", "--metric", "err",
                "--configuration", "c", "--evidence", "E-9999",
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
                # comparator ">" keeps err=0.05 from tripping the predicate, so
                # both outcomes are "supported"; the preregistered improves
                # direction (F2) makes a direction=improves claim valid while
                # still exercising n-collapse.
                run_cli(base + [
                    "register", "--hypothesis", "h", "--metric", "err",
                    "--comparator", ">", "--threshold", "0.1", "--command", self.CMD,
                    "--direction-if-supported", "improves",
                ])
            run_cli(base + ["execute", "--experiment-id", "E-0001"])
            run_cli(base + ["execute", "--experiment-id", "E-0002"])
            rc, out = run_cli(base + [
                "claim", "--effect", "faster", "--direction", "improves",
                "--metric", "err", "--configuration", "seed=42",
                "--evidence", "E-0001", "--evidence", "E-0002",
            ])
            records = rl.load_research_records(ledger)
            claim = next(r for r in records if r["record_type"] == rl.CLAIM)
            gate = cre.run_ledger_mode(ledger, Path(tmp))
        self.assertEqual(rc, 0)
        self.assertEqual(claim["n"], 1)
        self.assertEqual(gate, 0)


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

    def _claim(self, base, metric, direction):
        return run_cli(base + [
            "claim", "--effect", "x", "--direction", direction, "--metric", metric,
            "--configuration", "c", "--evidence", "E-0001",
        ])

    def test_metric_mismatch_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = ["--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl")]
            self._register_execute(base, "err", ">")  # err=0.05 !> 0.1 → supported
            rc, _ = self._claim(base, "latency", "improves")
        self.assertEqual(rc, 1)

    def test_not_evaluable_evidence_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = ["--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl")]
            self._register_execute(base, "ghost", "<")  # ghost absent → not-evaluable
            rc, _ = self._claim(base, "ghost", "mixed")
        self.assertEqual(rc, 1)

    def test_improves_with_disconfirmed_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = ["--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl")]
            self._register_execute(base, "err", "<")  # err=0.05 < 0.1 → disconfirmed
            rc, _ = self._claim(base, "err", "improves")
        self.assertEqual(rc, 1)

    def test_checker_catches_forged_inconsistent_claim(self) -> None:
        # Result outcome is disconfirmed, but the forged claim asserts
        # improves and stores a fabricated supported basis.
        records = build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.05}),
            make_claim(
                "C-0001", ["E-0001"], 1, direction="improves",
                basis=[{"experiment_id": "E-0001", "outcome": "supported"}],
            ),
        ])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertTrue(any(f.startswith("claim-binding:") for f in findings), findings)
        self.assertTrue(any(f.startswith("claim-basis-mismatch:") for f in findings), findings)


# --- (S4) conservative claim n from variation axes ---------------------------


class ClaimNTests(unittest.TestCase):
    def _pair(self, eid, digest, axis=""):
        return [
            make_prereg(eid, "2026-01-01T00:00:00+00:00", digest, axis=axis),
            make_result(eid, "2026-01-02T00:00:00+00:00", digest, {"err": 0.5}),
        ]

    def test_distinct_digests_without_axis_collapse_to_one(self) -> None:
        records = self._pair("E-0001", "d1") + self._pair("E-0002", "d2")
        self.assertEqual(rl.claim_n(records, ["E-0001", "E-0002"]), 1)

    def test_distinct_declared_axes_count_two(self) -> None:
        records = self._pair("E-0001", "d1", "seed=1") + self._pair("E-0002", "d2", "seed=2")
        self.assertEqual(rl.claim_n(records, ["E-0001", "E-0002"]), 2)

    def test_duplicate_axis_values_collapse(self) -> None:
        records = self._pair("E-0001", "d1", "seed=1") + self._pair("E-0002", "d2", "seed=1")
        self.assertEqual(rl.claim_n(records, ["E-0001", "E-0002"]), 1)

    def test_mixed_axis_keys_collapse_to_one(self) -> None:
        # Different knobs (seed vs batch) are not comparable configurations.
        records = self._pair("E-0001", "d1", "seed=1") + self._pair("E-0002", "d2", "batch=2")
        n, note = rl.claim_n_and_note(records, ["E-0001", "E-0002"])
        self.assertEqual(n, 1)
        self.assertIn("mixes axis keys", note)


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


if __name__ == "__main__":
    unittest.main()
