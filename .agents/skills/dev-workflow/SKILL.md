---
name: dev-workflow
description: "Use for any task that changes code or tests. Routes implementation work by risk and applicable branch skills before editing."
metadata:
  short-description: Risk-routed dev workflow
  requires:
    - references/dev-workflow.md
---

## Purpose

This skill is the router for implementation work in this repository.

It decides **which branch workflows are required** for the current task.

## When to use

Use this skill **for any task that changes code and/or tests**. It is mandatory.

## How to use

0) Open `references/dev-workflow.md` and fill it top-down.

1) Route by risk first (`low` | `normal` | `high`) and record why.
   - The output of this step is: required planning depth + required verification depth.

2) Run the default implementation lane when required by risk:
   - `low`: skip the lane only when the change is one file, adds no abstraction, leaves public APIs unchanged, has no behavior expansion, and every touched source file stays within the structure budget (`python scripts/check_structure.py <touched files>` passes).
   - `normal` / `high`: define acceptance criteria, seed a Test List when behavior can be tested, run `implementation-economy`, and run `design-balance` when module/class responsibility layout changes.

3) Apply **required trigger-based branches** only when facts trigger them.
   - new source file/module/crate/package, test placement decision, or structure budget finding on a touched file → `$project-structure`
   - bug/regression/flaky/crash/hang → `$bug-investigation-and-rca`
   - cross-boundary architecture/technology option comparison with measurable quality drivers (metric + target + measurement method all present; definition in `$architecture-decision-analysis`) → `$architecture-decision-analysis`
   - generic structural maintainability/boundary review → `$code-smells-and-antipatterns`
   - module/class responsibility layout, new layer/interface, or 2+ new classes/modules → `$design-balance`
   - normal/high-risk implementation or new abstraction/helper/wrapper/adapter → `$implementation-economy`
   - non-embedded request/render/job paths, input-proportional loops, loop I/O, N+1 risk, repeated serialization/allocation, serial awaits, or cache/batching decisions → `$performance-review`
   - function/helper/API/call-site boundary design change → `$function-boundary-governor`
   - replacing flawed abstraction with temporary red-state migration → `$destructive-refactor`
   - concurrency/parallelism change → `$concurrency-core` + `$thread-safety-tooling` (+ variant skills)
   - runtime behavior change (new/changed async or background work, external call, periodic job, user-visible operation, or retry/timeout/fallback path) → `$observability`
   - embedded/edge/target-local work where target behavior, hardware capability, operating envelope, bottlenecks, or NFR provenance are not understood → `$embedded-system-familiarization`
   - embedded/edge/target-local runtime, daemon, logger, recorder, collector, sampler, polling, or resource-sensitive always-on behavior → route by the embedded NFR table below
   - strict-constraint low-level code or repeated compile/test loops → `$staged-lowering`
   - legacy/no reliable tests/nondeterminism → `$working-with-legacy-code`
   - UI change → `$visual-regression-testing` + matching platform visual skill(s)
   - C++ headers touched → `$code-readability` (Doxygen gate)

4) Resolve overlaps with the routing precedence table. Walk the rows top-down; the **first matching row wins** and that skill runs before implementation. Later rows may still be triggered branches, but the winning row decides what runs first.

| # | The decision this task needs first is... | Route first |
|---|---|---|
| 1 | choosing among cross-boundary architecture or technology options — and every quality driver has metric + target + measurement method | `$architecture-decision-analysis` |
| 2 | same as row 1, but at least one quality driver lacks metric, target, or measurement method | `$requirements-engineering`, and only after that `$architecture-decision-analysis` |
| 3 | embedded physical-footprint NFRs that are broad, optimization-oriented, or architecture-shaping, and target behavior or hardware capability is not understood | `$embedded-system-familiarization` |
| 4 | embedded physical-footprint NFRs that are narrow | the specific embedded skills for missing target context (table below), and after that `$embedded-nfr-design` |
| 5 | which module/class/layer owns a responsibility, naming, layer count, or reason-to-change split | `$design-balance` |
| 6 | function boundary, helper/API shape, side-effect placement, or call-site migration | `$function-boundary-governor` |
| 7 | too much code, extra helpers/wrappers, or premature generality | `$implementation-economy` |
| 8 | performance of target-local / embedded physical footprint | embedded NFR skills + `$embedded-hot-path-review` |
| 9 | performance of host/app request, render, or job paths | `$performance-review` |

   Add `$code-smells-and-antipatterns` on top of any row only when module-layer dependencies, coupling, architecture boundaries, or adapters are also changing.

Embedded NFR routing table:

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

The embedded table **adds** branches; it never replaces the general trigger branches in step 3. An embedded daemon whose runtime behavior changes still triggers `$observability`. Conversely, work is embedded only when a physical target constraint exists (battery/power, thermal, flash wear, real-time deadline, constrained target CPU/RAM, or a separate target device) — logger/collector/polling vocabulary alone does not qualify.

5) Execute implementation with the selected route + required branches.

6) Run the structure watch (all risks, including low): `python scripts/check_structure.py <touched source files>`.
   - Any finding makes `$project-structure` required in this change: apply the split (layout), routing naming/ownership to `$design-balance` and function moves to `$function-boundary-governor`.
   - This step is state-based on purpose: it fires on accumulated size even when this change added only a few lines.

7) Run canonical verification at the depth required by the selected risk route.

8) Hand off to `$quality-gate` for final submission readiness.


## Gotchas

- **Common pitfall:** following optional skill lists after routing and blurring required-branch decisions.
  **Instead:** maintain only-triggered branches as required and do not execute untriggered branches.
- **Common pitfall:** forcing low risk and bypassing required branches.
  **Instead:** re-evaluate risk when API/behavior/UI/concurrency/boundary changes appear, and add required branches.
- **Common pitfall:** treating each small append to one file as low risk forever, so no layout skill ever fires while the file becomes a monolith.
  **Instead:** the structure watch is mandatory at every risk level; a budget finding forces `$project-structure` regardless of how small this change is.
- **Common pitfall:** trying to make pass/fail decisions in dev-workflow.
  **Instead:** limit dev-workflow to specifying required verification depth; delegate final judgment to `$quality-gate`.

## Output expectation

- Output must make the required route obvious:
  - selected risk and rationale
  - triggered required branches
  - structure watch result (pass, or findings + applied splits)
  - verification depth to run before gate
- Final submit/no-submit judgment belongs to `$quality-gate`.
