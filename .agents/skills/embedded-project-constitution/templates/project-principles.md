# Project Principles

## Physical Footprint Rule

No background runtime is production-ready until its physical footprint is measured or explicitly marked unknown/experimental.

## Claims Rule

No-measurement-no-claim applies to:

- low overhead
- battery safe
- lightweight
- flash safe
- thermally safe
- production ready

## Power Rule

Battery unknown is not AC power. Unknown power state limits production-readiness claims.

## Default Mode Rule

Default mode must be conservative. High-frequency or high-write behavior is burst-only or experimental unless budgeted and measured.

## Degraded Mode Rule

Features define behavior for battery_low, memory_pressure, thermal_pressure, storage_pressure, and measurement_unavailable.
