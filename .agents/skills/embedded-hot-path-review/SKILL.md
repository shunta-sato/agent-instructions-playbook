---
name: embedded-hot-path-review
description: "Use when reviewing embedded or target-local loops, polling, sampling, collectors, recorders, sub-100ms work, per-iteration I/O, repeated serialization, or hot-path allocation. Do not use for non-embedded application request/render/job paths; use performance-review there."
metadata:
  short-description: Embedded hot-path review
---

## Purpose

Use this skill to review the steady-state cost of target-local hot paths before they become production defaults.

It answers one question:

**Can this loop, sampler, poller, collector, recorder, or target-local hot path run without hidden CPU, wakeup, allocation, storage, or latency cost?**

## When to use

Use this skill when a change includes:

- loop, polling, sampling, collector, recorder, or watcher behavior on a target
- sub-100ms periodic work
- per-sample or per-iteration filesystem, network, database, or IPC work
- repeated JSON serialization, regex, sorting, directory scans, allocation, or blocking syscalls in a hot path
- ring buffers, queues, or retention logic on a resource-constrained target

Do not use it for cold-path setup, non-embedded backend request handlers, frontend render paths, pure tests, pure schema changes, or one-shot scripts without target-local steady-state cost. Use `performance-review` for non-embedded request/render/job path costs.

## How to use

1. Identify the hot path:
   - entry point
   - cadence or event trigger
   - maximum duration
   - default vs burst mode
2. Inspect per-iteration work:
   - allocations
   - serialization/parsing
   - filesystem or flash writes
   - directory scans
   - network/radio use
   - blocking syscalls
   - locks or queue operations
3. Check data-structure cost:
   - bounded buffers
   - O(n) operations per sample
   - drop/overwrite policy
   - backpressure behavior
4. Check cadence safety:
   - sub-100ms work must be justified, measured, and usually burst-only
   - default mode should prefer event-driven or coalesced cadence where possible
5. Write `reports/resource/hot-path-review.md` using the template.
6. Route findings to `embedded-nfr-design`, `embedded-nfr-harness-design`, or `embedded-nfr-gate` as needed.

## Outputs

Produce:

- `reports/resource/hot-path-review.md`

## Red Flags

- sub-100ms default polling
- JSON serialization in a high-frequency loop
- filesystem read/write per sample
- recursive directory scan in a loop
- regex, sort, or allocation per sample
- blocking syscall in high-frequency work
- unbounded queue or buffer growth
- O(n) removal from the front of a high-frequency ring buffer
