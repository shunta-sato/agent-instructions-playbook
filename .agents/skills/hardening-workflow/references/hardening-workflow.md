# Hardening-workflow checklist

For `$hardening-workflow` only. Measure, tier, execute, delta, stop — in that order.
This lane's defining risk is gold-plating, not under-hardening: every stage below
exists to keep the work bounded to a measured, highest-risk-first scope.

## Stage table

| Stage | Action | Owning part-skill | Evidence produced |
| --- | --- | --- | --- |
| 0 | Declare dimension + metric | this skill | `intent: hardening` + dimension + metric |
| 1 | Measure baseline | repo tooling (coverage, `check_structure.py`, flaky list, smell sweep) | baseline command + result |
| 2 | Tier targets | `$unit-test-design` E/S/H | tiered target list, highest-risk-first |
| 3 | Execute per target | `$unit-test-design` / `$observability` / `$project-structure` / `$code-smells-and-antipatterns` / `$performance-review` / `$refactor-workflow` (if restructuring is needed first) | per-target outcome |
| 4 | Record delta | this skill | before/after metric + behavior-preserved statement |
| 5 | Stop at ceiling | `$unit-test-design` policy ceiling | stop-criterion statement |

## Stage 0 — declare dimension + metric

Record `intent: hardening` and exactly one target quality dimension with its metric.
Pick one of:

- test coverage of high-risk code (changed-code line/branch coverage)
- structure-budget findings (`check_structure.py` finding count)
- flaky test count
- missing observability (signal count against `$observability`'s checklist)
- smell density (`$code-smells-and-antipatterns` finding count)
- performance of a named path (latency/throughput on a stated path)

A hardening task with no declared dimension has no way to satisfy stage 5's stop rule.

## Stage 1 — measure the baseline (before any change)

Run the repo's own measurement tool for the declared dimension and record the exact
command and result:

- coverage report for the touched area
- `python scripts/check_structure.py <candidate files>`
- the current flaky-test list
- a smell sweep via `$code-smells-and-antipatterns`

No baseline, no hardening claim — stage 4's delta is meaningless without this anchor.

## Stage 2 — tier the targets

Classify every candidate target with `$unit-test-design`'s E/S/H risk formula (impact x
likelihood; cite the tier and a one-line justification, do not restate the formula
itself). Order work highest-risk-first (H before S before E).

E-tier targets are explicitly NOT hardened in this lane. That exclusion is the point of
the E tier — treating it as a todo list to clear anyway reintroduces gold-plating.

## Stage 3 — execute highest-risk-first, through the owning part

Route each tiered target to the one skill that owns it — do not perform the work
directly inside this skill:

- Missing or thin tests → `$unit-test-design`. On legacy code (no reliable tests,
  nondeterminism), apply `$working-with-legacy-code`'s characterization semantics first.
- Missing signals (logs/metrics/traces for diagnosability) → `$observability`.
- Structure-budget findings → `$project-structure`.
- Coupling/smell findings → `$code-smells-and-antipatterns`.
- Hot-path performance → `$performance-review`.
- If a target must be restructured before it becomes testable or measurable, that
  restructuring step follows `$refactor-workflow`'s stage 1 lock-first discipline (cite
  it; do not re-derive the lock-first rule here). The restructuring itself is still
  behavior-preserving — a hardening task that changes behavior has drifted into `feature`
  intent.

## Stage 4 — record before/after delta

For each executed target, record:
- the stage-1 baseline value
- the post-work measured value (same command/tool, re-run)
- a behavior-preserved statement: the suite is green, and hardening added
  verification/diagnosability without changing contracts

A target with no measured delta contributes nothing to the hardening claim and should
not be listed as done.

## Stage 5 — stop at the policy ceiling

Apply `$unit-test-design`'s stop criteria as this lane's ceiling. The numbers are
owned by that skill's `references/unit-test-operations.md` §Coverage — read the
current values there rather than from any copy. The ceiling covers:
- the changed-code line/branch targets (standard and high-risk)
- the overall guide value and healthy range
- the prohibition on pushing normal-tier areas toward full coverage
- the prohibition on blanket-hardening E-tier targets
- the same-day-or-quarantine flaky rule

Hardening that adds no measured delta is gold-plating regardless of effort spent — the
same stop discipline `$unit-test-design` applies to individual test cases applies here
to the whole hardening pass. Record which specific criterion ended the work.

## Handback

After stage 5, continue in `dev-workflow`: the structure watch
(`python scripts/check_structure.py <touched files>`), canonical verification at the
routed risk depth, and `$quality-gate`. This checklist's stage-4/5 output feeds the
gate's hardening-branch evidence bullet; it does not replace the gate's own decision.
