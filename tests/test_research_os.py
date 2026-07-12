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


def make_prereg(eid: str, registered_at: str, digest: str, command: str = "run") -> dict:
    return {
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


def make_claim(cid: str, evidence: list[str], n: int) -> dict:
    return {
        "schema_version": 1,
        "record_type": rl.CLAIM,
        "claim_id": cid,
        "created_at": "2026-01-03T00:00:00+00:00",
        "effect": "faster",
        "direction": "improves",
        "metric": "err",
        "configurations": ["seed=42"],
        "evidence": evidence,
        "sources": [],
        "n": n,
    }


def write_ledger(path: Path, records: list[dict]) -> None:
    for record in records:
        rl.append_jsonl(path, record)


def run_cli(argv: list[str]) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = research_run.main(argv)
    return rc, out.getvalue()


# --- (B) HARKing + missing preregistration -----------------------------------


class HarkingTests(unittest.TestCase):
    def test_result_registered_after_started_fails(self) -> None:
        records = build_chain([
            make_prereg("E-0001", "2026-01-02T00:00:00+00:00", "d1"),
            make_result("E-0001", "2026-01-01T00:00:00+00:00", "d1", {"err": 0.05}),
        ])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertTrue(any(f.startswith("harking:") for f in findings), findings)

    def test_result_without_preregistration_fails(self) -> None:
        records = build_chain([
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.05}),
        ])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertTrue(any(f.startswith("missing-preregistration:") for f in findings), findings)


# --- (B2) chain tampering ----------------------------------------------------


class ChainTamperTests(unittest.TestCase):
    def test_mutating_middle_record_breaks_chain(self) -> None:
        records = build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1"),
            make_prereg("E-0002", "2026-01-02T00:00:00+00:00", "d2"),
            make_prereg("E-0003", "2026-01-03T00:00:00+00:00", "d3"),
        ])
        records[1]["hypothesis"] = "tampered"  # stored chain.hash now stale
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertTrue(any(f.startswith("chain-hash-mismatch:") for f in findings), findings)


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


# --- (D) promotion boundary --------------------------------------------------


class PromotionTests(unittest.TestCase):
    POLICY = {"path_modes": {"experiments/": "research"}, "safety_paths": []}

    def test_unmatched_path_under_research_declaration_requires_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.evaluate_diff(
                ["experiments/e1/run.py", "src/app.py"], Path(tmp), self.POLICY
            )
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertNotIn("promotion-required: experiments/e1/run.py", findings)

    def test_research_only_diff_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.evaluate_diff(["experiments/e1/run.py"], Path(tmp), self.POLICY)
        self.assertEqual(findings, [])


# --- (E) safety orthogonality ------------------------------------------------


class SafetyTests(unittest.TestCase):
    def test_safety_path_flagged_in_delivery_mode(self) -> None:
        policy = {"path_modes": {}, "safety_paths": ["SECURITY/"]}
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.evaluate_diff(["SECURITY/policy.md"], Path(tmp), policy)
        self.assertIn("safety-review-required: SECURITY/policy.md", findings)

    def test_safety_path_flagged_in_research_mode(self) -> None:
        policy = {"path_modes": {"SECURITY/": "research"}, "safety_paths": ["SECURITY/"]}
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.evaluate_diff(["SECURITY/keys.md"], Path(tmp), policy)
        self.assertIn("safety-review-required: SECURITY/keys.md", findings)

    def test_symlink_crossing_boundary_flagged(self) -> None:
        policy = {"path_modes": {"experiments/": "research", "src/": "delivery"}, "safety_paths": []}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            (root / "src" / "real.py").write_text("x\n", encoding="utf-8")
            (root / "experiments").mkdir()
            link = root / "experiments" / "link.py"
            link.symlink_to(root / "src" / "real.py")
            findings = cre.evaluate_diff(["experiments/link.py"], root, policy)
        self.assertIn("symlink-boundary: experiments/link.py", findings)


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
                run_cli(base + [
                    "register", "--hypothesis", "h", "--metric", "err",
                    "--comparator", "<", "--threshold", "0.1", "--command", self.CMD,
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


# --- (F2) self-invalidating command digest -----------------------------------


def _git_init(root: Path) -> None:
    for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


class SelfInvalidatingDigestTests(unittest.TestCase):
    """Regression: a tracked, dirty ledger must not invalidate its own digest.

    ``register`` appends to the ledger, so before the exclusion the ledger was
    a dirty tracked file whose sha256 fed ``command_digest``. ``execute`` then
    recomputed the digest over the now-larger ledger and rejected the pair with
    "command_digest ... changed since registration". The recording medium (and
    ``research/runs/`` outputs) are excluded so the digest fingerprints only
    experiment inputs.
    """

    def test_register_then_execute_succeeds_with_tracked_dirty_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            ledger = root / rl.LEDGER_REL
            ledger.parent.mkdir(parents=True, exist_ok=True)
            ledger.write_text("", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, capture_output=True)
            subprocess.run(
                ["git", "-C", str(root), "commit", "-qm", "seed"], check=True, capture_output=True
            )

            base = ["--repo-root", str(root), "--ledger", str(ledger)]
            rc_reg, _ = run_cli(base + [
                "register", "--hypothesis", "h", "--metric", "err",
                "--comparator", "<", "--threshold", "0.1", "--command", LaunderingTests.CMD,
            ])
            self.assertEqual(rc_reg, 0)
            # register appended to the tracked ledger, so it is now dirty vs HEAD.
            self.assertIn(
                rl.LEDGER_REL,
                subprocess.run(
                    ["git", "-C", str(root), "diff", "--name-only", "HEAD"],
                    check=True, capture_output=True, text=True,
                ).stdout,
            )
            rc_exec, _ = run_cli(base + ["execute", "--experiment-id", "E-0001"])
            self.assertEqual(rc_exec, 0)

            records = rl.load_research_records(ledger)
            prereg = rl.find_preregister(records, "E-0001")
            result = rl.find_result(records, "E-0001")
            self.assertEqual(result["command_digest"], prereg["command_digest"])
            self.assertEqual(cre.run_ledger_mode(ledger, root), 0)


# --- predicate evaluation ----------------------------------------------------


class PredicateTests(unittest.TestCase):
    def test_disconfirmed(self) -> None:
        self.assertEqual(rl.derive_outcome(DISCONFIRM, {"err": 0.05}), "disconfirmed")

    def test_supported(self) -> None:
        self.assertEqual(rl.derive_outcome(DISCONFIRM, {"err": 0.5}), "supported")

    def test_not_evaluable_missing_metric(self) -> None:
        self.assertEqual(rl.derive_outcome(DISCONFIRM, {"other": 1}), "not-evaluable")

    def test_not_evaluable_null_metrics(self) -> None:
        self.assertEqual(rl.derive_outcome(DISCONFIRM, None), "not-evaluable")

    def test_malformed_predicate_reported(self) -> None:
        self.assertTrue(rl.validate_predicate({"metric": "e", "comparator": "~", "threshold": 1}))


# --- render-claims determinism + staleness -----------------------------------


class RenderTests(unittest.TestCase):
    def _seed(self) -> list[dict]:
        return build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.05}),
            make_claim("C-0001", ["E-0001"], 1),
        ])

    def test_render_is_deterministic_without_timestamps(self) -> None:
        records = self._seed()
        first = rl.render_claims(records)
        second = rl.render_claims(records)
        self.assertEqual(first, second)
        self.assertIn("ledger-head:", first)
        self.assertIn("Observed once under configuration seed=42", first)

    def test_fresh_view_passes_and_stale_view_fails(self) -> None:
        records = self._seed()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "ledger.jsonl"
            write_ledger(ledger, records)
            (root / "research").mkdir()
            (root / "research" / "claims.md").write_text(
                rl.render_claims(records), encoding="utf-8"
            )
            self.assertEqual(cre.run_ledger_mode(ledger, root), 0)

            extra = dict(make_prereg("E-0002", "2026-01-05T00:00:00+00:00", "d2"))
            extra["chain"] = {"prev": records[-1]["chain"]["hash"]}
            extra["chain"]["hash"] = rl.compute_hash(extra)
            rl.append_jsonl(ledger, extra)
            findings = cre.check_ledger(rl.load_research_records(ledger), root)
        self.assertTrue(any(f.startswith("stale-claims-view:") for f in findings), findings)


# --- empty ledger ------------------------------------------------------------


class EmptyLedgerTests(unittest.TestCase):
    def test_empty_ledger_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "ledger.jsonl"
            self.assertEqual(cre.run_ledger_mode(ledger, Path(tmp)), 0)


# --- wiring: the chain, not just the script ----------------------------------


class WiringTests(unittest.TestCase):
    def test_makefile_lint_target_invokes_check(self) -> None:
        makefile = Path(__file__).resolve().parent.parent / "Makefile"
        text = makefile.read_text(encoding="utf-8")
        lint_block = text.split("\nlint:", 1)[1].split("\nanalysis:", 1)[0]
        self.assertIn("check_research_evidence.py --check-ledger", lint_block)


if __name__ == "__main__":
    unittest.main()
