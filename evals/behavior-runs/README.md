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

## Wave-2 reduction re-measurement (2026-07-26, branch lint-migration-w2, 6 isolated Sonnet subjects)

Gate for the quality-gate reference reduction (`plans/20260726-submission-evidence.md`
adjudication 4). Decision accuracy 6/6 — identical to the baseline; the reduction
did not move any gate call. Output-contains 9/10: the one missing fragment is
`"scope"` on the scope-violation case. Single-sample variance (n=1 per case):
the diff gives no mechanism — the reference's `scope` occurrences went UP
(2→3) and the §3 line the subject echoed ("changed files exceed allowed
files") is unchanged by this change set and was equally available in the
baseline run that scored 10/10. Recorded as-is — the expectation was not
edited; the fragment sits on the existing findings-phrase calibration
watchlist. Only the six quality-gate cases were re-run (the reduction touched no
other skill's behavior surface).
