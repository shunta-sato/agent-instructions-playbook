# Routing A/B: failure-retrospective introduction (2026-07-27)

Variants: before = main b66c946 (212 cases, 12 batches, surface 68,282
chars); after = branch failure-retrospective-v1 (223 cases — 212 common +
11 new failure-retrospective trigger cases — 13 batches, surface 68,829
chars, +0.8%). Subjects: isolated Sonnet 5, one per batch, canonical
RUNBOOK instruction, no expectation leak. Two full after-side samples were
taken for the six batches involved in run-1 regressions.

## Results

| Metric (common 212)         | before | after run1 | after run2 |
|-----------------------------|--------|------------|------------|
| should-trigger recall       | 258/290 = 88.97% | 243/290 = 83.79% | 258/290 = 88.97% |
| should-not-trigger compliance | 357/362 = 98.62% | 355/362 = 98.07% | 356/362 = 98.34% |
| mean co-fire                | 3.349  | 3.024      | 3.274      |

New failure-retrospective cases (after only): recall 9/9 = 100%,
compliance 23/24 = 95.8% (the one violation is a quality-gate co-fire on
the typo-one-line-fix negative — not a failure-retrospective firing).
failure-retrospective fired on ZERO of the 212 common cases in both after
runs: no co-fire pollution, no boundary leakage into bug-RCA /
research-synthesis / branch-completion cases.

## Adjudication of the run-1 dip (corrected by adversarial review)

Run 1's −5.2pt recall was investigated before any repair. The initial
"repacking" explanation was WRONG and is retracted: at batch size 18 the
10-case regression cluster sits in a batch whose composition is
byte-identical before vs after (the 11 new cases insert later in the
corpus), so repacking cannot explain it — only per-subject interpretation
variance or the +547-char surface can. What the evidence does support:
(1) failure-retrospective was selected on ZERO of the 212 common cases in
BOTH after runs — the new skill cannot be crowding anything out; (2) the
misses concentrate in skill families this diff never touched (embedded
chains, function-boundary-governor, project-structure), all pre-existing
watchlist items; (3) re-running the six affected batches with fresh
subjects recovered 11/16 misses and returned aggregate recall to the
before value. Caveat disclosed: only the losing batches were resampled
while the before side stayed n=1, so the exact-match recall is
best-of-two on the losing tail, not an unbiased estimate — the
decision-carrying evidence is the zero-fire result and the untouched-
family concentration, not the recovered aggregate. No expectation was
edited; no description/anti-trigger repair was warranted because no
regression is attributable to the change.

Confusion delta (should-not-trigger violations by skill, common cases):
after runs add `embedded-nfr-harness-design` +1 and `implementation-
economy` +1 versus before — single-case deltas in known-variance families
with no textual mechanism in this diff; recorded, not repaired.

Commit-field caveat: the after-side graded JSONs stamp the BASE commit
(b66c946) while measuring the dirty worktree whose surface is 547 chars
larger; per RUNBOOK §1 the recorded commit is untrustworthy for the after
files — identify them by filename, not by commit equality.

## Decisions taken on this measurement

- visibility=default is CONFIRMED for failure-retrospective (zero false
  fires, co-fire unchanged-to-better, surface +0.8%).
- The AGENTS.md wiki bootstrap line is NOT added: the A/B contains no
  signal on it, and the directive makes it measurement-gated.
