# Dev-workflow router template

This file is the routing template for `$dev-workflow`.
Focus on one question: **which branches are required for this task?**

## 0) Risk routing (mandatory first)

Classify first, then plan depth is decided automatically.

- **Low risk**: tiny/local; no API/schema/boundary/concurrency/UI/legacy/refactor trigger.
- **Normal risk**: default for most code/test changes.
- **High risk**: cross-boundary impact, runtime-behavior shift, broad refactor, strict constraints, safety/perf critical.

Record:
- Risk level:
- Why this level:
- Escalation trigger (what would raise risk):

### Required outputs by risk

| Area | Low | Normal | High |
|---|---|---|---|
| Change brief depth | compact | full | full |
| Requirements depth | minimal EARS + acceptance bullets | full EARS + acceptance | full EARS + acceptance + failure-path notes |
| Test planning | impacted tests list | Test List (3–10) | Test List (3–10) + explicit strategy |
| Verification depth before gate | canonical minimum for changed surface | full canonical chain | full canonical chain |
| Final gate | `$quality-gate` required | `$quality-gate` required | `$quality-gate` required |
| ExecPlan | optional | required if complex | required if complex/long-running |

## 1) Required trigger branches (all risks)

Mark each line as `triggered` or `not triggered` with one-line evidence.

- bug/regression/flaky/crash/hang → `$bug-investigation-and-rca`
- structural boundary/refactor change → `$code-smells-and-antipatterns`
- concurrency/parallelism change → `$concurrency-core` + `$thread-safety-tooling`
- ROS2 concurrency context → `$concurrency-ros2`
- Android concurrency context → `$concurrency-android`
- runtime behavior change → `$observability`
- explicit performance target → `$nfr-iso25010`
- strict-constraint/low-level synthesis OR repeated compile/test loops → `$staged-lowering`
- weak tests / nondeterminism / legacy refactor → `$working-with-legacy-code`
- C++ headers touched (`.h/.hpp/...`) → `$code-readability` (Doxygen)
- UI changes → `$visual-regression-testing` + platform visual skill(s)

## 2) Route summary (handoff contract)

Fill this before implementation starts:

- Selected risk route:
- Required branches to execute:
- Required verification depth before gate:
- Non-triggered branches explicitly skipped:

## 3) Implementation + verify execution log (short)

- Branches executed:
- Verification commands executed:
- Remaining known gaps before gate (if any):

## 4) Gate handoff (mandatory)

Always finish by invoking `$quality-gate`.
`$dev-workflow` does not decide final submit readiness; it hands off required evidence.
