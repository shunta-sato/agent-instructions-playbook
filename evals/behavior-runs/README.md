# Behavior eval runs

Results from `scripts/run_behavior_eval.py` (build → run subjects → grade →
report; protocol mirrors `evals/routing-runs/RUNBOOK.md` with per-case packs and
plain-text responses). Naming: `<date>-<variant>-<model>.json`.

## First measurement (2026-07-25, commit a10a3ab, 9 isolated Sonnet subjects)

Decision accuracy 100% (6/6 quality-gate cases: all four delegated-run
no-submit/submit calls and both NFR-claim calls correct). Output-contains 100%
(9/9 cases, 30/30 fragments: tier letters, both boundary-value sets, the
exactly-once transfer contract, stop-criteria language). Findings ratio 35.7% —
informational only; the quality-gate seed cases carry sentence-length finding
phrases that rarely match free-form wording (known grader weakness; calibrate to
short fragments as cases are touched, as the unit-test-design cases already are).

Case-design lesson recorded honestly: the first version of the unit-test-design
cases set `expected_decision` on a skill that has no decision-marker output,
mis-scoring 3 correct responses; the schema now makes `expected_decision`
optional and the accuracy denominator counts only cases that declare it. The
responses were never regenerated — only the bookkeeping was fixed.
