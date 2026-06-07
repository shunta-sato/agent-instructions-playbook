---
name: embedded-operating-envelope-discovery
description: "Use to discover normal, near-boundary, degraded, failure-adjacent, and logging/telemetry blackout behavior for embedded targets before calibrating NFR budgets. Do not use for ordinary performance benchmarking without an embedded target envelope question."
metadata:
  short-description: Embedded operating envelope discovery
---

## Purpose

Use this skill to safely discover where a target operates normally, approaches a boundary, degrades, recovers, or loses telemetry.

It answers one question:

**What behavior range should NFR calibration consider safe, risky, degraded, or unavailable?**

## When to use

Use this skill when:

- normal vs abnormal target behavior is unknown
- the target changes gradually before failure or degradation
- telemetry, logger, recorder, or measurement signals may stop near incidents
- workload thresholds, battery drain, thermal mitigation, memory pressure, CPU pressure, or observer effect boundaries are unknown
- NFR budgets need calibration from real operating behavior

Do not use it for static docs/schema work or ordinary web/backend performance benchmarking.

## How to use

1. Start from target characterization when available.
2. Define safe scenarios using `templates/operating-envelope.md`.
3. Include idle, nominal, peak, near_boundary, degraded, observer_off, observer_on, recovery, and blackout_or_telemetry_loss when relevant.
4. Record safety limits before running any experiment.
5. Capture report paths for each scenario.
6. Record normal ranges, early warning trends, boundary conditions, blackout points, observer effect, and no-go boundaries.
7. Hand off to `embedded-nfr-calibration` with calibration inputs.

## Outputs

Produce or update:

- `docs/targets/<target>/operating-envelope.md`
- `reports/operating-envelope/<target>/<scenario>.json`
- `baselines/resource/<target>/near_boundary.json`
- `baselines/resource/<target>/degraded.json`

## Rules

- Do not push a target past safe experimental limits.
- Treat telemetry blackout as evidence, not absence of failure.
- Record observer-on and observer-off differences when the observer can perturb workload.
