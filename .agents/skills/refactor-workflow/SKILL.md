---
name: refactor-workflow
description: "Use for delivery-mode tasks whose purpose is structural change with no intended behavior change: extracting, moving, or renaming code, replacing a flawed abstraction, or consolidating duplication. Sequences a behavior lock, the owning structural-change skill, and equivalence evidence. Do not use for behavior-changing feature work, or the in-feature preparatory-refactor step, which stays in dev-workflow step 2b."
metadata:
  short-description: Behavior-preserving refactor lane
  requires:
    - references/refactor-workflow.md
---

## Purpose

Use this skill as the lane for delivery-mode tasks whose purpose is structural change: the code's externally observable behavior must not change, only its internal shape. It is a thin composition layer over existing parts — it does not own any new mechanism, and it does not replace `dev-workflow`'s gates. `dev-workflow` routes here by declared intent; this lane hands the task back to `dev-workflow`/`$quality-gate` to close.

## When to use

Use when the task's declared intent (`dev-workflow` step 1a) is `refactor`: extracting/moving/renaming code, replacing a flawed abstraction, consolidating duplication, or improving physical layout, with no intended behavior change.

Do not use for:
- behavior-changing feature work (intent `feature`) — any intentional behavior change belongs there, not here.
- the in-feature preparatory-refactor step done to make a feature change easy first — that stays in `dev-workflow` step 2b.

## How to use

0) Record `intent: refactor` and the compat-mode. Compat-mode semantics (`preserve` / `staged` / `break-allowed`) are owned by `dev-workflow` step 1b — cite the recorded value here, do not restate its definitions.

1) Lock behavior before any structural edit: run the full suite and record it green as the baseline. If tests for the touched area are unreliable, slow, or absent, stop and add characterization tests first via `$working-with-legacy-code`; size those tests with `$unit-test-design`'s E/S/H tiers (cite the tier, do not restate the risk formula).

2) Make the structural change through the one owning part-skill for its scope — do not improvise a mechanism this skill does not own:
   - function/API-level shape → `$function-boundary-governor`
   - module/class responsibility → `$design-balance`
   - temporary red-state migration replacing a flawed abstraction → `$destructive-refactor` (under refactor intent its intentional-behavior-change allowance is unavailable — behavior preservation stays mandatory, and its "add/update tests" step is limited to keeping migrated call sites green)
   - physical file/module layout → `$project-structure`
   New tests are not written for moved-but-unchanged behavior — the stage-1 lock is the equivalence evidence for that code. `$implementation-economy` still applies to any new abstraction the refactor introduces.

3) Close with equivalence evidence: pre-existing tests are unchanged and green; test edits are allowed only for renamed/moved symbols, and each such edit is listed by file and symbol; no new public behavior was introduced; under compat-mode `break-allowed`, the `check_api_removal.py` sweep (see `$destructive-refactor`) returns zero hits.

4) Name anti-patterns before calling the task done: a "refactor" that changes behavior is a mislabeled feature change; deleting a failing test to reach green is forbidden; skipping the stage-1 lock because "the change is obviously safe" is forbidden; a big-bang rewrite where `$destructive-refactor`'s staged migration fits is a scope error.

5) Continue into `dev-workflow`'s remaining steps (structure watch, verification, `$quality-gate`) — this lane supplies evidence for the gate's refactor bullet, it does not substitute for the gate.

## Output expectation

- compat-mode: `preserve` | `staged` | `break-allowed` (cited from `dev-workflow` step 1b)
- lock evidence: baseline suite command + result, or characterization tests added (cite `$working-with-legacy-code` output and the `$unit-test-design` tier used)
- stage list: which owning part-skill ran for the structural change and its decision
- equivalence evidence: pre-existing tests unchanged-and-green status; no-new-public-behavior statement; `break-allowed` sweep result when applicable
- any listed test edits: file + symbol + reason (renamed/moved only)
