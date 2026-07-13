"""R4 + Q3 promotion-acknowledgment evidence-binding tests for the Research OS
gate.

The downgrade binds to recorded ledger evidence, not syntax: a valid
acknowledgment cites ``Delivery-run:`` run_ids that resolve to ``agent_run``
records with passing validation COMMANDS and a recorded quality-gate pass (Q3c),
plus any ``C-<n>`` claim that re-derives in the canonical ledger. A
promotion-required path is downgraded only when it is BOTH under a ``Covers:``
prefix AND spanned by a cited run's ``changed_files`` or a digest-verified
``reviewed_files`` entry — never its ``allowed_files`` (Q3a/Q3b). Acknowledgment
files and the run ledger are the promotion MECHANISM, never promotion-required
(Q3d). Mock ledgers here; boundary/mode tests live in ``test_research_os_gate``.
"""

from __future__ import annotations

import contextlib
import hashlib
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


def _run(run_id: str, passed: bool = True, changed=None, allowed=None, reviewed=None) -> dict:
    # Q3c: delivery evidence needs recorded validation COMMANDS + a passing
    # quality gate, not a caller boolean; a failing run flips both.
    validation = (
        {"commands": [{"cmd": "make test-unit", "exit_code": 0, "passed": True}],
         "passed": True, "quality_gate": "pass"}
        if passed else
        {"commands": [{"cmd": "make test-unit", "exit_code": 1, "passed": False}],
         "passed": False, "quality_gate": "no-submit"}
    )
    run = {
        "record_type": "agent_run",
        "run_id": run_id,
        "validation": validation,
        "changed_files": changed or [],
        "allowed_files": allowed or [],
    }
    if reviewed is not None:
        run["reviewed_files"] = reviewed
    return run


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

    def test_caller_boolean_only_run_downgrades_nothing(self) -> None:
        # Q3c inversion: a run asserting only outcome.validation_passed (no
        # recorded validation commands or quality-gate pass) is NOT evidence.
        run = {"record_type": "agent_run", "run_id": "run-1",
               "outcome": {"validation_passed": True},
               "changed_files": ["src/app.py"], "allowed_files": ["src/"]}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_canonical_ledger(root, [run])
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"])
            findings, notes = cre.evaluate_diff(["src/app.py", ACK], root, POLICY, "research")
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any("did not pass validation" in n for n in notes), notes)

    def test_no_quality_gate_pass_downgrades_nothing(self) -> None:
        # Q3c: passing validation commands but quality_gate=not_run is not enough.
        run = _run("run-1", changed=["src/app.py"], allowed=["src/"])
        run["validation"]["quality_gate"] = "not_run"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_canonical_ledger(root, [run])
            _write_ack(root, ACK, covers=["src/", ".agents/promotions/"], run_ids=["run-1"])
            findings, notes = cre.evaluate_diff(["src/app.py", ACK], root, POLICY, "research")
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any("quality gate not recorded as pass" in n for n in notes), notes)

    def test_allowed_only_path_stays_blocking(self) -> None:
        # Q3a inversion (round-3 test overturned): allowed_files is authorization
        # scope, NOT coverage. Only changed_files (here src/app.py) cover; paths
        # present merely in allowed_files (src/deep/x.py, tools/build.py) block.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_canonical_ledger(root, [_run("run-1", changed=["src/app.py"], allowed=["src/", "tools/"])])
            _write_ack(root, ACK, covers=["src/", "tools/", ".agents/promotions/"], run_ids=["run-1"])
            findings, notes = cre.evaluate_diff(["src/app.py", "src/deep/x.py", "tools/build.py", ACK], root, POLICY, "research")
        self.assertIn(f"promotion acknowledged: {ACK} covers src/app.py", notes)
        self.assertIn("promotion-required: src/deep/x.py", findings)
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


class AckReviewedFilesTests(unittest.TestCase):
    """Q3b: a digest-verified ``reviewed_files`` entry covers a promoted path;
    coverage union is ``changed_files`` ∪ reviewed_files, never allowed_files."""

    def _digest(self, path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def test_reviewed_file_with_matching_digest_covers_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            reviewed_path = root / "docs" / "guide.md"
            reviewed_path.write_text("hello\n", encoding="utf-8")
            run = _run("run-1", changed=[], allowed=[],
                       reviewed=[{"path": "docs/guide.md", "sha256": self._digest(reviewed_path)}])
            _write_canonical_ledger(root, [run])
            _write_ack(root, ACK, covers=["docs/", ".agents/promotions/"], run_ids=["run-1"])
            findings, notes = cre.evaluate_diff(["docs/guide.md", ACK], root, POLICY, "research")
        self.assertEqual([f for f in findings if f.startswith("promotion-required:")], [])
        self.assertIn(f"promotion acknowledged: {ACK} covers docs/guide.md", notes)

    def test_reviewed_file_with_stale_digest_stays_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs" / "guide.md").write_text("changed since the review\n", encoding="utf-8")
            run = _run("run-1", changed=[], allowed=[],
                       reviewed=[{"path": "docs/guide.md", "sha256": "0" * 64}])  # recorded digest drifted
            _write_canonical_ledger(root, [run])
            _write_ack(root, ACK, covers=["docs/", ".agents/promotions/"], run_ids=["run-1"])
            findings, notes = cre.evaluate_diff(["docs/guide.md", ACK], root, POLICY, "research")
        self.assertIn("promotion-required: docs/guide.md", findings)
        self.assertIn("stale-review: docs/guide.md", notes)

    def test_symlink_reviewed_file_matches_on_disk(self) -> None:
        # Supervisor follow-up: a reviewed path that is a git-tracked SYMLINK to
        # a directory (e.g. .claude/skills/<name>) must be covered by its
        # readlink-target digest, not rejected/mismatched by following it.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "real_dir").mkdir()
            (root / "link").symlink_to("real_dir")
            run = _run("run-1", changed=[], allowed=[],
                       reviewed=[{"path": "link", "sha256": hashlib.sha256(b"real_dir").hexdigest()}])
            _write_canonical_ledger(root, [run])
            _write_ack(root, ACK, covers=["link", ".agents/promotions/"], run_ids=["run-1"])
            findings, notes = cre.evaluate_diff(["link", ACK], root, POLICY, "research")
        self.assertEqual([f for f in findings if f.startswith("promotion-required:")], [])
        self.assertIn(f"promotion acknowledged: {ACK} covers link", notes)


class AckSymlinkHeadBlobTests(unittest.TestCase):
    """Q3b follow-up: the gate's ``--diff-range`` verification hashes the
    ``git show <head>:<path>`` blob, which for a symlink IS its readlink target
    string — match and mismatch/stale, exercised through ``run_diff_mode``."""

    def _capture(self, fn, *args) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = fn(*args)
        return rc, buf.getvalue()

    def _git(self, root: Path, *args) -> None:
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)

    def _repo_with_committed_symlink(self, tmp: str, reviewed_sha256: str) -> tuple[Path, Path]:
        root = Path(tmp)
        for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            self._git(root, *args)
        policy = root / "policy.json"
        policy.write_text(json.dumps(POLICY), encoding="utf-8")
        _write_canonical_ledger(root, [_run(
            "run-1", changed=[], allowed=[],
            reviewed=[{"path": "link", "sha256": reviewed_sha256}],
        )])
        self._git(root, "add", "-A")
        self._git(root, "commit", "-qm", "base")
        (root / "target_dir").mkdir()
        (root / "link").symlink_to("target_dir")  # tracked symlink to a DIRECTORY
        _write_ack(root, ACK, covers=["link", ".agents/promotions/"], run_ids=["run-1"])
        self._git(root, "add", "-A")
        self._git(root, "commit", "-qm", "promote")
        return root, policy

    def test_matching_symlink_digest_downgrades_at_head(self) -> None:
        correct = hashlib.sha256(b"target_dir").hexdigest()  # readlink target, no newline
        with tempfile.TemporaryDirectory() as tmp:
            root, policy = self._repo_with_committed_symlink(tmp, correct)
            rc, output = self._capture(cre.run_diff_mode, "HEAD~1..HEAD", policy, root, "research")
        self.assertEqual(rc, 0)
        self.assertIn(f"NOTE promotion acknowledged: {ACK} covers link", output)

    def test_mismatched_symlink_digest_stays_blocking_and_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root, policy = self._repo_with_committed_symlink(tmp, "0" * 64)  # recorded digest drifted
            rc, output = self._capture(cre.run_diff_mode, "HEAD~1..HEAD", policy, root, "research")
        self.assertEqual(rc, 1)
        self.assertIn("FINDING promotion-required: link", output)
        self.assertIn("NOTE stale-review: link", output)


class MechanismPathTests(unittest.TestCase):
    """Q3d: acknowledgment files and the run ledger are the promotion/recording
    MECHANISM, not promoted content — never ``promotion-required``."""

    def test_ack_and_ledger_paths_are_never_promotion_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            changed = [".agents/promotions/README.md", ".agents/runs/agent-runs.jsonl"]
            findings, _ = cre.evaluate_diff(changed, Path(tmp), POLICY, "research")
        self.assertEqual([f for f in findings if f.startswith("promotion-required:")], [])


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
