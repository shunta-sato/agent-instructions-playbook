"""B1 claim-category tests for the Research OS (round-5 finding B1, review
comment 3568085567).

Covers the machine-derived claim category: a claim carries no caller-supplied
direction: ``derive_claim_category`` derives ``supported`` / ``within-bounds``
/ ``mixed`` purely from cited-evidence outcomes and predicate shapes, the
checker re-derives it independently (field-presence grandfathered for
pre-B1 records), and ``render_claims`` states only the predicate fact — never
improves/degrades/better/worse/no-effect vocabulary. Shared builders come
from ``test_research_os``; other claim/runner tests live there and in the
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
    LaunderingTests,
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

            rc, _ = run_cli(base + [
                "claim", "--metric", "latency", "--configuration", "c", "--evidence", "E-0001",
            ])
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
    """The three derived-category outcomes, driven purely by evidence outcome
    + predicate shape (never a claim CLI flag)."""

    CMD = LaunderingTests.CMD  # writes err=0.05

    def _claim(self, base: list[str], evidence: list[str]) -> tuple[int, str]:
        args = ["claim", "--metric", "err", "--configuration", "c"]
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

    def test_disconfirmed_evidence_yields_mixed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "l.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            run_cli(base + ["register", "--hypothesis", "h", "--metric", "err",
                            "--comparator", "<", "--threshold", "0.1", "--command", self.CMD])
            run_cli(base + ["execute", "--experiment-id", "E-0001"])  # 0.05 < 0.1 → disconfirmed
            rc, _ = self._claim(base, ["E-0001"])
            self.assertEqual(rc, 0)
            self.assertEqual(self._derived_category(ledger), rl.CATEGORY_MIXED)
            rendered = rl.render_claims(rl.load_research_records(ledger))
        self.assertIn("err evidence is mixed — observed in a single configuration.", rendered)

    def test_mixed_predicate_types_yield_mixed(self) -> None:
        # Two supported experiments on the same metric, but one threshold and
        # one equivalence predicate: a predicate-shape mix, not a directional one.
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
            self.assertEqual(rc, 0)
            self.assertEqual(self._derived_category(ledger), rl.CATEGORY_MIXED)


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
                "claim", "--direction", "improves", "--metric", "err",
                "--configuration", "c", "--evidence", "E-0001",
            ])


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
