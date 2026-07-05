---
name: embedded-system-familiarization
description: "Use when embedded, edge, target-local, robot, Android, ROS 2, kernel/driver-adjacent, sensor, logger, recorder, or daemon work requires understanding target behavior, hardware capability, operating envelope, bottlenecks, or NFR provenance before design or optimization. Do not use for small changes with current characterization and no runtime/architecture impact."
metadata:
  short-description: Principal embedded system familiarization
  requires:
    - templates/architecture-constraints.md
    - templates/bottleneck-margin-map.md
    - templates/capability-cost-model.md
    - templates/controlled-operating-points.md
    - templates/experiment-design-matrix.md
    - templates/hardware-capability-map.md
    - templates/hardware-control-surface-map.md
    - templates/system-familiarization.md
    - templates/workload-map.md
---

## Purpose

Use this skill to orchestrate target learning, operating-envelope discovery, NFR calibration, hardware capability mapping, control-surface discovery, operating point experiment planning, bottleneck/margin analysis, and architecture constraint formation before implementation or optimization.

It answers:

**What must we learn about this target so software can exploit hardware capability without violating physical budgets?**

## When to use

Use this skill when:

- starting or reshaping embedded, edge, robot-local, Android, ROS 2, kernel/driver-adjacent, sensor, recorder, logger, or target-local runtime work
- porting software to a new hardware target
- optimizing for battery, latency, throughput, thermal, memory, flash wear, wakeups, real-time behavior, or target-local observer overhead
- target normal behavior, degraded behavior, blackout behavior, hardware capability, workload envelope, bottleneck, margin, or NFR budget provenance is unknown
- architecture options depend on CPU, memory, I/O, accelerator, scheduler, thermal, battery, wakeup, or flash-write behavior
- an architecture or NFR claim depends on CPU frequency, CPU governor, core affinity, online cores, thermal state, power mode, workload level, accelerator availability, or another hardware operating point
- the user asks how to use hardware capability efficiently without wasting target resources

Do not use it when:

- target characterization, operating envelope, calibrated NFRs, hardware capability map, and architecture constraints are current
- the task is a narrow calibration update with current characterization and envelope reports
- only a concrete sub-skill is explicitly requested and the broader target/system context is already known
- the change is pure docs, schema, parser, or non-target code
- the work is generic cloud/backend performance with no embedded physical footprint
- the user asks for a narrow fix with no target-learning, optimization, or architecture decision involved
- the work is a host-side CLI, batch tool, server, or ordinary daemon with no physical target constraint (battery/power budget, thermal limit, flash-wear limit, real-time deadline, constrained target CPU/RAM, or a physically separate target device); logger/recorder/collector/sampler/polling vocabulary alone does not make work embedded, and when in doubt with no physical constraint named, use the general skills (`$performance-review`, `$observability`) instead

## How to use

1. Establish the decision or feature that needs target understanding.
2. Inventory current artifacts:
   - target characterization
   - operating envelope
   - calibrated NFRs
   - hardware capability map
   - hardware control surface map
   - controlled operating points
   - experiment design matrix
   - capability cost model
   - workload map
   - bottleneck/margin map
   - architecture constraints
3. Mark each artifact as `current`, `stale`, `missing`, `provisional`, or `deferred`, including freshness/revisit conditions.
4. Separate evidence types before making claims:
   - `observed natural variation`: values changed under normal policies or uncontrolled workload conditions
   - `controlled operating point`: values were intentionally set, verified, measured, and restored safely
   - `given conditions`: fixed context that was not varied in the experiment
   - `observed covariates`: measured variables that were not controlled
   - `uncontrolled confounders`: variables not controlled or sufficiently observed; these limit claims
5. Classify hardware and workload factors as `controlled_factor`, `observed_covariate`, or `uncontrolled_confounder`.
   Include CPU governor/frequency, core affinity, online cores, thermal state, power mode, workload level, and any GPU/NPU/DSP/I/O capability relevant to the decision.
6. Map control surfaces using `templates/hardware-control-surface-map.md`.
   For each control action record precondition, control command or method, verification command, abort condition, restore command or method, restore verification, privilege need, reversibility, and operator approval need.
   Mark unsupported or unsafe factors as `not_controllable`, `read_only_observable`, `control_requires_privilege`, `control_unsafe`, or `control_not_supported`.
   For cross-host workflows, also record deployment/runtime discovery compatibility: installer output path, runtime invocation path, non-interactive SSH `PATH`, target runner path, controller env override, target-local `PATH`, helper path, version identity, and the distinction between unsupported, missing, and PATH-missing diagnostics.
7. Plan operating point coverage using `templates/controlled-operating-points.md`.
   Use coverage statuses `not_started`, `observational_only`, `partially_controlled`, `controlled_subset`, `controlled_full`, `blocked_unsafe`, and `not_controllable`.
   Use confidence levels `none`, `low`, `medium`, and `high`; observed natural variation is at most `low`, controlled subset is typically `medium`, and repeated sweeps with thermal/power/workload conditions recorded can be `high`.
8. Use `templates/experiment-design-matrix.md` when a controlled benchmark or sweep is needed.
   Include repetitions, warmup seconds, cooldown seconds, run order, randomization, thermal precondition, thermal soak state, ambient condition, safety limits, setup verification, abort, and restore.
9. Use `templates/capability-cost-model.md` when hardware capability influences architecture.
   Hardware presence is not enough; require control surface, API/runtime path, transfer/setup/scheduling cost, workload fit, power/thermal cost, benchmark evidence, and fallback implications.
10. Route to concrete skills as needed:
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
11. Produce a System Familiarization Pack using `templates/system-familiarization.md`.
12. Fill supporting maps when relevant:
   - `templates/workload-map.md`
   - `templates/hardware-capability-map.md`
   - `templates/hardware-control-surface-map.md`
   - `templates/controlled-operating-points.md`
   - `templates/experiment-design-matrix.md`
   - `templates/capability-cost-model.md`
   - `templates/bottleneck-margin-map.md`
   - `templates/architecture-constraints.md`
13. Define architecture constraints, claim-to-evidence traces, allowed wording, forbidden claims, and claims blocked by missing evidence.
    Architecture decisions cannot rely on unswept operating points or unknown cost models except as explicit provisional assumptions.
14. When handing off to `architecture-decision-analysis`, include an architecture evidence packet summarizing hardware/control surface status, operating point coverage, cost model status, benchmark evidence, confounders, provisional assumptions, blocked claims, and verification tasks.
15. Hand off to concrete execution skills with `not_needed`, `required_pending`, `completed`, `deferred_with_reason`, or `blocked` status.

## Output expectation

Produce or update:

- `docs/targets/<target>/system-familiarization.md`
- `docs/targets/<target>/target-characterization.md`
- `docs/targets/<target>/operating-envelope.md`
- `docs/targets/<target>/hardware-capability-map.md`
- `docs/targets/<target>/hardware-control-surface-map.md`
- `docs/targets/<target>/controlled-operating-points.md`
- `docs/targets/<target>/experiment-design-matrix.md`
- `docs/targets/<target>/capability-cost-model.md`
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
- Do not treat observed natural variation as a controlled operating point sweep.
- Do not count CPU frequency observed under `ondemand`, `schedutil`, or another dynamic policy as a fixed-frequency sweep unless the frequency was intentionally controlled, verified, and restored.
- Do not optimize before target characterization or an explicit provisional target model.
- Do not finalize NFR budgets without calibration or explicit provisional/unknown status.
- Do not make architecture decisions on unknown target constraints.
- Do not make architecture decisions from unswept operating points, unknown control surfaces, or unknown capability cost models unless the decision is marked provisional and verification tasks are recorded.
- Do not claim hardware-efficient, low-overhead, battery-safe, flash-safe, thermally-safe, or production-ready without evidence.
- Do not claim "works at all CPU clocks", "battery safe", "GPU offload is better", or "low overhead across frequency range" unless the claim-to-evidence trace points to controlled operating point experiments and an adequate cost model where relevant.
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
- **Common pitfall:** treating `scaling_cur_freq` variation under a dynamic governor as a CPU clock sweep.
  **Instead:** call it observational-only evidence and plan fixed operating points with setup, verification, abort, and restore.
- **Common pitfall:** treating a listed GPU/NPU/DSP as proof that offload is better.
  **Instead:** require API/control surface evidence, transfer/setup cost, workload fit, power/thermal cost, and target benchmark evidence.
