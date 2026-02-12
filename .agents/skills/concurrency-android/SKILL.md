---
name: concurrency-android
description: "Android concurrency & background work: coroutines/dispatchers, structured concurrency, WorkManager vs Services/Foreground services, and OS execution limits. Use when modifying Android app code or background processing."
metadata:
  short-description: Android concurrency and background work
---

## Purpose

Keep UI responsive and background work reliable under Android platform constraints.

## When to use

Use this skill when touching:
- Kotlin coroutines, flows, or dispatchers
- Service / WorkManager / JobScheduler
- long-running or background work

## How to use

0) Open `references/concurrency-android.md`.
1) Decide: in-process coroutine vs WorkManager vs Foreground Service. Justify with constraints.
2) Enforce structured concurrency and cancellation paths.
3) Define failure handling and retries (idempotency).
4) Define observability (log correlation IDs; metrics for queue/latency).
5) Define verification (unit tests + instrumentation tests if needed; background restrictions).

## Output expectation

- Add an **Android Background Work Choice** section to the Concurrency Plan.
