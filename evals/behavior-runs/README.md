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

## failure-retrospective first measurement (2026-07-27, branch failure-retrospective-v1, 7 isolated Sonnet subjects)

All 7 new cases: decision-level behavior correct in every case — the
project-specific deterministic case paired local-lint with the wiki entry
instead of wiki-only; the cross-project confusion case absorbed into
quality-gate with shared enforcement and refused a new skill; productive
exploration closed no-durable-change without new gates; unclear causality
closed insufficient-evidence with a complete observe-first block; the
repeated+preventable+deterministic case REFUSED the proposed docs-only
close citing closure rules 5.1/5.2; the absorption case rejected
new-skill-candidate with a full 5.4 rationale; the final-attempt-success
case kept causal confidence at plausible. Output-contains 27/33: the six
missing fragments are vocabulary drift (e.g. "absorption is sufficient"
vs the seed's "absorbed", "Machine-Checkability" heading vs the seed's
"enforceability") — recorded as-is without editing expectations; they
join the findings-phrase calibration watchlist. Findings ratio 0/16 —
same known-weak grader as the MT2 run (sentence-length phrases rarely
match free-form wording).

Adversarial-review correction (F3): run 1's recorded `decision_accuracy:
1.0` was a ZERO-DENOMINATOR artifact — no case declared
`expected_decision`, so no decision was measured, and the narrative
"decision-level behavior correct" above rests on manual reading of the
responses, not on the grader. Fixed by adding a documented `Disposition:`
marker to the skill's Output expectation and `expected_decision` to all 7
seeds, then re-running fresh subjects: run 2
(`20260727-failure-retrospective-run2-sonnet-5.json`) measures decision
accuracy 7/7 on a real denominator. Output-contains stayed 27/33 with a
DIFFERENT missing-fragment set than run 1 — fragment misses rotate across
runs (vocabulary variance) while the decision tier is stable. Run 1's
responses were never rewritten; both runs are kept.
