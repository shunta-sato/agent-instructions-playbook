"""Ledger-chain integrity tests for the Research OS.

Covers ``check_research_evidence.check_ledger`` / ``run_ledger_mode`` and
``research_ledger`` predicate/render helpers: HARKing, chain tampering,
predicate evaluation, claims-view rendering/staleness, empty-ledger,
untracked-probe digest participation, per-ledger claims-view freshness, and
non-numeric metrics. Runner/claim/promotion-boundary tests live in the
sibling ``test_research_os.py`` and ``test_research_os_gate.py``.

Builders (``build_chain``, ``make_prereg``, ``make_result``, ``make_claim``,
``write_ledger``, ``run_cli``, ``DISCONFIRM``, ``_git_init``) are shared from
``test_research_os`` rather than duplicated, since they live there as the
home for the claim/runner tests.
"""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import check_research_evidence as cre
from scripts import research_ledger as rl
from tests.test_research_os import (
    DISCONFIRM,
    LaunderingTests,
    _git_init,
    build_chain,
    make_claim,
    make_prereg,
    make_result,
    run_cli,
    write_ledger,
)


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


# --- (F2) self-invalidating command digest -----------------------------------


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
        # err=0.5 does not trip err<0.1, so the outcome is "supported", which
        # is consistent with a direction=improves claim under S3 binding.
        return build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.5}),
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


# --- (C1) untracked probe participates in the digest -------------------------


class UntrackedProbeDigestTests(unittest.TestCase):
    def test_untracked_probe_in_digest_and_edit_refuses_execute(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "seed.txt").write_text("seed\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, capture_output=True)
            subprocess.run(
                ["git", "-C", str(root), "commit", "-qm", "seed"], check=True, capture_output=True
            )
            ledger = root / rl.LEDGER_REL
            # An un-added (untracked, non-ignored) probe file — the normal case.
            probe = root / "probe.py"
            probe.write_text("v1\n", encoding="utf-8")

            base = ["--repo-root", str(root), "--ledger", str(ledger)]
            rc_reg, _ = run_cli(base + [
                "register", "--hypothesis", "h", "--metric", "err",
                "--comparator", "<", "--threshold", "0.1", "--command", LaunderingTests.CMD,
            ])
            self.assertEqual(rc_reg, 0)
            records = rl.load_research_records(ledger)
            prereg = rl.find_preregister(records, "E-0001")
            self.assertIn(
                "probe.py", [e["path"] for e in prereg["dirty_files"]],
                "untracked probe must participate in command_digest",
            )
            # Editing the probe between register and execute must be detected.
            probe.write_text("v2-tampered\n", encoding="utf-8")
            rc_exec, _ = run_cli(base + ["execute", "--experiment-id", "E-0001"])
            self.assertEqual(rc_exec, 1)


# --- (C2) per-ledger claims-view freshness -----------------------------------


class AltLedgerClaimsViewTests(unittest.TestCase):
    def _records(self) -> list[dict]:
        return build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.5}),
            make_claim("C-0001", ["E-0001"], 1),
        ])

    def test_adjacent_matching_view_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "alt" / "ledger.jsonl"
            ledger.parent.mkdir(parents=True)
            write_ledger(ledger, self._records())
            (ledger.parent / "claims.md").write_text(
                rl.render_claims(rl.load_research_records(ledger)), encoding="utf-8"
            )
            self.assertEqual(cre.run_ledger_mode(ledger, root), 0)

    def test_stale_adjacent_view_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "alt" / "ledger.jsonl"
            ledger.parent.mkdir(parents=True)
            write_ledger(ledger, self._records())
            (ledger.parent / "claims.md").write_text("stale\n", encoding="utf-8")
            findings = cre.check_ledger(rl.load_research_records(ledger), root, ledger)
        self.assertTrue(any(f.startswith("stale-claims-view:") for f in findings), findings)

    def test_canonical_view_unaffected_by_alt_ledger(self) -> None:
        # An alt ledger must not be judged against research/claims.md.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "research").mkdir()
            (root / "research" / "claims.md").write_text("unrelated\n", encoding="utf-8")
            ledger = root / "alt" / "ledger.jsonl"
            ledger.parent.mkdir(parents=True)
            write_ledger(ledger, self._records())
            self.assertEqual(cre.run_ledger_mode(ledger, root), 0)


# --- (C3) non-numeric metric under an ordered comparator ---------------------


class NonNumericMetricTests(unittest.TestCase):
    ORDERED = {"metric": "err", "comparator": "<", "threshold": 0.1}

    def test_runner_path_not_evaluable_not_crash(self) -> None:
        self.assertEqual(rl.derive_outcome(self.ORDERED, {"err": "low"}), "not-evaluable")

    def test_checker_path_not_evaluable_not_crash(self) -> None:
        records = build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": "low"}),
        ])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertFalse(any(f.startswith("outcome-mismatch:") for f in findings), findings)


if __name__ == "__main__":
    unittest.main()
