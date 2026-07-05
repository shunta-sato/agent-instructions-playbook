---
name: embedded-nfr-harness-design
description: "Use after embedded physical budgets exist, or when an embedded daemon/logger/recorder/sampler needs resource, battery, wakeup, flash, thermal, latency, or observer-overhead measurement. Do not use for performance advice without a target-local physical footprint."
metadata:
  short-description: Embedded NFR harness design
  requires:
    - templates/resource-harness-plan.md
    - templates/resource-report.schema.json
    - templates/target-profile.yaml
---

## Purpose

Use this skill to convert embedded NFR budgets into measurement scenarios, target profiles, baseline files, report schemas, host fallback checks, and target smoke commands.

It answers one question:

**How will this feature prove or limit its physical-footprint claims?**

## When to use

Use this skill when:

- `embedded-nfr-design` produced physical budgets that need measurement
- a background loop, daemon, logger, recorder, sampler, collector, tracer, or watcher needs resource smoke evidence
- a claim about low overhead, battery safety, flash safety, thermal safety, wakeups, or jitter needs verification
- target evidence is not available yet and a host fallback plus explicit limitation is needed

Do not use it for generic benchmark planning, web performance tests, or code paths with no embedded/target-local physical constraint.

## How to use

1. Read the physical budgets from `docs/nfr/<feature>.md`, `requirements/nfr/<feature>.yaml`, or the equivalent artifact.
2. Classify the harness:
   - `discovery_harness`: used to understand target behavior and operating envelope
   - `gate_harness`: used to prove implementation satisfies budgets
3. Define target profiles using `templates/target-profile.yaml`.
4. Define measurement scenarios using `templates/resource-harness-plan.md`:
   - idle baseline
   - default steady state
   - bounded burst
   - degraded mode
   - observer-on vs observer-off when relevant
5. Define the report shape using `templates/resource-report.schema.json`.
   Include `budget_results` entries that pair each NFR budget with its measurement, unit, result, evidence path, and fail/unknown reason.
6. Add commands or command skeletons:
   - target smoke command
   - host fallback command
   - baseline capture command
   - report generation path
   For controller-target harnesses, also define the controller-side command, target-local command, target runner binary path, PATH/env assumptions, preflight command, artifact retrieval or include-run path, and the meaning of failures: install missing, PATH missing, version skew, unsupported surface, permission denied, or helper unavailable.
7. State what the harness cannot prove.
8. Route discovery work to `embedded-target-characterization` or `embedded-operating-envelope-discovery` when target envelope is unknown.
9. Route to `embedded-nfr-gate` once reports or explicit unknowns exist.

## Output expectation

Produce or update:

- `docs/testing/resource-harness.md`
- `target_profiles/<target-class>.yaml`
- `baselines/resource/*.json`
- `scripts/resource/run-resource-smoke.sh` or a project-equivalent command
- `reports/resource/<feature>.json` schema or sample location
- resource report `budget_results` that `embedded-nfr-gate` can compare directly

## Rules

- Do not use a gate harness as a substitute for target characterization when the target envelope is unknown.
- Discovery harness results can calibrate budgets; gate harness results prove budgets for a submitted implementation.

## Gotchas

- **Common pitfall:** using host-only results to claim target battery safety.
  **Instead:** label host fallback evidence as limited and keep target-only claims blocked.
- **Common pitfall:** measuring only burst behavior.
  **Instead:** include idle baseline and default steady-state scenarios.
- **Common pitfall:** measuring observer-on behavior only.
  **Instead:** add observer-on vs observer-off comparison when the observer can perturb workload.
