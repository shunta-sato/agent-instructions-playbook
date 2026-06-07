# Dev-workflow router template

This file is the routing template for `$dev-workflow`.
Focus on one question: **which branches are required for this task?**

## 0) Risk routing (mandatory first)

Classify first, then plan depth is decided automatically.

- **Low risk**: tiny/local; no API/schema/boundary/concurrency/UI/legacy/refactor trigger.
- **Normal risk**: default for most code/test changes.
- **High risk**: cross-boundary impact, runtime-behavior shift, broad refactor, strict constraints, safety/perf critical.

Embedded high-risk examples:

- target-local daemon, service, logger, recorder, collector, sampler, watcher, or background loop
- sub-100ms polling or sampling
- target-local filesystem writes, flash wear, wakeup, battery, thermal, or jitter impact
- resource-sensitive default behavior described as low overhead, battery safe, lightweight, or production ready

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
- cross-boundary architecture/technology option comparison with measurable quality drivers → `$architecture-decision-analysis`
- generic structural maintainability/boundary review → `$code-smells-and-antipatterns`
- function/helper/API/call-site design change → `$function-boundary-governor`
- replace flawed abstraction requiring temporary red-state migration → `$destructive-refactor`
- concurrency/parallelism change → `$concurrency-core` + `$thread-safety-tooling`
- ROS2 concurrency context → `$concurrency-ros2`
- Android concurrency context → `$concurrency-android`
- runtime behavior change → `$observability`
- embedded/edge/target-local work where target behavior, hardware capability, operating envelope, bottlenecks, or NFR provenance are not understood → `$embedded-system-familiarization`
- embedded/edge/target-local work with missing target profile, unknown normal workload, unknown measurement surfaces, unknown resource headroom, or guessed physical budget → `$embedded-target-characterization`
- embedded work where normal, near-boundary, degraded, failure-adjacent, recovery, or telemetry blackout behavior is unknown → `$embedded-operating-envelope-discovery`
- embedded work where physical budget values are being set or revised from target evidence → `$embedded-nfr-calibration`
- embedded/edge/target-local runtime, daemon, logger, recorder, collector, sampler, polling, or resource-sensitive always-on behavior → `$embedded-nfr-design`
- target-local loop/polling/sampling/collector/recorder hot path, sub-100ms cadence, per-iteration I/O, repeated serialization, or hot-path allocation → `$embedded-hot-path-review`
- target-local logging/recording/collection/tracing/profiling/measurement that can perturb scheduler, power, thermal, I/O, memory, wakeups, or workload → `$embedded-observer-effect-review`
- embedded physical budgets require measurement or a target smoke command → `$embedded-nfr-harness-design`
- feature-level embedded NFR design, harness, hot-path, or observer-effect branch was triggered → `$embedded-nfr-gate` before `$quality-gate`
- project bootstrap or new embedded runtime class without feature implementation → `$embedded-project-constitution`
- ambiguous requirements or explicit quality/NFR target → `$requirements-engineering`
- strict-constraint/low-level synthesis OR repeated compile/test loops → `$staged-lowering`
- weak tests / nondeterminism / legacy refactor → `$working-with-legacy-code`
- C++ headers touched (`.h/.hpp/...`) → `$code-readability` (Doxygen)
- UI changes → `$visual-regression-testing` + matching platform reference

## 2) Route summary (handoff contract)

Fill this before implementation starts:

- Selected risk route:
- Required branches to execute:
- Required verification depth before gate:
- Non-triggered branches explicitly skipped:

### Embedded NFR routing table

Use this table to avoid opening all embedded NFR skills by default.

| Skill | Trigger |
| --- | --- |
| `$embedded-system-familiarization` | Broad target-learning, optimization, or architecture-shaping work where target behavior, hardware capability, workload envelope, bottlenecks, margins, or NFR provenance are not understood. |
| `$embedded-target-characterization` | If target profile, normal workload, measurement surface, resource headroom, or physical budget provenance is missing. |
| `$embedded-operating-envelope-discovery` | If normal, near-boundary, degraded, failure-adjacent, recovery, or telemetry blackout behavior is unknown. |
| `$embedded-nfr-calibration` | If budget values are being set or revised from target characterization, baselines, or operating envelope evidence. |
| `$embedded-nfr-design` | Always for embedded physical-footprint work after missing target context has been routed to characterization or explicitly marked unknown/provisional. |
| `$embedded-hot-path-review` | Only if loop, polling, sampling, collector, recorder, or hot-path behavior exists. |
| `$embedded-observer-effect-review` | Only if instrumentation or measurement can perturb workload. |
| `$embedded-nfr-harness-design` | Only if measurement or budget proof is needed. |
| `$embedded-nfr-gate` | Before final submit if feature-level embedded NFR work was triggered. |
| `$embedded-project-constitution` | Only for project bootstrap or a new embedded runtime class. |

Use `$embedded-system-familiarization` as an orchestrator for broad target-learning or optimization efforts. Use the specific embedded skills directly for narrow tasks with known target context.

## 3) Live external discovery (when applicable)

If the task touches external systems, repo tooling, CI, schemas/configs, or artifact-producing tools, discover current reality before trusting examples.

Record:
- Repo command/interface discovered (file, target, script, CI job, or help output):
- Current version/status output:
- Schema/config/connection state checked:
- Artifact/log/output paths expected:

## 4) Implementation + verify execution log (short)

- Branches executed:
- Verification commands executed:
- Live discovery evidence captured (or `not applicable`):
- Remaining known gaps before gate (if any):

## 5) Gate handoff (mandatory)

Always finish by invoking `$quality-gate`.
`$dev-workflow` does not decide final submit readiness; it hands off required evidence.
