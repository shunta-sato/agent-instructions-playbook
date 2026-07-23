---
name: embedded-observer-effect-review
description: "Use when target-local logging, recording, collection, tracing, profiling, or measurement could change scheduler, power, thermal, I/O, memory, wakeup, or workload behavior. Do not use for ordinary server observability with no embedded physical-footprint risk."
metadata:
  short-description: Embedded observer-effect review
  templates:
    - templates/observer-effect-review.md
---

## Purpose

Use this skill to check whether the observer changes the behavior being observed on embedded or target-local systems.

It answers one question:

**Could this logging, recording, tracing, profiling, collection, or measurement path become part of the workload or hide the true physical footprint?**

## When to use

Use this skill when a change adds or modifies:

- target-local logger, recorder, collector, tracer, profiler, or measurement harness
- high-frequency observation
- workload-sensitive paths where extra wakeups, I/O, serialization, or allocation can perturb results
- resource claims based on instrumentation that runs on the target

Do not use it for ordinary server-side logs/metrics/traces unless the instrumentation is target-local and resource-sensitive.

Do not use for host-side CLIs, batch tools, servers, or ordinary daemons that have no physical target constraint. Work is embedded only when an actual constraint exists: battery/power budget, thermal limit, flash-wear limit, real-time deadline, constrained target CPU/RAM, or a physically separate target device. Logger/recorder/collector/sampler/polling vocabulary alone does not make work embedded; when in doubt and no physical constraint is named, treat the work as non-embedded and use the general skills (`$performance-review`, `$observability`).

## How to use

1. Identify the observer:
   - component
   - cadence
   - data captured
   - storage/transmission path
   - default vs debug mode
2. Compare observer-on and observer-off behavior where possible.
3. Review perturbation vectors:
   - scheduler and wakeups
   - CPU and allocation
   - storage writes and flash wear
   - network/radio use
   - thermal behavior
   - lock contention or queue pressure
   - timing/jitter impact
4. Decide whether the observer can be enabled by default.
5. Define mitigation:
   - sampling
   - throttling
   - ring buffer with bounded drops
   - debug-only mode
   - off-target collection
   - event-driven capture
6. Write `reports/resource/observer-effect-review.md` using the template.
7. Route measurement scenarios to `embedded-nfr-harness-design` and final decision to `embedded-nfr-gate`.

## Output expectation

Produce:

- `reports/resource/observer-effect-review.md`

## Gotchas

- **Common pitfall:** measuring a workload with a logger that causes the workload.
  **Instead:** compare observer-on and observer-off or mark observer overhead unknown.
- **Common pitfall:** adding verbose target logs to diagnose a resource issue.
  **Instead:** throttle, sample, or make the observer debug-only until measured.
- **Common pitfall:** hiding flash wear in diagnostic capture.
  **Instead:** include storage write rate and retention in the observer review.
