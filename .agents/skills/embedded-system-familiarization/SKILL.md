---
name: embedded-system-familiarization
description: "Use when embedded, edge, target-local, robot, Android, ROS 2, kernel/driver-adjacent, sensor, logger, recorder, or daemon work requires understanding target behavior, hardware capability, operating envelope, bottlenecks, or NFR provenance before design or optimization. Do not use for small changes with current characterization and no runtime/architecture impact."
metadata:
  short-description: Principal embedded system familiarization
---

## Purpose

Use this skill to orchestrate target learning, operating-envelope discovery, NFR calibration, hardware capability mapping, bottleneck/margin analysis, and architecture constraint formation before implementation or optimization.

It answers:

**What must we learn about this target so software can exploit hardware capability without violating physical budgets?**

## When to use

Use this skill when:

- starting or reshaping embedded, edge, robot-local, Android, ROS 2, kernel/driver-adjacent, sensor, recorder, logger, or target-local runtime work
- porting software to a new hardware target
- optimizing for battery, latency, throughput, thermal, memory, flash wear, wakeups, real-time behavior, or target-local observer overhead
- target normal behavior, degraded behavior, blackout behavior, hardware capability, workload envelope, bottleneck, margin, or NFR budget provenance is unknown
- architecture options depend on CPU, memory, I/O, accelerator, scheduler, thermal, battery, wakeup, or flash-write behavior
- the user asks how to use hardware capability efficiently without wasting target resources

Do not use it when:

- target characterization, operating envelope, calibrated NFRs, hardware capability map, and architecture constraints are current
- the task is a narrow calibration update with current characterization and envelope reports
- only a concrete sub-skill is explicitly requested and the broader target/system context is already known
- the change is pure docs, schema, parser, or non-target code
- the work is generic cloud/backend performance with no embedded physical footprint
- the user asks for a narrow fix with no target-learning, optimization, or architecture decision involved

## How to use

1. Establish the decision or feature that needs target understanding.
2. Inventory current artifacts:
   - target characterization
   - operating envelope
   - calibrated NFRs
   - hardware capability map
   - workload map
   - bottleneck/margin map
   - architecture constraints
3. Mark each artifact as `current`, `stale`, `missing`, `provisional`, or `deferred`, including freshness/revisit conditions.
4. Route to concrete skills as needed:
   - `embedded-project-constitution` for project bootstrap or a new embedded runtime class
   - `embedded-target-characterization` when target facts, normal workload, measurement surfaces, or baselines are missing
   - `embedded-operating-envelope-discovery` when normal, near-boundary, degraded, recovery, or blackout behavior is unknown
   - `embedded-nfr-calibration` when budgets need values or provenance
   - `embedded-nfr-design` when implementation constraints and no-claim rules must be set
   - `architecture-decision-analysis` when multiple architecture options trade off target constraints
   - `embedded-hot-path-review` when target-local loops, polling, sampling, collectors, or recorders exist
   - `embedded-observer-effect-review` when instrumentation or observation can perturb the workload
   - `embedded-nfr-harness-design` when measurement harnesses or target smoke commands are needed
   - `embedded-nfr-gate` before submit, then `quality-gate`
5. Produce a System Familiarization Pack using `templates/system-familiarization.md`.
6. Fill supporting maps when relevant:
   - `templates/workload-map.md`
   - `templates/hardware-capability-map.md`
   - `templates/bottleneck-margin-map.md`
   - `templates/architecture-constraints.md`
7. Define architecture constraints, forbidden claims, and claims blocked by missing evidence.
8. Hand off to concrete execution skills with `not_needed`, `required_pending`, `completed`, `deferred_with_reason`, or `blocked` status.

## Outputs

Produce or update:

- `docs/targets/<target>/system-familiarization.md`
- `docs/targets/<target>/target-characterization.md`
- `docs/targets/<target>/operating-envelope.md`
- `docs/targets/<target>/hardware-capability-map.md`
- `docs/targets/<target>/workload-map.md`
- `docs/targets/<target>/bottleneck-margin-map.md`
- `docs/targets/<target>/architecture-constraints.md`
- `target_profiles/<target>.yaml`
- `baselines/resource/<target>/idle.json`
- `baselines/resource/<target>/nominal_workload.json`
- `baselines/resource/<target>/near_boundary.json`
- `reports/target-characterization/<target>.json`
- `reports/operating-envelope/<target>/<scenario>.json`
- `reports/nfr-calibration/<feature>.md`
- `requirements/nfr/<feature>.yaml`
- `reports/resource/nfr-gate-report.md`

Not every artifact is required every time, but the pack must state which artifacts are required, current, missing, provisional, or deferred; why current evidence is still valid; when it must be revisited; and whether each handoff is complete, pending, deferred, blocked, or not needed.

## Rules

- Do not invent target capability.
- Do not optimize before target characterization or an explicit provisional target model.
- Do not finalize NFR budgets without calibration or explicit provisional/unknown status.
- Do not make architecture decisions on unknown target constraints.
- Do not claim hardware-efficient, low-overhead, battery-safe, flash-safe, thermally-safe, or production-ready without evidence.
- Host fallback is not target proof.
- Unknown is not pass.

## Gotchas

- **Common pitfall:** using this skill for every embedded task.
  **Instead:** use it only when broad target learning, hardware capability, bottlenecks, or architecture constraints are unknown.
- **Common pitfall:** duplicating detailed target characterization inside this skill.
  **Instead:** record orchestration status, then route to `embedded-target-characterization` for concrete target facts and baselines.
- **Common pitfall:** choosing an architecture because it is faster on the host.
  **Instead:** require target evidence or mark the decision provisional.
- **Common pitfall:** treating available margin as permission for default waste.
  **Instead:** map the software lever, budget, evidence, and degraded-mode impact before exploiting margin.
