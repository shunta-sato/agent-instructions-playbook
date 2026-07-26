# Submission evidence record + lint (Wave 2) — design record

Owner: supervisor (architect). Continues the lint-migration program
(`plans/20260725-lint-migration.md` Wave-2 scope: "`submission_evidence`
ledger record + `lint_submission.py` + quality-gate reduction to residual
semantic judgment"). A read-only classification pass over every quality-gate
demand preceded this adjudication: roughly 40% already enforced by existing
lints, ~30% machine-checkable but unenforced, ~30% genuinely semantic.

## Adjudications (the decisions in this wave)

1. **The record follows the research-gate precedent, not a new invention.**
   The promotion machinery (`research_gate.py`) is the repo's strongest
   existing pattern: structured record, re-derived (never trusted)
   citations, content-identity binding, fail-closed on gaps. The
   `submission_evidence` record adopts all four properties. It lives in the
   SAME ledger (`.agents/runs/agent-runs.jsonl`, `record_type:
   "submission_evidence"`) — the ledger metadata line already declares that
   existing scripts ignore non-`agent_run` records, so this is
   forward-compatible by design and keeps one evidence ledger.
2. **Writer and checker are separate scripts.** `agent_run.py` is near its
   structure budget and stays per-delegated-run. New
   `scripts/submission_run.py` (writer) captures at record time, computed by
   the tool rather than self-reported: changed files from git (NUL-delimited,
   research-gate pattern) each with sha256; validation command + exit-code
   pairs; cited delegated run IDs; triggered quality-gate branch keys with
   the artifact path satisfying each; the gate decision. New
   `scripts/lint_submission.py` (checker) re-derives everything: cited runs
   must evaluate `accepted` AND carry `quality_gate` in {pass, submit} (the
   research-gate criterion, stricter than `evaluate_run_record`'s
   `not_run`-passes semantics — which stays unchanged for backward
   compatibility); cited artifacts must exist and, for a cited
   workflow-contract review, conclude `submit` (a SUBMISSION condition, not
   artifact validity — `no-submit` remains a valid review outcome, so this
   check belongs here and NOT in `lint_artifacts`); the canonical verify
   chain must appear in the validation pairs with exit 0; changed-file
   digests must match HEAD (post-record edits invalidate the record).
3. **Enforcement is validate-if-present, then ratchet.** Requiring a
   submission record on every PR today would fail every in-flight branch and
   invert the adoption order. `lint_submission.py` validates any record
   matching the current diff and passes-with-note when none exists; a
   project-policy flag can later flip it to required once the practice has
   instances. The Wave-2 PR itself records the first submission_evidence
   entry (dogfood), so the lint is exercised on real data from day one.
4. **quality-gate reference shrinks only where a lint actually took over.**
   Rows classified (a) — already enforced — compress to one-line pointers at
   the owning lint. Rows that `lint_submission.py` now covers compress
   likewise. Rows classified (c) — root-cause validity, waiver boundedness,
   claim meaningfulness, comment judgment — stay prose verbatim; the Wave-0
   "not lintable" list is binding. The edit is measured: the behavior-eval
   quality-gate packs re-run after the reduction, compared against the MT2
   baseline (decision 6/6, output-contains 30/30).
5. **Two tool-permits-what-prose-forbids gaps close mechanically.**
   `judge_agent_run.py` defaulting to the latest run when `--run-id` is
   omitted contradicts the explicit-identity rule (`quality-gate.md`
   forbids `latest`); `--run-id` becomes required (caller sweep found only
   prose references, all already using explicit IDs). The stale
   positional-invocation wording for `check_structure.py` in the
   quality-gate SKILL capsule and dev-workflow SKILL body is aligned to
   `--working-tree` (doc-drift found by the classification pass).
6. **Registry addition, not expansion:** `nfr-gate-report`
   (`reports/resource/*.md`, exact headings from the embedded-nfr-gate
   template) joins the artifact registry — quality-gate names it as evidence
   but Wave 1 only covered the `.json` metrics file. Zero instances;
   fail-closed at creation like the UI packs.
7. **Deferred, recorded:** design-ledger entry enforcement (the ledger has
   never had a real entry; enforcing before practice exists is noise —
   telemetry-driven); a canonical path for the UI Visual Verification Report
   (needs a skill-content decision in visual-regression-testing first);
   branch-completion's mechanical linkage to the submission record (natural
   Wave-2b once records exist); per-branch artifact paths for the seven
   evidence kinds that have no declared path (observability plan, complexity
   budget, responsibility map, performance review, ADA record, coverage
   report, C++ Doxygen completeness).

## Record schema (pinned for workers)

```json
{
  "schema_version": 1,
  "record_type": "submission_evidence",
  "run_id": "<issued>",
  "created_at": "<utc>",
  "branch": "<git branch name>",
  "base_ref": "<merge base or empty>",
  "changed_files": [{"path": "...", "sha256": "..."}],
  "validation": {"commands": [{"cmd": "...", "exit_code": 0, "passed": true}]},
  "cited_runs": ["<agent_run run_id>", "..."],
  "triggered_branches": [{"branch": "<quality-gate row key>", "artifact": "<path or run id>"}],
  "gate_decision": "submit | no-submit",
  "notes": "<open risks / skips, free text>"
}
```

Writer computes `changed_files` and digests itself; `cited_runs` and
`triggered_branches` are declared by the recorder and RE-DERIVED by the
checker. Deleted files are recorded with `"sha256": null` and matched
against absence at HEAD.

## Workers

W-A: submission_run.py + tests. W-B: lint_submission.py + judge_agent_run
`--run-id` required + wiring (Makefile/CI validate-if-present) + tests.
W-C (after A/B land): quality-gate reference reduction + doc-drift fixes +
registry addition. Supervisor: design, integration, behavior-eval re-run,
Opus adversarial review.

## Handoff

- 2026-07-26: Wave 2 started on branch `lint-migration-w2` (based on main
  b5ffbd9, Wave 1 merged). Schema and adjudications above are the binding
  input to the worker briefs; the behavior-eval re-run gates the
  quality-gate reduction before the PR.
- 2026-07-26 (integration): W2-A writer (run be4aeea9), W2-B checker +
  judge tightening + wiring (run ca6fe094), W2-C reduction (run 48068a26)
  all accepted. Supervisor applied the escalated artifact-shape decision:
  a run-id-shaped `triggered_branches[].artifact` is validated as a cited
  run (`artifact-run:*` findings) instead of a HEAD path, per the pinned
  schema's "path or run id"; regression test added. Supervisor also added
  the `nfr-gate-report` registry kind (exact headings from the
  embedded-nfr-gate template). W2-C's one disclosed inference — merging
  the verbatim-duplicate delegated-evidence row 61 into row 41 — was
  verified line-by-line and accepted (all four criteria preserved in the
  merged row). Behavior-eval re-measurement (6 isolated Sonnet subjects,
  quality-gate cases only): decision 6/6 = baseline, no gate call moved;
  output-contains 9/10 with the single miss being vocabulary drift toward
  the reference's own §3 wording, recorded without editing the
  expectation (`evals/behavior-runs/20260726-w2-reduction-sonnet-5.json`).
  370 tests OK; all lints and `make verify` green. Next: Opus adversarial
  review, dogfood submission record, PR.
- 2026-07-26 (Opus adversarial review, run 8151247d): verdict
  integrate-after-fixes with 3 blockers — the strongest review of the
  program so far, all findings reproduced by execution. Supervisor applied:
  - F1 (blocker): records had no commit identity, so the first merged
    record would have turned every later PR touching its paths into a
    stale-record failure — silently flipping the deferred ratchet. Fixed
    with a commit-identity model: the writer stamps `head_commit`; range
    modes consider only records whose head_commit lies INSIDE the range
    (a merged record describes its own commit forever); working-tree mode
    matches head_commit == HEAD and checks digests against the dirt those
    records describe; `--record` validates against the record's own
    commit. Known edge (accepted): a pre-first-commit working-tree record
    is not found by CI (adoption-phase pass), never a landmine.
  - F2 (blocker): §1a had replaced the unconditional "exact commands +
    key results" criterion with the record mechanism while §1f said the
    record was optional, and claimed the lint checks commands "ran".
    Restored the criterion; one merged row now states the adoption-phase
    status AND the honest limitation: the lint re-derives DECLARED exit
    codes and cannot detect omissions (this is also F4's disposition —
    a path-class map for omission detection is future work, recorded).
  - F3 (blocker): malformed records failed OPEN (non-list cited_runs,
    entry without artifact => silent pass). Schema is now type-aware,
    path entries reject absolute/`..` (also F19), and a triggered entry
    with no artifact is a finding.
  - F5: a recorded failing command is now always a finding — a passing
    `make verify` cannot launder an honest recorded failure. F6: the
    FIRST decision token decides `contract-not-submit`, and the unfilled
    `submit / no-submit` template is a finding. F8: `not_run` worker runs
    are citable exactly when the citing record's own gate_decision is
    submit (18/53 accepted ledger runs are supervisor-gated workers —
    the review showed the strict rule made the dogfood record impossible
    to write honestly). F9: artifacts and digests now resolve against the
    same state. F11: ALL in-range candidates are evaluated — a clean
    record cannot shadow a dirty sibling. F12: duplicate ledger run_ids
    are findings (`cited-run:duplicate`).
  - F10: the behavior-eval README's causal story for the 9/10 fragment
    was not supported by the diff (the reviewer showed `scope`
    occurrences went UP and the echoed line was unchanged); rewritten as
    single-sample variance with the evidence, n=1 noted.
  - F16: the stale positional check_structure invocation swept from four
    more skills. F15: the registry re-sort in the nfr-gate-report edit is
    hereby disclosed (semantic diff: one addition, zero changes). F14
    (deferred): the porcelain-z parser now has four copies — one shared
    helper is registered as follow-up. F17 (accepted): an honest
    no-submit record fails make lint only until the next commit moves
    HEAD — a small, intentional window. F18 (not actioned): --ledger
    outside the repo root stays an error.
  - Structure budget forced two honest splits during the fix:
    `scripts/submission_checks.py` (check functions) out of
    lint_submission.py, and `tests/test_lint_submission_modes.py` (mode/
    selection tests) out of the check-unit tests.
  After fixes: 376 tests OK; all lints, artifact lint, context budget,
  and `make verify` green; adoption-phase pass on this tree.
- 2026-07-26 (dogfood caught the last hole): CI failed on a fixture
  branch-name assumption (runners default to master; pinned `-b main`),
  and recording a second submission for that fix made the lint stale the
  FIRST record — range mode was validating every candidate against the
  range head instead of its own commit, reproducing F1's landmine inside
  one branch. Fixed: range-mode candidates each validate against their
  OWN head_commit (regression test: record → fix-commit → record stays
  green). Both dogfood records (33a7b30c, 434ffe5f) now validate as the
  range's two candidates. 377 tests OK.
