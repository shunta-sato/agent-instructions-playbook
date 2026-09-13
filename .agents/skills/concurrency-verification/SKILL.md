---
name: concurrency-verification
description: "Change or diagnose synchronization, cancellation, executor scheduling, shared-state ownership, or shutdown behavior."
---

# Concurrency verification

Identify the changed shared-state invariant, lifetime, ordering, cancellation and
shutdown behavior. Verify the race or liveness property that matters; the existence
of a thread or callback is not a request for a complete concurrency plan.

Use `references/android.md` for Android lifecycle/background scheduling decisions,
`references/ros2.md` for executor and callback-group interactions, and
`references/native.md` for native race/lock tooling. Check the project's actual
platform versions before using version-sensitive APIs.

A stress test or sanitizer pass is evidence only for exercised behavior. Inspect
lock ordering, blocking under locks, bounded queues, cancellation propagation and
resource ownership where affected. Multiple executor threads alone do not eliminate
a deadlock. Do not add production instrumentation if it is not needed to diagnose
an actual failure or support a required claim.
