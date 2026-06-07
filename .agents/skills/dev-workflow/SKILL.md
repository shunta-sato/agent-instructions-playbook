---
name: dev-workflow
description: "MANDATORY routing workflow for any code/test change: classify risk and execute only the required triggered branches, then hand off to quality-gate."
metadata:
  short-description: Risk-routed dev workflow
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

2) Apply **required trigger-based branches** only when facts trigger them.
   - bug/regression/flaky/crash/hang → `$bug-investigation-and-rca`
   - cross-boundary architecture/technology option comparison with measurable quality drivers → `$architecture-decision-analysis`
   - generic structural maintainability/boundary review → `$code-smells-and-antipatterns`
   - function/helper/API/call-site boundary design change → `$function-boundary-governor`
   - replacing flawed abstraction with temporary red-state migration → `$destructive-refactor`
   - concurrency/parallelism change → `$concurrency-core` + `$thread-safety-tooling` (+ variant skills)
   - runtime behavior change → `$observability`
   - embedded/edge/target-local runtime, daemon, logger, recorder, collector, sampler, polling, or resource-sensitive always-on behavior → route by the embedded NFR table below
   - strict-constraint low-level code or repeated compile/test loops → `$staged-lowering`
   - legacy/no reliable tests/nondeterminism → `$working-with-legacy-code`
   - UI change → `$visual-regression-testing` + matching platform visual skill(s)
   - C++ headers touched → `$code-readability` (Doxygen gate)

3) Apply routing priority to avoid overlap:
   - If the task requires choosing among cross-boundary architecture or technology options with measurable quality drivers, run `$architecture-decision-analysis` before implementation. Route to `$requirements-engineering` first if the quality drivers or requirements are too vague to measure.
   - If embedded physical-footprint NFRs are present, first route missing target context, unknown envelope behavior, and budget provenance gaps to characterization, envelope discovery, and calibration as applicable; then run `$embedded-nfr-design` before implementation. Route to `$architecture-decision-analysis` only when multiple cross-boundary architecture options must be compared.
   - If the primary question is function boundary/helper/API shape/side-effect placement/call-site migration, run `$function-boundary-governor` first.
   - Add `$code-smells-and-antipatterns` only when module-layer dependencies/coupling/architecture boundaries/adapters are also changing.

Embedded NFR routing table:

| Skill | Trigger |
| --- | --- |
| `$embedded-target-characterization` | If target profile, normal workload, measurement surface, resource headroom, or physical budget provenance is missing. |
| `$embedded-operating-envelope-discovery` | If normal, near-boundary, degraded, failure-adjacent, recovery, or telemetry blackout behavior is unknown. |
| `$embedded-nfr-calibration` | If budget values are being set or revised from target characterization, baselines, or operating envelope evidence. |
| `$embedded-nfr-design` | Always for embedded physical-footprint work after missing target context has been routed to characterization or explicitly marked unknown/provisional. |
| `$embedded-hot-path-review` | Only if loop, polling, sampling, collector, recorder, or hot-path behavior exists. |
| `$embedded-observer-effect-review` | Only if instrumentation or measurement can perturb workload. |
| `$embedded-nfr-harness-design` | Only if measurement or budget proof is needed. |
| `$embedded-nfr-gate` | Before final submit if feature-level embedded NFR work was triggered. |
| `$embedded-project-constitution` | Only for project bootstrap or a new embedded runtime class. |

4) Execute implementation with the selected route + required branches.

5) Run canonical verification at the depth required by the selected risk route.

6) Hand off to `$quality-gate` for final submission readiness.


## Gotchas

- **Common pitfall:** following optional skill lists after routing and blurring required-branch decisions.  
  **Instead:** maintain only-triggered branches as required and do not execute untriggered branches.
- **Common pitfall:** forcing low risk and bypassing required branches.  
  **Instead:** re-evaluate risk when API/behavior/UI/concurrency/boundary changes appear, and add required branches.
- **Common pitfall:** trying to make pass/fail decisions in dev-workflow.  
  **Instead:** limit dev-workflow to specifying required verification depth; delegate final judgment to `$quality-gate`.

## Output expectation

- Output must make the required route obvious:
  - selected risk and rationale
  - triggered required branches
  - verification depth to run before gate
- Final submit/no-submit judgment belongs to `$quality-gate`.
