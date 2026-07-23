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
- Intent (`feature` | `poc` | `refactor` | `hardening`) — full definitions and tie-breaks: §0a:
- Compat-mode (`preserve` | `staged` | `break-allowed`) when public/cross-module APIs are touched or the task is a rework/consolidation/deletion request; for `break-allowed`, quote the requester's waiver — full definitions: §0b:

### Required outputs by risk

| Area | Low | Normal | High |
|---|---|---|---|
| Change brief depth | compact | full | full |
| Requirements depth | minimal EARS + acceptance bullets | full EARS + acceptance | full EARS + acceptance + failure-path notes |
| Test planning | impacted tests list | Test List (3–10) | Test List (3–10) + explicit strategy |
| Default implementation lane | skip if one file, no new abstraction, public API unchanged, no behavior expansion | required | required |
| Complexity budget | optional only when new abstraction appears | `implementation-economy` budget + audit | `implementation-economy` budget + audit |
| Responsibility layout | optional only when module/class layout changes | `design-balance` map when layout changes | `design-balance` map when layout changes |
| Structure watch (`scripts/check_structure.py` on touched files) | required | required | required |
| Verification depth before gate | canonical minimum for changed surface | full canonical chain | full canonical chain |
| Final gate | `$quality-gate` required | `$quality-gate` required | `$quality-gate` required |
| ExecPlan | optional | required if complex | required if complex/long-running |

## 0a) Work intent

Declare the work-intent and record it like compat-mode: `feature` (default) | `poc` | `refactor` | `hardening`.

- `poc` (prototype/demo/feasibility construction): this is research-mode work — the PoC boundary must be a research-mode path or a declared research mode; route `$poc-workflow` and stop here (dev-workflow's remaining steps are delivery mandates). A PoC built on delivery paths in delivery mode gets no exemptions.
- `refactor` (structural change, behavior preserved as the task's purpose): run the `$refactor-workflow` lane; its stages call back into this skill's parts (1b compat-mode, `$function-boundary-governor`, `$design-balance`, `$destructive-refactor`). The lane subsumes step 2's default implementation lane — after it, resume at step 6; do not re-run 1a–2 and do not seed a Test List (the lane forbids new tests for moved-but-unchanged behavior). The in-feature preparatory refactor stays step 2b — do not reroute it.
- `hardening` (quality improvement of existing behavior as the task's purpose): run the `$hardening-workflow` lane. The lane subsumes step 2 — after it, resume at step 6; do not re-run 1a–2.
- `feature`: continue unchanged.
- Tie-break: intent is about the task's PURPOSE — a feature that happens to refactor en route stays `feature` (step 2b); a task whose deliverable IS the structural change or the quality delta takes the dedicated intent. Refactor-vs-hardening tie-break: a measured quality delta as the deliverable (coverage, smell count, flaky count, latency metric) → `hardening`; a specific structural transformation with no target metric → `refactor`; a behavior-preserving cleanup that names a measurable quality dimension defaults to `hardening` (the lanes gate differently — hardening requires a baseline).

## 0b) Compat-mode

Record the compat-mode whenever the task touches public or cross-module APIs, or is a rework/consolidation/deletion request:

- `preserve` (default): existing callers must keep working.
- `staged`: temporary adapters allowed, each with a ledger entry naming its removal condition.
- `break-allowed`: the requester explicitly waived backward compatibility — quote the waiver. Under `break-allowed`, delete rather than deprecate: old APIs, deprecated markers, re-export aliases, and parallel old/new versions are defects, not caution.

## 1) Default implementation lane

Run this lane before trigger branches for normal/high-risk implementation. For low risk, record the skip reason only when all are true: one file, no new abstraction, public API unchanged, no behavior expansion, and the structure watch passes on every touched source file.

1. Requirements/DoD: record the smallest acceptance criteria and Definition of Done.
2. Test List: seed from acceptance criteria when behavior can be tested; route to `$test-driven-development` when using Red/Green/Refactor.
3. Responsibility layout: run `$design-balance` when the change introduces 2+ classes/modules, adds a layer/interface, or adds a new reason-to-change to an existing class/module.
4. Complexity budget: run `$implementation-economy` for normal/high-risk work and for any new helper, wrapper, adapter, class, module, or indirection.
5. Lightweight readability check: check that touched names predict responsibilities; rename if a class/module/function name cannot be explained in one sentence.
6. Preparatory refactor check (make the change easy first): if the landing area has structure-budget findings, near-duplicate functions the feature would extend, or forces a boolean-flag/shotgun edit, do a scoped preparatory refactor as its own verified step (tests green before and after), then implement the feature.

Default lane output:
- Definition of Done / acceptance criteria:
- Prep-refactor: done | not-needed (one-line reason):
- Test List source or skip reason:
- Responsibility map path/summary or skip reason:
- Complexity budget + audit path/summary or skip reason:
- Naming/responsibility check result:

## 2) Required trigger branches (all risks)

Mark each line as `triggered` or `not triggered` with one-line evidence.

- new source file/module/crate/package created, test placement decision, or structure budget finding on a touched file → `$project-structure`
- explicit rework/rewrite/consolidation/simplification request, API deletion, or backward compatibility explicitly waived → record compat-mode (§0b), then `$function-boundary-governor` (function/API level) or `$design-balance` (module/class level); temporary red state needed → `$destructive-refactor`
- code or API with zero remaining callers → `$function-boundary-governor` (`delete` action)
- bug/regression/flaky/crash/hang → `$bug-investigation-and-rca`
- cross-boundary architecture/technology option comparison with measurable quality drivers (metric + target + measurement method all present) → `$architecture-decision-analysis`
- generic structural maintainability/boundary review → `$code-smells-and-antipatterns`
- module/class responsibility layout, new layer/interface, 2+ new classes/modules, or existing class/module gains a second reason-to-change → `$design-balance`
- normal/high-risk implementation or new abstraction/helper/wrapper/adapter/indirection → `$implementation-economy`
- non-embedded request/render/job path, input-proportional collection processing, loop I/O, N+1 query risk, repeated serialization/allocation, serial awaits, or cache/batching/pagination decisions → `$performance-review`
- function/helper/API/call-site design change → `$function-boundary-governor`
- replace flawed abstraction requiring temporary red-state migration → `$destructive-refactor`
- concurrency/parallelism change → `$concurrency-core` + `$thread-safety-tooling`
- ROS2 concurrency context → `$concurrency-ros2`
- Android concurrency context → `$concurrency-android`
- runtime behavior change (new/changed async or background work, external call, periodic job, user-visible operation, or retry/timeout/fallback path) → `$observability`
- embedded/edge/target-local work where target behavior, hardware capability, workload envelope, bottlenecks, margins, or NFR provenance are not understood → `$embedded-system-familiarization`
- embedded/edge/target-local runtime, daemon, logger, recorder, collector, sampler, polling, or resource-sensitive always-on behavior → route by the Embedded NFR routing table (§2a)
- ambiguous requirements or explicit quality/NFR target → `$requirements-engineering`
- strict-constraint/low-level synthesis OR repeated compile/test loops → `$staged-lowering`
- weak tests / nondeterminism / legacy refactor → `$working-with-legacy-code`
- unit tests being added, changed, or reviewed; deciding test cases, boundaries, coverage, or mock use → `$unit-test-design`
- C++ headers touched (`.h/.hpp/...`) → `$code-readability` (Doxygen)
- UI changes → `$visual-regression-testing` + matching platform reference
- adding or editing implementation comments, commit-message content decisions, or test names/descriptions → `$comment-discipline`

## 2a) Embedded NFR routing table

Use this table to avoid opening all embedded NFR skills by default.

| Skill | Trigger |
| --- | --- |
| `$embedded-system-familiarization` | Broad target-learning, optimization, or architecture-shaping work where target behavior, hardware capability, workload envelope, bottlenecks, margins, or NFR provenance are not understood. |
| `$embedded-target-characterization` | If target profile, normal workload, measurement surface, resource headroom, or physical budget provenance is missing. |
| `$embedded-operating-envelope-discovery` | If normal, near-boundary, degraded, failure-adjacent, recovery, or telemetry blackout behavior is unknown. |
| `$embedded-nfr-calibration` | If budget values are being set or revised from target characterization, baselines, or operating envelope evidence. |
| `$embedded-nfr-design` | Always for embedded physical-footprint work after missing target context has been routed to characterization or explicitly marked unknown/provisional. |
| `$embedded-hot-path-review` | Target-local loop/polling/sampling/collector/recorder hot path, sub-100ms cadence, per-iteration I/O, repeated serialization, or hot-path allocation. |
| `$embedded-observer-effect-review` | Target-local logging/recording/collection/tracing/profiling/measurement that can perturb scheduler, power, thermal, I/O, memory, wakeups, or workload. |
| `$embedded-nfr-harness-design` | Embedded physical budgets require measurement or a target smoke command. |
| `$embedded-nfr-gate` | Feature-level embedded NFR design, harness, hot-path, or observer-effect branch was triggered; route before `$quality-gate`. |
| `$embedded-project-constitution` | Project bootstrap or a new embedded runtime class, without feature implementation. |

Use `$embedded-system-familiarization` as an orchestrator for broad target-learning or optimization efforts. Use the specific embedded skills directly for narrow tasks with known target context.

The embedded table adds branches; it never replaces the general trigger branches in section 2 (an embedded daemon with changed runtime behavior still triggers `$observability`). Work is embedded only when a physical target constraint exists (battery/power, thermal, flash wear, real-time deadline, constrained target CPU/RAM, or a separate target device); logger/collector/polling vocabulary alone does not qualify.

## 2b) Routing precedence

Resolve overlaps with the routing precedence table. Walk the rows top-down; the **first matching row wins** and that skill runs before implementation. Later rows may still be triggered branches, but the winning row decides what runs first.

| # | The decision this task needs first is... | Route first |
|---|---|---|
| 1 | choosing among cross-boundary architecture or technology options — and every quality driver has metric + target + measurement method | `$architecture-decision-analysis` |
| 2 | same as row 1, but at least one quality driver lacks metric, target, or measurement method | `$requirements-engineering`, and only after that `$architecture-decision-analysis` |
| 3 | embedded physical-footprint NFRs that are broad, optimization-oriented, or architecture-shaping, and target behavior or hardware capability is not understood | `$embedded-system-familiarization` |
| 4 | embedded physical-footprint NFRs that are narrow | the specific embedded skills for missing target context (§2a Embedded NFR routing table), and after that `$embedded-nfr-design` |
| 5 | which module/class/layer owns a responsibility, naming, layer count, or reason-to-change split | `$design-balance` |
| 6 | function boundary, helper/API shape, side-effect placement, or call-site migration | `$function-boundary-governor` |
| 7 | too much code, extra helpers/wrappers, or premature generality | `$implementation-economy` |
| 8 | performance of target-local / embedded physical footprint | embedded NFR skills + `$embedded-hot-path-review` |
| 9 | performance of host/app request, render, or job paths | `$performance-review` |

Add `$code-smells-and-antipatterns` on top of any row only when module-layer dependencies, coupling, architecture boundaries, or adapters are also changing.

## 2c) Structure watch

Run the structure watch (all risks, including low): `python scripts/check_structure.py <touched source files>`.

- Any finding makes `$project-structure` required in this change: apply the split (layout), routing naming/ownership to `$design-balance` and function moves to `$function-boundary-governor`.
- This step is state-based on purpose: it fires on accumulated size even when this change added only a few lines.

## 3) Route summary (handoff contract)

Fill this before implementation starts:

- Selected risk route:
- Default lane executed or skipped:
- Required branches to execute:
- Required verification depth before gate:
- Non-triggered branches explicitly skipped:

## 4) Live external discovery (when applicable)

If the task touches external systems, repo tooling, CI, schemas/configs, or artifact-producing tools, discover current reality before trusting examples.

Record:
- Repo command/interface discovered (file, target, script, CI job, or help output):
- Current version/status output:
- Schema/config/connection state checked:
- Artifact/log/output paths expected:

## 5) Implementation + verify execution log (short)

- Default lane outputs:
- Branches executed:
- Structure watch result (`scripts/check_structure.py` on touched files; findings + applied splits, or pass):
- Verification commands executed:
- Live discovery evidence captured (or `not applicable`):
- Remaining known gaps before gate (if any):

## 6) Gate handoff (mandatory)

Always finish by invoking `$quality-gate`.
`$dev-workflow` does not decide final submit readiness; it hands off required evidence.

## Gotchas

- **Common pitfall:** following optional skill lists after routing and blurring required-branch decisions.
  **Instead:** maintain only-triggered branches as required and do not execute untriggered branches.
- **Common pitfall:** forcing low risk and bypassing required branches.
  **Instead:** re-evaluate risk when API/behavior/UI/concurrency/boundary changes appear, and add required branches.
- **Common pitfall:** treating each small append to one file as low risk forever, so no layout skill ever fires while the file becomes a monolith.
  **Instead:** the structure watch is mandatory at every risk level; a budget finding forces `$project-structure` regardless of how small this change is.
- **Common pitfall:** trying to make pass/fail decisions in dev-workflow.
  **Instead:** limit dev-workflow to specifying required verification depth; delegate final judgment to `$quality-gate`.
