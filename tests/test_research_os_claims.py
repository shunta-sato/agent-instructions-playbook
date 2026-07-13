"""F2 claim-direction tests for the Research OS.

Covers the preregistered-direction rule: ``improves``/``degrades`` claims
require every cited registration's ``direction_if_supported`` to equal the
claim's direction, so grandfathered evidence backs only ``no-effect``/
``mixed``; the checker re-derives it and grandfathers pre-F2 claim records by
field-presence (absent ``direction_basis``). Shared builders come from
``test_research_os``; other claim/runner tests live there and in the sibling
``test_research_os_ledger`` / ``test_research_os_gate``.
"""

from __future__ import annotations

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


class DirectionPreregistrationCLITests(unittest.TestCase):
    # comparator ">" keeps err=0.05 "supported" so improves/degrades are
    # outcome-eligible and only the preregistered-direction rule is exercised.
    def _reg_exec(self, base: list[str], direction: str) -> None:
        run_cli(base + [
            "register", "--hypothesis", "h", "--metric", "err",
            "--comparator", ">", "--threshold", "0.1",
            "--command", LaunderingTests.CMD, "--direction-if-supported", direction,
        ])
        run_cli(base + ["execute", "--experiment-id", "E-0001"])

    def _claim(self, base: list[str], direction: str) -> tuple[int, str]:
        return run_cli(base + [
            "claim", "--direction", direction, "--metric", "err",
            "--configuration", "c", "--evidence", "E-0001",
        ])

    def test_matching_preregistered_direction_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "l.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            self._reg_exec(base, "improves")
            rc, _ = self._claim(base, "improves")
            self.assertEqual(rc, 0)
            self.assertEqual(cre.run_ledger_mode(ledger, Path(tmp)), 0)

    def test_mismatched_direction_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = ["--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl")]
            self._reg_exec(base, "improves")
            rc, _ = self._claim(base, "degrades")
        self.assertEqual(rc, 1)

    def test_none_direction_cannot_back_improves(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = ["--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl")]
            self._reg_exec(base, "none")
            rc, _ = self._claim(base, "improves")
        self.assertEqual(rc, 1)


class DirectionCheckerTests(unittest.TestCase):
    def test_post_f2_claim_with_wrong_preregistered_direction_flagged(self) -> None:
        # A post-F2 claim (carries direction_basis) asserting improves over
        # evidence preregistered degrades must be flagged on re-derivation.
        records = build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1", direction="degrades"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.5}),
            make_claim(
                "C-0001", ["E-0001"], 1, direction="improves",
                basis=[{"experiment_id": "E-0001", "outcome": "supported"}],
                direction_basis=[{"experiment_id": "E-0001", "direction_if_supported": "degrades"}],
            ),
        ])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertTrue(any(f.startswith("claim-binding:") for f in findings), findings)

    def test_grandfathered_claim_over_grandfathered_evidence_passes(self) -> None:
        # C-0001-style: improves over evidence lacking direction_if_supported,
        # with the claim lacking direction_basis → direction rule not enforced.
        records = build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1"),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.5}),
            make_claim("C-0001", ["E-0001"], 1, direction="improves"),
        ])
        with tempfile.TemporaryDirectory() as tmp:
            findings = cre.check_ledger(records, Path(tmp))
        self.assertEqual(findings, [])


# --- (R2b) no-effect requires an equivalence-bounds predicate ----------------


class NoEffectPredicateTests(unittest.TestCase):
    # LaunderingTests.CMD writes err=0.05.
    def _reg_exec(self, base: list[str], *predicate_args: str) -> None:
        run_cli(base + ["register", "--hypothesis", "h", "--metric", "err",
                        "--command", LaunderingTests.CMD, *predicate_args])
        run_cli(base + ["execute", "--experiment-id", "E-0001"])

    def _claim(self, base: list[str], direction: str) -> tuple[int, str]:
        return run_cli(base + ["claim", "--direction", direction, "--metric", "err",
                               "--configuration", "c", "--evidence", "E-0001"])

    def test_threshold_predicate_cannot_license_no_effect(self) -> None:
        # Reviewer point: a THRESHOLD predicate — even a supported one — must not
        # license no-effect; only an equivalence-bounds predicate can.
        with tempfile.TemporaryDirectory() as tmp:
            base = ["--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl")]
            self._reg_exec(base, "--comparator", ">", "--threshold", "0.1")  # supported
            rc, _ = self._claim(base, "no-effect")
        self.assertEqual(rc, 1)

    def test_equivalence_within_bounds_supported_accepts_no_effect(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "l.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            self._reg_exec(base, "--equivalence-bounds", "0.0", "0.1")  # 0.05 within → supported
            rc, _ = self._claim(base, "no-effect")
            self.assertEqual(rc, 0)
            self.assertEqual(cre.run_ledger_mode(ledger, Path(tmp)), 0)

    def test_equivalence_out_of_bounds_disconfirmed_cannot_be_no_effect(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = ["--repo-root", tmp, "--ledger", str(Path(tmp) / "l.jsonl")]
            self._reg_exec(base, "--equivalence-bounds", "0.1", "0.2")  # 0.05 outside → disconfirmed
            rc, _ = self._claim(base, "no-effect")
        self.assertEqual(rc, 1)

    def test_mixed_is_the_home_for_disconfirmed_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "l.jsonl"
            base = ["--repo-root", tmp, "--ledger", str(ledger)]
            self._reg_exec(base, "--comparator", "<", "--threshold", "0.1")  # 0.05 < 0.1 → disconfirmed
            rc, _ = self._claim(base, "mixed")
            self.assertEqual(rc, 0)
            self.assertEqual(cre.run_ledger_mode(ledger, Path(tmp)), 0)


if __name__ == "__main__":
    unittest.main()
