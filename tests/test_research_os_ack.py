"""R4 promotion-acknowledgment evidence-binding tests for the Research OS gate.

The F7 downgrade now binds to recorded ledger evidence, not syntax: a valid
acknowledgment must cite ``Delivery-run:`` run_ids that resolve to green
``agent_run`` records and any ``C-<n>`` claim that re-derives in the canonical
ledger, and a promotion-required path is downgraded only when it is BOTH under
a ``Covers:`` prefix AND spanned by the cited runs' ``changed_files`` ∪
``allowed_files``. Mock ledgers here; the boundary/mode tests live in the
sibling ``test_research_os_gate.py``.
"""

from __future__ import annotations

import contextlib
import io
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts import check_research_evidence as cre
from tests.test_research_os import build_chain, make_claim, make_prereg, make_result

POLICY = {"path_modes": {"experiments/": "research"}, "safety_paths": ["SECURITY/"]}
ACK = ".agents/promotions/2026-07-13-promote.md"


def _run(run_id: str, passed: bool = True, changed=None, allowed=None) -> dict:
    return {
        "record_type": "agent_run",
        "run_id": run_id,
        "validation": {"passed": passed},
        "changed_files": changed or [],
        "allowed_files": allowed or [],
    }


def _write_canonical_ledger(root: Path, records: list[dict]) -> None:
    path = root / ".agents" / "runs" / "agent-runs.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")


def _write_ack(root: Path, ack_rel: str, covers, run_ids, claim_line="no research claims promoted") -> None:
    ack = root / ack_rel
    ack.parent.mkdir(parents=True, exist_ok=True)
    covers_block = "\n".join(f"- {p}" for p in covers)
    run_block = "\n".join(f"Delivery-run: {r}" for r in run_ids)
    ack.write_text(f"Scope: test\n{claim_line}\n{run_block}\nCovers:\n{covers_block}\n", encoding="utf-8")


class AckEvidenceBindingTests(unittest.TestCase):
    # A run whose union spans the ack's own path AND the promoted delivery path.
    def _good_run(self, run_id="run-1"):
        return _run(run_id, passed=True, changed=["src/app.py"], allowed=["src/", ".agents/promotions/"])

    def test_happy_path_downgrades_with_green_run_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_canonical_ledger(root, [self._good_run()])
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"])
            findings, notes = cre.evaluate_diff(["src/app.py", ACK], root, POLICY, "research")
        self.assertEqual([f for f in findings if f.startswith("promotion-required:")], [])
        self.assertIn(f"promotion acknowledged: {ACK} covers src/app.py", notes)

    def test_unknown_run_id_downgrades_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_canonical_ledger(root, [self._good_run("run-1")])
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-does-not-exist"])
            findings, notes = cre.evaluate_diff(["src/app.py", ACK], root, POLICY, "research")
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any(n.startswith(f"invalid-acknowledgment: {ACK}") and "unknown Delivery-run" in n
                            for n in notes), notes)

    def test_validation_failed_run_downgrades_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_canonical_ledger(root, [_run("run-1", passed=False, changed=["src/app.py"], allowed=["src/"])])
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"])
            findings, notes = cre.evaluate_diff(["src/app.py", ACK], root, POLICY, "research")
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any("did not pass validation" in n for n in notes), notes)

    def test_outcome_validation_passed_shape_accepted(self) -> None:
        # R4.2 accepts outcome.validation_passed as an alternative to validation.passed.
        run = {"record_type": "agent_run", "run_id": "run-1",
               "outcome": {"validation_passed": True},
               "changed_files": ["src/app.py"], "allowed_files": ["src/", ".agents/promotions/"]}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_canonical_ledger(root, [run])
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"])
            findings, _ = cre.evaluate_diff(["src/app.py", ACK], root, POLICY, "research")
        self.assertEqual([f for f in findings if f.startswith("promotion-required:")], [])

    def test_path_outside_run_union_stays_blocking(self) -> None:
        # R4.3: even under a Covers prefix, a path not spanned by the cited runs'
        # files stays blocking; a directory in the union covers its subtree.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_canonical_ledger(root, [_run("run-1", changed=["src/app.py"], allowed=["src/", ".agents/promotions/"])])
            _write_ack(root, ACK, covers=["src/", "tools/", ".agents/promotions/"], run_ids=["run-1"])
            findings, notes = cre.evaluate_diff(["src/deep/x.py", "tools/build.py", ACK], root, POLICY, "research")
        # src/deep/x.py is under the "src/" directory in the union → downgraded.
        self.assertIn(f"promotion acknowledged: {ACK} covers src/deep/x.py", notes)
        # tools/build.py is under a Covers prefix but NOT in the run union → blocking.
        self.assertIn("promotion-required: tools/build.py", findings)

    def test_missing_delivery_run_is_structural_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_canonical_ledger(root, [self._good_run()])
            # No Delivery-run line at all.
            (root / ".agents" / "promotions").mkdir(parents=True, exist_ok=True)
            (root / ACK).write_text("Scope: t\nno research claims promoted\nCovers:\n- src/\n", encoding="utf-8")
            findings, notes = cre.evaluate_diff(["src/app.py", ACK], root, POLICY, "research")
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any("Delivery-run: run_ids" in n for n in notes), notes)

    def test_safety_never_downgraded_by_ack(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_canonical_ledger(root, [_run("run-1", changed=["SECURITY/p.md"], allowed=["SECURITY/", ".agents/promotions/"])])
            _write_ack(root, ACK, covers=["SECURITY/", ".agents/promotions/"], run_ids=["run-1"])
            findings, _ = cre.evaluate_diff(["SECURITY/p.md", ACK], root, POLICY, "research")
        self.assertIn("safety-review-required: SECURITY/p.md", findings)


class AckClaimBindingTests(unittest.TestCase):
    """R4.1: a cited ``C-<n>`` must re-derive in the canonical ledger."""

    def _ledger_with_claim(self, root: Path, run) -> None:
        # A valid research chain (prereg+result+claim) alongside the agent_run.
        claim_records = build_chain([
            make_prereg("E-0001", "2026-01-01T00:00:00+00:00", "d1", command="run", direction=""),
            make_result("E-0001", "2026-01-02T00:00:00+00:00", "d1", {"err": 0.5}),
            make_claim("C-0001", ["E-0001"], 1, direction="improves"),
        ])
        path = root / ".agents" / "runs" / "agent-runs.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [json.dumps(run)] + [json.dumps(r) for r in claim_records]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def test_resolving_claim_id_allows_downgrade(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._ledger_with_claim(root, _run("run-1", changed=["src/app.py"], allowed=["src/", ".agents/promotions/"]))
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"], claim_line="promotes C-0001")
            findings, notes = cre.evaluate_diff(["src/app.py", ACK], root, POLICY, "research")
        self.assertEqual([f for f in findings if f.startswith("promotion-required:")], [])
        self.assertIn(f"promotion acknowledged: {ACK} covers src/app.py", notes)

    def test_nonexistent_claim_id_downgrades_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._ledger_with_claim(root, _run("run-1", changed=["src/app.py"], allowed=["src/", ".agents/promotions/"]))
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"], claim_line="promotes C-9999")
            findings, notes = cre.evaluate_diff(["src/app.py", ACK], root, POLICY, "research")
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any("C-9999 does not resolve" in n for n in notes), notes)


class AckDiffModeTests(unittest.TestCase):
    """R4 end-to-end through ``run_diff_mode`` over a real git range."""

    def _capture(self, fn, *args) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = fn(*args)
        return rc, buf.getvalue()

    def _git(self, root: Path, *args) -> None:
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)

    def test_promotion_with_evidence_bound_ack_exits_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
                self._git(root, *args)
            policy = root / "policy.json"
            policy.write_text(json.dumps(POLICY), encoding="utf-8")
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("x\n", encoding="utf-8")
            _write_canonical_ledger(root, [_run("run-1", changed=["src/app.py"], allowed=["src/", ".agents/promotions/"])])
            self._git(root, "add", "-A")
            self._git(root, "commit", "-qm", "base")
            (root / "src" / "app.py").write_text("y\n", encoding="utf-8")
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"])
            self._git(root, "add", "-A")
            self._git(root, "commit", "-qm", "promote")
            rc, _ = self._capture(cre.run_diff_mode, "HEAD~1..HEAD", policy, root, "research")
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
