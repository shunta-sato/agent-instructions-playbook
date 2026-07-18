"""R4 + Q3 + B3 promotion-acknowledgment evidence-binding tests for the
Research OS gate. The downgrade binds to recorded ledger evidence, not
syntax: a valid acknowledgment cites ``Delivery-run:`` run_ids resolving to
``agent_run`` records with passing validation COMMANDS + a recorded
quality-gate pass + the run's own re-derived acceptance (Q3c), plus any
``C-<n>`` claim re-deriving in the canonical ledger. A promotion-required
LIVE path downgrades only when it is BOTH under a ``Covers:`` prefix AND
spanned by a digest-verified ``reviewed_files`` entry naming that exact path
— never by mere presence in a cited run's ``changed_files`` (no content
guarantee against a LATER edit of the same path, B3) or its ``allowed_files``
(Q3a). A DELETED path downgrades only via a matching tombstone entry. Ack
files/the run ledger are the promotion MECHANISM, never promotion-required
(Q3d). Mock ledgers, evaluate_diff only; real-git ``run_diff_mode`` proofs
for this same feature live in ``test_research_os_gate``.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts import check_research_evidence as cre
from tests.test_research_os import build_chain, make_claim, make_prereg, make_result

POLICY = {"path_modes": {"experiments/": "research"}, "safety_paths": ["SECURITY/"]}
ACK = ".agents/promotions/2026-07-13-promote.md"


def _run(run_id: str, passed: bool = True, changed=None, allowed=None, reviewed=None, agent_completed=True) -> dict:
    # Q3c: delivery evidence needs recorded validation COMMANDS + a passing
    # quality gate + the run's own re-derived ``evaluate_run_record`` acceptance.
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
        "outcome": {"agent_completed": agent_completed},
    }
    if reviewed is not None:
        run["reviewed_files"] = reviewed
    return run


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def _diff(root, run, changed_paths, covers=None, run_ids=None, **digest_kwargs) -> tuple[list[str], list[str]]:
    # Shared plumbing: write the ledger + ack, evaluate the changed-path set.
    _write_canonical_ledger(root, [run])
    _write_ack(root, ACK, covers=covers or ["src/", ".agents/promotions/"], run_ids=run_ids or ["run-1"])
    return cre.evaluate_diff([*changed_paths, ACK], root, POLICY, "research", **digest_kwargs)


class AckEvidenceBindingTests(unittest.TestCase):
    # A Q3c-passing run citing src/app.py only via changed_files (B3: no content guarantee).
    def _good_run(self, run_id="run-1"):
        return _run(run_id, passed=True, changed=["src/app.py"], allowed=["src/", ".agents/promotions/"])

    def test_changed_only_evidence_does_not_downgrade(self) -> None:
        # B3 (round-5 finding): a changed_files listing must not cover on its
        # own, or a run that changed src/app.py blesses ANY later edit of it.
        with tempfile.TemporaryDirectory() as tmp:
            findings, notes = _diff(Path(tmp), self._good_run(), ["src/app.py"])
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertFalse(any(n.startswith("promotion acknowledged:") for n in notes), notes)

    def test_reviewed_digest_of_same_path_downgrades_with_green_run_evidence(self) -> None:
        # The B3 fix: the SAME path, digest-reviewed against its content, DOES cover.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            app = root / "src" / "app.py"
            app.write_text("payload\n", encoding="utf-8")
            run = _run("run-1", passed=True, changed=["src/app.py"], allowed=["src/app.py", ".agents/promotions/"],
                       reviewed=[{"path": "src/app.py", "sha256": _sha256(app), "mode": "100644"}])
            findings, notes = _diff(root, run, ["src/app.py"])
        self.assertEqual([f for f in findings if f.startswith("promotion-required:")], [])
        self.assertIn(f"promotion acknowledged: {ACK} covers src/app.py", notes)

    def test_unknown_run_id_downgrades_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            findings, notes = _diff(Path(tmp), self._good_run(), ["src/app.py"], run_ids=["run-does-not-exist"])
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any(n.startswith(f"invalid-acknowledgment: {ACK}") and "unknown Delivery-run" in n
                            for n in notes), notes)

    def test_validation_failed_run_downgrades_nothing(self) -> None:
        run = _run("run-1", passed=False, changed=["src/app.py"], allowed=["src/"])
        with tempfile.TemporaryDirectory() as tmp:
            findings, notes = _diff(Path(tmp), run, ["src/app.py"])
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any("did not pass validation" in n for n in notes), notes)

    def test_caller_boolean_only_run_downgrades_nothing(self) -> None:
        # Q3c: a run asserting only outcome.validation_passed is NOT evidence.
        run = {"record_type": "agent_run", "run_id": "run-1",
               "outcome": {"validation_passed": True},
               "changed_files": ["src/app.py"], "allowed_files": ["src/"]}
        with tempfile.TemporaryDirectory() as tmp:
            findings, notes = _diff(Path(tmp), run, ["src/app.py"])
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any("did not pass validation" in n for n in notes), notes)

    def test_no_quality_gate_pass_downgrades_nothing(self) -> None:
        # Q3c: passing commands but quality_gate=not_run is not enough.
        run = _run("run-1", changed=["src/app.py"], allowed=["src/"])
        run["validation"]["quality_gate"] = "not_run"
        with tempfile.TemporaryDirectory() as tmp:
            findings, notes = _diff(Path(tmp), run, ["src/app.py"])
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any("quality gate not recorded as pass" in n for n in notes), notes)

    def test_allowed_and_changed_only_paths_stay_blocking(self) -> None:
        # Q3a/B3: allowed_files and changed_files are NEITHER coverage; none
        # of these three paths is digest-reviewed, so all stay blocking.
        run = _run("run-1", changed=["src/app.py"], allowed=["src/", "tools/"])
        with tempfile.TemporaryDirectory() as tmp:
            findings, notes = _diff(Path(tmp), run, ["src/app.py", "src/deep/x.py", "tools/build.py"],
                                     covers=["src/", "tools/", ".agents/promotions/"])
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertIn("promotion-required: src/deep/x.py", findings)
        self.assertIn("promotion-required: tools/build.py", findings)
        self.assertFalse(any(n.startswith("promotion acknowledged:") for n in notes), notes)

    def test_reviewed_digest_path_covers_but_allowed_only_paths_still_block(self) -> None:
        # Q3a: a digest-reviewed path covers; allowed_files-only paths don't.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            app = root / "src" / "app.py"
            app.write_text("payload\n", encoding="utf-8")
            run = _run("run-1", changed=[], allowed=["src/", "tools/"],
                       reviewed=[{"path": "src/app.py", "sha256": _sha256(app), "mode": "100644"}])
            findings, notes = _diff(root, run, ["src/app.py", "src/deep/x.py", "tools/build.py"],
                                     covers=["src/", "tools/", ".agents/promotions/"])
        self.assertIn(f"promotion acknowledged: {ACK} covers src/app.py", notes)
        self.assertIn("promotion-required: src/deep/x.py", findings)
        self.assertIn("promotion-required: tools/build.py", findings)

    def test_missing_delivery_run_is_structural_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_canonical_ledger(root, [self._good_run()])
            (root / ".agents" / "promotions").mkdir(parents=True, exist_ok=True)  # no Delivery-run line at all
            (root / ACK).write_text("Scope: t\nno research claims promoted\nCovers:\n- src/\n", encoding="utf-8")
            findings, notes = cre.evaluate_diff(["src/app.py", ACK], root, POLICY, "research")
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any("Delivery-run: run_ids" in n for n in notes), notes)

    def test_safety_never_downgraded_by_ack(self) -> None:
        run = _run("run-1", changed=["SECURITY/p.md"], allowed=["SECURITY/", ".agents/promotions/"])
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = _diff(Path(tmp), run, ["SECURITY/p.md"], covers=["SECURITY/", ".agents/promotions/"])
        self.assertIn("safety-review-required: SECURITY/p.md", findings)


class RunAcceptanceEvidenceTests(unittest.TestCase):
    """(a): a cited Delivery-run's OWN outcome must re-derive as accepted —
    passing validation + a quality-gate pass are not enough alone."""

    def _covers(self, **run_kwargs) -> tuple[list[str], list[str]]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "src").mkdir()
            app = root / "src" / "app.py"
            app.write_text("payload\n", encoding="utf-8")
            run = _run("run-1", allowed=["src/app.py", ".agents/promotions/"],
                       reviewed=[{"path": "src/app.py", "sha256": _sha256(app), "mode": "100644"}], **run_kwargs)
            return _diff(root, run, ["src/app.py"])

    def test_not_accepted_runs_downgrade_nothing(self) -> None:
        # agent_completed: false, and an out-of-scope changed file — both
        # otherwise pass validation + quality-gate + a matching digest.
        cases = {
            "agent-not-completed": dict(changed=["src/app.py"], agent_completed=False),
            "out-of-scope-changed-file": dict(changed=["src/app.py", "src/other.py"]),
        }
        for label, kwargs in cases.items():
            with self.subTest(label):
                findings, notes = self._covers(**kwargs)
                self.assertIn("promotion-required: src/app.py", findings)
                self.assertTrue(any("was not accepted" in n for n in notes), notes)

    def test_fully_accepted_run_downgrades(self) -> None:
        # Flip both defects above: agent_completed True + in-scope changes.
        findings, notes = self._covers(changed=["src/app.py"], agent_completed=True)
        self.assertEqual([f for f in findings if f.startswith("promotion-required:")], [])
        self.assertIn(f"promotion acknowledged: {ACK} covers src/app.py", notes)


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
            (root / "src").mkdir()
            app = root / "src" / "app.py"
            app.write_text("payload\n", encoding="utf-8")
            self._ledger_with_claim(root, _run(
                "run-1", changed=["src/app.py"], allowed=["src/app.py", ".agents/promotions/"],
                reviewed=[{"path": "src/app.py", "sha256": _sha256(app), "mode": "100644"}],
            ))
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
    """Q3b/B3: a digest-verified ``reviewed_files`` entry covers a promoted
    path; this is the ONLY coverage source — never changed_files, never
    allowed_files."""

    def test_reviewed_digest_match_and_drift(self) -> None:
        cases = {"matching": ("hello\n", None), "stale": ("changed since the review\n", "0" * 64)}
        for label, (content, forced_digest) in cases.items():
            with self.subTest(label):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    (root / "docs").mkdir()
                    guide = root / "docs" / "guide.md"
                    guide.write_text(content, encoding="utf-8")
                    digest = forced_digest or _sha256(guide)  # forced -> drifted from disk content
                    run = _run("run-1", changed=[], allowed=[],
                               reviewed=[{"path": "docs/guide.md", "sha256": digest, "mode": "100644"}])
                    findings, notes = _diff(root, run, ["docs/guide.md"], covers=["docs/", ".agents/promotions/"])
                if forced_digest:
                    self.assertIn("promotion-required: docs/guide.md", findings)
                    self.assertIn("stale-review: docs/guide.md", notes)
                else:
                    self.assertEqual([f for f in findings if f.startswith("promotion-required:")], [])
                    self.assertIn(f"promotion acknowledged: {ACK} covers docs/guide.md", notes)

    def test_symlink_reviewed_file_matches_on_disk(self) -> None:
        # A reviewed path that is a git-tracked SYMLINK to a directory (e.g.
        # .claude/skills/<name>) covers via its readlink-target digest.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "real_dir").mkdir()
            (root / "link").symlink_to("real_dir")
            run = _run("run-1", changed=[], allowed=[],
                       reviewed=[{"path": "link", "sha256": hashlib.sha256(b"real_dir").hexdigest(), "mode": "120000"}])
            findings, notes = _diff(root, run, ["link"], covers=["link", ".agents/promotions/"])
        self.assertEqual([f for f in findings if f.startswith("promotion-required:")], [])
        self.assertIn(f"promotion acknowledged: {ACK} covers link", notes)


class MechanismPathTests(unittest.TestCase):
    """Q3d: acknowledgment files and the run ledger are the promotion/recording
    MECHANISM, not promoted content — never ``promotion-required``."""

    def test_ack_and_ledger_paths_are_never_promotion_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            changed = [".agents/promotions/README.md", ".agents/runs/agent-runs.jsonl"]
            findings, _ = cre.evaluate_diff(changed, Path(tmp), POLICY, "research")
        self.assertEqual([f for f in findings if f.startswith("promotion-required:")], [])


class AckDeletionCoverageTests(unittest.TestCase):
    """(c)/M2/M5: a DELETED path (absent at head, present at base) is covered
    only by a matching tombstone's (base_sha256, mode) AT THE RANGE BASE — a
    normal digest entry never covers a deletion, and a tombstone never covers
    a live file. The real-git ``run_diff_mode`` wiring lives in
    ``test_research_os_gate``/``test_research_os_mode``."""

    BASE_DIGEST = hashlib.sha256(b"legacy\n").hexdigest()
    BASE_MODE = "100644"

    def _eval(self, reviewed, identity):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run = _run("run-1", changed=["src/old.py"], allowed=["src/old.py", ".agents/promotions/"],
                       reviewed=reviewed)
            return _diff(root, run, ["src/old.py"], identity=identity,
                         base_identity=lambda p: (self.BASE_DIGEST, self.BASE_MODE))

    def test_deletion_coverage_matrix(self) -> None:
        # tombstone matches -> downgrade; absent/mismatched/wrong-kind -> blocking.
        cases = {
            "matching-tombstone-downgrades": ([{"path": "src/old.py", "deleted": True,
                                                 "base_sha256": self.BASE_DIGEST, "mode": self.BASE_MODE}], True, None),
            "missing-tombstone-blocks": ([], False, None),
            "mismatched-digest-tombstone-is-blocking": ([{"path": "src/old.py", "deleted": True,
                                                 "base_sha256": "0" * 64, "mode": self.BASE_MODE}],
                                                 False, "tombstone-base-mismatch"),
            "mismatched-mode-tombstone-is-blocking": ([{"path": "src/old.py", "deleted": True,
                                                 "base_sha256": self.BASE_DIGEST, "mode": "100755"}],
                                                 False, "tombstone-base-mismatch"),
            "unbound-mode-tombstone-never-covers": ([{"path": "src/old.py", "deleted": True,
                                                 "base_sha256": self.BASE_DIGEST}], False, "unbound-mode"),
            "normal-entry-never-covers-deletion": ([{"path": "src/old.py",
                                                      "sha256": self.BASE_DIGEST, "mode": self.BASE_MODE}], False, None),
        }
        for label, (reviewed, covered, stale) in cases.items():
            with self.subTest(label):
                findings, notes = self._eval(reviewed, identity=lambda p: (None, None))
                required = [f for f in findings if f.startswith("promotion-required:")]
                self.assertEqual(required, [] if covered else ["promotion-required: src/old.py"])
                if stale:
                    self.assertTrue(any(n.startswith(f"{stale}: src/old.py") for n in notes), notes)

    def test_tombstone_never_covers_a_live_file(self) -> None:
        # src/old.py is LIVE (head identity == base identity) — a tombstone
        # entry for it, even with a matching (digest, mode), must not cover.
        findings, _ = self._eval(
            [{"path": "src/old.py", "deleted": True, "base_sha256": self.BASE_DIGEST, "mode": self.BASE_MODE}],
            identity=lambda p: (self.BASE_DIGEST, self.BASE_MODE),
        )
        self.assertIn("promotion-required: src/old.py", findings)


class LiveModeBindingTests(unittest.TestCase):
    """M2/G3: a LIVE promoted path binds to (digest, git-mode), not bytes
    alone — a reviewed regular file cannot be covered by a same-bytes symlink
    (or 100644 by a 100755), and a mode-less entry never covers (no grandfather)."""

    DIGEST = "d" * 64

    def _eval(self, entry_mode, current_mode):
        reviewed = [{"path": "src/app.py", "sha256": self.DIGEST, **({"mode": entry_mode} if entry_mode else {})}]
        with tempfile.TemporaryDirectory() as tmp:
            run = _run("run-1", changed=[], allowed=[], reviewed=reviewed)
            return _diff(Path(tmp), run, ["src/app.py"], covers=["src/", ".agents/promotions/"],
                         identity=lambda p: (self.DIGEST, current_mode))

    def test_mode_mismatch_does_not_cover(self) -> None:
        findings, notes = self._eval(entry_mode="100644", current_mode="100755")
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any(n.startswith("stale-review: src/app.py") for n in notes), notes)

    def test_symlink_mode_does_not_cover_a_reviewed_regular_file(self) -> None:
        findings, _ = self._eval(entry_mode="100644", current_mode="120000")
        self.assertIn("promotion-required: src/app.py", findings)

    def test_matching_digest_and_mode_covers(self) -> None:
        findings, notes = self._eval(entry_mode="100644", current_mode="100644")
        self.assertEqual([f for f in findings if f.startswith("promotion-required:")], [])
        self.assertIn(f"promotion acknowledged: {ACK} covers src/app.py", notes)

    def test_no_stored_mode_never_covers(self) -> None:
        # G3: the grandfather path is removed — a mode-less entry blocks, it no longer downgrades.
        findings, notes = self._eval(entry_mode=None, current_mode="100755")
        self.assertIn("promotion-required: src/app.py", findings)
        self.assertTrue(any(n.startswith("unbound-mode: src/app.py") for n in notes), notes)


if __name__ == "__main__":
    unittest.main()
