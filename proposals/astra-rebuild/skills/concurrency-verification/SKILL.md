---
name: concurrency-verification
description: "Use when ownership, cancellation, synchronization or execution ordering changes; not merely because code runs in a service."
---

# Concurrency verification

State the invariant, ownership/lifetime, execution context and happens-before or
serialization argument that matters. Examine cancellation, shutdown, lock ordering,
backpressure, reentrancy and error propagation where affected.

Use [platform constraints](references/platforms.md) for Android or ROS 2. Select
available race tooling, controlled scheduling or stress tests for the invariant;
tools do not replace an ownership argument and a clean sanitizer run is not proof
for all schedules. Preserve actual tool/runtime versions with decisive results.

No mandatory platform cascade or separate concurrency report. Deliver the changed
contract and focused proof, retaining material limitations for unsupported tooling.
