---
name: hardening-workflow
description: "Use for delivery-mode tasks whose purpose is quality improvement on shipped code: closing high-risk coverage gaps, structure-budget findings, flaky tests, missing observability, or smell density on a named path. Sequences a measured baseline, risk-tiered targets, and a stop at the policy ceiling. Do not use for tests written alongside new feature behavior, or embedded NFR budget work (embedded-nfr-design)."
metadata:
  short-description: Measure-tier-stop hardening lane
  requires:
    - references/hardening-workflow.md
---

## Purpose

Use this skill as the lane for delivery-mode tasks whose purpose is quality
improvement, not new capability: the code's contracts do not change, only its
tested-ness, structure, diagnosability, or measured performance. It is a thin
composition layer over existing parts, and its defining discipline is stopping —
gold-plating (uniform coverage push, over-hardening low-risk areas) is the
failure mode this lane exists to prevent.

## When to use

Use when the task's declared intent (`dev-workflow` step 1a) is `hardening`: the
work targets one declared quality dimension (test coverage of high-risk code,
structure-budget findings, flaky count, missing observability, smell density, or
performance of a named path) on code whose behavior is not intentionally changing.

Do not use for:
- tests written alongside new feature behavior — those belong to the feature's own
  `$unit-test-design` work, not this lane.
- embedded physical-footprint NFR budget work — that belongs to `$embedded-nfr-design`
  and the embedded NFR skill family.

## How to use

0) Record `intent: hardening`, the target quality dimension, and its metric (for
   example: changed-code branch coverage, `check_structure.py` finding count, flaky
   test count, missing signal count, smell count, or a named path's latency/throughput).

1) Measure the baseline before changing anything, with the repo's own tools: a
   coverage report, `python scripts/check_structure.py`, the flaky-test list, or a
   smell sweep (`$code-smells-and-antipatterns`). No baseline means no hardening claim
   can be made later — record the command and its result.

2) Tier the candidate targets with `$unit-test-design`'s E/S/H risk tiers (cite the
   tier and its one-line justification, do not restate the risk formula) and work
   highest-risk-first. E-tier targets are explicitly excluded from this lane — that
   exclusion is the point of the E tier, not an oversight.

3) Execute each tiered target through the one part-skill that owns it:
   - missing tests → `$unit-test-design` (+ `$working-with-legacy-code` characterization
     semantics when the target is legacy code)
   - missing signals → `$observability`
   - structure-budget findings → `$project-structure`
   - coupling/smells → `$code-smells-and-antipatterns`
   - hot paths → `$performance-review`
   - if code must be restructured before it becomes testable, that restructuring step
     follows `$refactor-workflow`'s lock-first discipline (cite it, do not redo it here)

4) Record before/after evidence: the metric delta from stage 1's baseline to the
   post-work measurement, plus a statement that behavior is preserved (suite green;
   hardening adds verification/diagnosability, it does not change contracts).

5) Stop at the policy ceiling owned by `$unit-test-design`
   (`references/unit-test-operations.md` §Coverage — cite it, do not restate the
   numbers): changed-code targets, the overall guide and healthy range, no
   normal-tier pushes toward full coverage, no blanket-hardening of E-tier
   targets. Flaky fixes follow that reference's same-day-or-quarantine rule.
   Hardening work that produced no measured delta is gold-plating — the stop
   criteria apply to quality work exactly as they apply to test cases.

## Output expectation

- dimension + metric: the declared quality dimension and how it is measured
- baseline: command + result, recorded before any change
- tiered target list: each target with its E/S/H tier and one-line justification
- per-target part-skill: which owning skill executed each target and its outcome
- after-metric delta: baseline value vs. post-work value, with the measurement command
- stop-criterion statement: which policy-ceiling rule ended the work (ceiling reached,
  E-tier excluded, or no further measured delta available)
