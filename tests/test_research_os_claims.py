"""B1 claim-category tests for the Research OS (round-5 finding B1, review comment 3568085567),
plus round-6 thread 3594347694: predicate identity (S5, item1), the ``disconfirmed`` category
(B5, item2), and evidence-derived configuration identity (S6, item3).

Covers the machine-derived claim category: a claim carries no caller-supplied direction;
``derive_claim_category`` derives ``supported``/``within-bounds``/``disconfirmed``/``mixed``
purely from cited-evidence outcomes and predicate shapes; an aggregate claim's citations must
share ONE normalized predicate; the checker re-derives all of this independently (field-presence
grandfathered for pre-B1 records); and ``render_claims`` states only the predicate fact — never
improves/degrades/better/worse/no-effect vocabulary, and never a stored free-text configuration.
Shared builders come from ``test_research_os``; other claim/runner tests live there and in the
sibling ``test_research_os_ledger`` / ``test_research_os_gate``.
"""

from __future__ import annotations

import contextlib
import io
import sys
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
)

FORBIDDEN_VOCABULARY = ("improves", "degrades", "better", "worse", "no-effect")


class ReviewerBypassScenarioTests(unittest.TestCase):
    """The exact round-5 finding B1 bypass: a threshold disconfirm of
    ``latency < 100`` with a measured value of 150 makes the predicate FALSE
    (not disconfirmed), so the outcome is ``supported`` — the metric moved the
    WORSE way. B1: the derived category is a predicate fact (``supported``),
    never a direction, and the rendered sentence carries no improvement word."""

    CMD = (
        sys.executable
        + " -c \"import json,os; open(os.path.join(os.environ['RESEARCH_RUN_DIR'],"
        + "'result.json'),'w').write(json.dumps({'latency':150}))\""
    )

    def test_disconfirm_false_on_worse_value_yields_supported_category(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "l.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            run_cli(base + [
                "register", "--hypothesis", "h", "--metric", "latency",
                "--comparator", "<", "--threshold", "100", "--command", self.CMD,
            ])
            run_cli(base + ["execute", "--experiment-id", "E-0001"])
            result = rl.find_result(rl.load_research_records(ledger), "E-0001")
            self.assertEqual(result["outcome"], "supported")  # sanity: NOT disconfirmed

            rc, _ = run_cli(base + ["claim", "--metric", "latency", "--evidence", "E-0001"])
            self.assertEqual(rc, 0)
            records = rl.load_research_records(ledger)
            claim = next(r for r in records if r["record_type"] == rl.CLAIM)
            self.assertEqual(claim["derived_category"], rl.CATEGORY_SUPPORTED)

            rendered = rl.render_claims(records)
        self.assertIn(
            "latency stayed on the non-disconfirming side of < 100 — observed in a single"
            " configuration.",
            rendered,
        )
        lowered = rendered.lower()
        for word in FORBIDDEN_VOCABULARY:
            self.assertNotIn(word, lowered, rendered)


class ClaimCategoryDerivationTests(unittest.TestCase):
    """The derived-category outcomes, driven purely by evidence outcome
    + predicate shape (never a claim CLI flag)."""

    CMD = LaunderingTests.CMD  # writes err=0.05

    def _claim(self, base: list[str], evidence: list[str]) -> tuple[int, str]:
        args = ["claim", "--metric", "err"]
        for eid in evidence:
            args += ["--evidence", eid]
        return run_cli(base + args)

    def _derived_category(self, ledger: Path) -> str:
        records = rl.load_research_records(ledger)
        claim = next(r for r in records if r["record_type"] == rl.CLAIM)
        return claim["derived_category"]

    def test_equivalence_supported_yields_within_bounds(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "l.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            run_cli(base + ["register", "--hypothesis", "h", "--metric", "err",
                            "--equivalence-bounds", "0.0", "0.1", "--command", self.CMD])
            run_cli(base + ["execute", "--experiment-id", "E-0001"])
            rc, _ = self._claim(base, ["E-0001"])
            self.assertEqual(rc, 0)
            self.assertEqual(self._derived_category(ledger), rl.CATEGORY_WITHIN_BOUNDS)
            rendered = rl.render_claims(rl.load_research_records(ledger))
        self.assertIn(
            "err remained within [0.0, 0.1] — observed in a single configuration.", rendered
        )

    def test_all_disconfirmed_evidence_yields_disconfirmed_category(self) -> None:
        # B5/item2: a single disconfirmed citation is ALL-disconfirmed -> "disconfirmed",
        # never "mixed" (mixed is reserved for a genuine outcome mixture).
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "l.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            run_cli(base + ["register", "--hypothesis", "h", "--metric", "err",
                            "--comparator", "<", "--threshold", "0.1", "--command", self.CMD])
            run_cli(base + ["execute", "--experiment-id", "E-0001"])  # 0.05 < 0.1 → disconfirmed
            rc, _ = self._claim(base, ["E-0001"])
            self.assertEqual(rc, 0)
            self.assertEqual(self._derived_category(ledger), rl.CATEGORY_DISCONFIRMED)
            rendered = rl.render_claims(rl.load_research_records(ledger))
        self.assertIn("err met the disconfirm predicate < 0.1 in the configuration.", rendered)

    def test_mixed_predicate_types_refused_at_claim_time(self) -> None:
        # S5/item1: a threshold citation + an equivalence citation on the same metric no longer
        # aggregate into one claim (predicate identity spans TYPE too) — refused before category
        # derivation is ever reached.
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "l.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            run_cli(base + ["register", "--hypothesis", "h", "--metric", "err",
                            "--comparator", ">", "--threshold", "0.1", "--command", self.CMD])
            run_cli(base + ["execute", "--experiment-id", "E-0001"])
            run_cli(base + ["register", "--hypothesis", "h", "--metric", "err",
                            "--equivalence-bounds", "0.0", "0.1", "--command", self.CMD])
            run_cli(base + ["execute", "--experiment-id", "E-0002"])
            rc, _ = self._claim(base, ["E-0001", "E-0002"])
        self.assertEqual(rc, 1)


class PredicateIdentityTests(unittest.TestCase):
    """S5/item1: an aggregate claim's cited registrations must share ONE normalized predicate —
    the reviewer's exact E1 ``latency < 100`` / E2 ``latency > 200`` bypass (both "supported" on
    the same real 150ms measurement, but on DIFFERENT predicates) is refused at claim time, and a
    hand-forged ledger that skips the CLI is caught by the checker as ``claim-predicate-mismatch``."""

    CMD = ReviewerBypassScenarioTests.CMD  # writes latency=150

    def test_reviewer_e1_e2_pair_refused_at_claim_time(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "l.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            run_cli(base + ["register", "--hypothesis", "h", "--metric", "latency",
                            "--comparator", "<", "--threshold", "100", "--command", self.CMD])
            run_cli(base + ["execute", "--experiment-id", "E-0001"])
            run_cli(base + ["register", "--hypothesis", "h", "--metric", "latency",
                            "--comparator", ">", "--threshold", "200", "--command", self.CMD])
            run_cli(base + ["execute", "--experiment-id", "E-0002"])
            rc, _ = run_cli(base + [
                "claim", "--metric", "latency", "--evidence", "E-0001", "--evidence", "E-0002",
            ])
        self.assertEqual(rc, 1)

    def test_forged_ledger_predicate_mismatch_flagged(self) -> None:
        # Same E1/E2 pair, hand-forged directly into the ledger (bypassing the CLI refusal).
        prereg1 = make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1")
        prereg1["disconfirm"] = {"metric": "latency", "comparator": "<", "threshold": 100}
        result1 = make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"latency": 150})
        result1["outcome"] = "supported"
        prereg2 = make_prereg("E-0002", "2026-01-01T00:00:00+00:00", "d2")
        prereg2["disconfirm"] = {"metric": "latency", "comparator": ">", "threshold": 200}
        result2 = make_result("E-0002", "2026-01-02T00:00:00+00:00", "d2", {"latency": 150})
        result2["outcome"] = "supported"
        claim = make_claim(
            "C-0001", ["E-0001", "E-0002"], 1, metric="latency",
            basis=[{"experiment_id": "E-0001", "outcome": "supported"},
                   {"experiment_id": "E-0002", "outcome": "supported"}],
        )
        records = build_chain([prereg1, result1, prereg2, result2, claim])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertTrue(any(f.startswith("claim-predicate-mismatch:") for f in findings), findings)


class CheckerCatchesForgedCategoryTests(unittest.TestCase):
    def test_hand_forged_derived_category_flagged(self) -> None:
        # Real evidence is supported + threshold (re-derives "supported"), but
        # the hand-forged claim record asserts "within-bounds".
        forged_claim = make_claim(
            "C-0001", ["E-0001"], 1,
            basis=[{"experiment_id": "E-0001", "outcome": "supported"}],
        )
        forged_claim["derived_category"] = rl.CATEGORY_WITHIN_BOUNDS
        records = build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.5}),
            forged_claim,
        ])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertTrue(any(f.startswith("claim-category-mismatch:") for f in findings), findings)

    def test_grandfathered_claim_without_derived_category_skips_the_check(self) -> None:
        # C-0001-style: a pre-B1 record with only a legacy ``direction`` field
        # and no ``derived_category`` — the field-presence check is skipped.
        records = build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.5}),
            make_claim("C-0001", ["E-0001"], 1),
        ])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertEqual(findings, [])


class CLIRejectsDirectionFlagsTests(unittest.TestCase):
    """B1: the caller-supplied direction vocabulary is deleted at the CLI, not
    merely unused — passing it is an argparse usage error (exit 2)."""

    def _expect_usage_error(self, argv: list[str]) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                run_cli(argv)
        self.assertEqual(ctx.exception.code, 2)

    def test_register_rejects_direction_if_supported_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._expect_usage_error([
                "--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl"),
                "register", "--hypothesis", "h", "--metric", "err",
                "--comparator", "<", "--threshold", "0.1", "--command", "run",
                "--direction-if-supported", "improves",
            ])

    def test_claim_rejects_direction_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self._expect_usage_error([
                "--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl"),
                "claim", "--direction", "improves", "--metric", "err", "--evidence", "E-0001",
            ])


class ConfigurationDerivedFromEvidenceTests(unittest.TestCase):
    """S6/item3: ``--configuration`` is deleted from the claim CLI; the rendered
    ``configurations:`` line is derived from evidence, never caller-supplied free text."""

    def test_claim_cli_rejects_configuration_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as ctx:
                    run_cli([
                        "--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl"),
                        "claim", "--metric", "err", "--configuration", "c", "--evidence", "E-0001",
                    ])
            self.assertEqual(ctx.exception.code, 2)

    def test_new_claim_record_stores_no_configurations_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "l.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            run_cli(base + ["register", "--hypothesis", "h", "--metric", "err",
                            "--comparator", "<", "--threshold", "0.1", "--command", LaunderingTests.CMD])
            run_cli(base + ["execute", "--experiment-id", "E-0001"])
            run_cli(base + ["claim", "--metric", "err", "--evidence", "E-0001"])
            claim = next(r for r in rl.load_research_records(ledger) if r["record_type"] == rl.CLAIM)
        self.assertNotIn("configurations", claim)

    def test_axis_less_claim_renders_single_configuration(self) -> None:
        records = build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.5}),
            make_claim("C-0001", ["E-0001"], 1),
        ])
        rendered = rl.render_claims(records)
        self.assertIn("configurations: single configuration", rendered)

    def test_axis_bearing_claim_renders_derived_axis_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _git_init(root)
            (root / "probe.py").write_text(LaunderingTests.SEED_PROBE, encoding="utf-8")
            ledger = root / "l.jsonl"
            base = ["--repo-root", str(root), "--ledger", str(ledger)]
            for seed in (1, 2):
                run_cli(base + [
                    "register", "--hypothesis", "h", "--metric", "seed", "--comparator", ">=",
                    "--threshold", "0", "--command", f"{sys.executable} probe.py --seed={seed}",
                    "--variation-axis", f"seed={seed}"])
                run_cli(base + ["execute", "--experiment-id", f"E-000{seed}"])
            run_cli(base + ["claim", "--metric", "seed", "--evidence", "E-0001", "--evidence", "E-0002"])
            rendered = rl.render_claims(rl.load_research_records(ledger))
        self.assertIn("configurations: seed=1, seed=2", rendered)


class RealConfigurationFreeTextGoneTests(unittest.TestCase):
    """item3: BOTH real claims views must render with no free-text configuration remnants — the
    grandfathered ``configurations`` field on C-0001/C-0002 is stored but never read."""

    def test_canonical_view_has_no_free_text_configuration_remnants(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        rendered = rl.render_claims(rl.load_research_records(repo_root / rl.LEDGER_REL))
        self.assertNotIn("76-79", rendered)
        self.assertNotIn("recovered", rendered)
        self.assertNotIn("ablation", rendered)

    def test_sort_probe_view_has_no_free_text_configuration_remnants(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        records = rl.load_research_records(repo_root / "experiments/sort-degradation-probe/ledger.jsonl")
        rendered = rl.render_claims(records)
        self.assertNotIn("quicksort=", rendered)
        self.assertNotIn("recursion", rendered)


class AxisEffectiveCheckerParityTests(unittest.TestCase):
    """item4: the runner's B4 axis_effective override and the checker's outcome re-derivation
    must agree — both now call the SAME ``research_ledger.final_outcome``."""

    def test_stored_not_evaluable_with_mismatched_axis_effective_passes(self) -> None:
        prereg = make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1",
                              command="run --seed=1", axis="seed=1")
        result = make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1",
                              {"err": 0.5, "axis_effective": "2"})
        result["outcome"] = "not-evaluable"
        records = build_chain([prereg, result])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertFalse(any(f.startswith("outcome-mismatch:") for f in findings), findings)

    def test_stored_supported_with_mismatched_axis_effective_flagged(self) -> None:
        # err=0.5 does not trip err<0.1, so derive_outcome ALONE would agree with the stored
        # (forged) "supported" — only the shared axis_effective override in final_outcome catches it.
        prereg = make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1",
                              command="run --seed=1", axis="seed=1")
        result = make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1",
                              {"err": 0.5, "axis_effective": "2"})
        records = build_chain([prereg, result])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertTrue(any(f.startswith("outcome-mismatch:") for f in findings), findings)

    def test_final_outcome_matches_derive_outcome_when_axis_confirmed(self) -> None:
        prereg = make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1",
                              command="run --seed=1", axis="seed=1")
        metrics = {"err": 0.5, "axis_effective": "1"}
        self.assertEqual(rl.final_outcome(prereg, metrics), rl.derive_outcome(DISCONFIRM, metrics))


class RealClaimsViewVocabularyTests(unittest.TestCase):
    """B1: render output for BOTH real claims views in this repo must never
    contain improvement/degradation vocabulary — exercised against the actual
    canonical and experiment ledgers, not a synthetic fixture."""

    def _assert_clean(self, ledger_rel: str) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        records = rl.load_research_records(repo_root / ledger_rel)
        rendered = rl.render_claims(records).lower()
        for word in FORBIDDEN_VOCABULARY:
            self.assertNotIn(word, rendered, f"{ledger_rel}: found {word!r}")

    def test_canonical_ledger_view_is_clean(self) -> None:
        self._assert_clean(rl.LEDGER_REL)

    def test_sort_probe_ledger_view_is_clean(self) -> None:
        self._assert_clean("experiments/sort-degradation-probe/ledger.jsonl")


if __name__ == "__main__":
    unittest.main()
