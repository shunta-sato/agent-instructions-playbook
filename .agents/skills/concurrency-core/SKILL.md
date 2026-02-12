---
name: concurrency-core
description: "Concurrency design patterns & safety workflow. Use when you introduce or modify concurrency (threads/async/callbacks/queues/locks), parallelize for performance, or need a clear shutdown/cancellation strategy."
metadata:
  short-description: Concurrency design patterns and planning
---

## Purpose

Produce a **Concurrency Plan** with pattern-based choices so concurrent behavior is deliberate, safe, and testable.

## When to use

Use this skill when you:
- add or change threads, async/await, callbacks, queues, locks, or executors
- parallelize work for performance or responsiveness
- introduce background workers, timers, or concurrent IO

## How to use

0) Open `references/concurrency-core.md`.
1) Write a **Concurrency Plan** (use the template).
2) Select an appropriate pattern (or justify why none fits).
3) Identify shared mutable state and choose a containment strategy.
4) Define cancellation/shutdown and error propagation.
5) Define observability hooks for diagnosing concurrent behavior.
6) Define verification strategy; invoke `$thread-safety-tooling` if multi-threading exists.

## Output expectation

- Output the full Concurrency Plan sections.
- Add a short **Risks & mitigations** summary.
