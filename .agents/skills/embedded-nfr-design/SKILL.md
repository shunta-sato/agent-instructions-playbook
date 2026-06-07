---
name: embedded-nfr-design
description: "Use before implementing embedded, edge, target-local, daemon, logger, recorder, collector, sampler, polling-loop, or resource-sensitive always-on behavior to define physical NFR budgets and measurement claims. Do not use for generic backend, web, or schema-only work with no target-local physical footprint."
metadata:
  short-description: Embedded physical NFR design
---

## Purpose

Use this skill to turn embedded physical-footprint risk into a concrete contract before implementation.

It answers one question:

**What CPU, memory, wakeup, battery, flash, thermal, latency, degradation, and observer-overhead limits must this feature satisfy, and what evidence is allowed to support those claims?**

## When to use

Use this skill when a change adds or modifies:

- embedded, edge, target-local, firmware-adjacent, robot-local, or device-local runtime behavior
- daemon, service, logger, recorder, collector, sampler, tracer, watcher, polling loop, or background task
- sampling interval, polling cadence, target-local filesystem write, network/radio background use, or resource claim
- product language such as "low overhead", "battery safe", "lightweight", "background safe", or "production ready" for target-local runtime behavior

Do not use it for generic backend APIs, web UI, schema-only work, pure docs, or pure parser/data-structure changes unless the prompt or code path states a target-local physical-footprint constraint.

## How to use

0) Open `references/embedded-nfr-taxonomy.md` and only the templates needed for the feature.

1. Define target-class assumptions:
   - target class and operating mode
   - power source assumptions
   - default, burst, and degraded modes
   - unavailable measurement surfaces

2. Create an Embedded NFR Matrix using `templates/nfr-matrix.md`.
   Include CPU, wakeups, memory, hot-path allocation, storage writes, flash wear, battery, network/radio, thermal, latency/jitter, degradation, and observer overhead when relevant.

3. Create or update physical budgets using `templates/physical-budgets.yaml`.
   Use explicit unknown or experimental values when a budget cannot be measured yet.

4. Separate steady-state from burst behavior.
   Default mode must be conservative; high-frequency behavior needs a bounded burst or experimental-only status.

5. Define the degraded-mode policy.
   Include battery_low, memory_pressure, thermal_pressure, storage_pressure, and measurement_unavailable decisions where relevant.

6. Define the measurement plan.
   Route to `embedded-nfr-harness-design` when budgets need a harness or target smoke command.

7. Record the no-measurement-no-claim list.
   Claims such as "low overhead" or "battery safe" require measurement evidence or must be removed/limited.

8. Record handoffs:
   - `embedded-hot-path-review` for loops, samplers, polling, collectors, recorders, or high-frequency paths
   - `embedded-observer-effect-review` for target-local logging, recording, tracing, or profiling
   - `architecture-decision-analysis` when multiple structure options trade off physical NFRs
   - `observability` when runtime diagnostic signals are added
   - `embedded-nfr-gate` before final submit readiness

## Outputs

Produce or update:

- `docs/nfr/<feature>.md` with Embedded NFR Matrix, assumptions, degraded-mode policy, measurement plan, and no-claim list
- `requirements/nfr/<feature>.yaml` or equivalent physical budget file

## Gotchas

- **Common pitfall:** treating battery unknown as AC power.
  **Instead:** record `battery_power_state: unknown` and limit production claims until measured or explicitly experimental.
- **Common pitfall:** allowing a short sampling interval because tests pass.
  **Instead:** classify it as default, burst, or experimental and give it a budget plus measurement.
- **Common pitfall:** saying "low overhead" without evidence.
  **Instead:** add it to the no-measurement-no-claim list or remove the claim.
