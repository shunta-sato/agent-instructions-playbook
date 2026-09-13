# Native concurrency evidence

State ownership, lifetime, synchronization, ordering, cancellation and progress invariants.
Inspect blocking while holding locks, callbacks under locks, lock ordering and publication
of partially initialized state. Atomics do not automatically make a multi-field invariant
atomic; race freedom alone does not establish correctness or liveness.

Use compiler annotations, static analysis, thread/address sanitizers and bounded stress
when supported by the actual toolchain. Dynamic tools cover the paths/interleavings they
observe; a clean run is not a proof of all races or deadlocks. Do not claim a race detector
establishes deadline compliance. Retain a concrete regression schedule/oracle when one
exists and distinguish scheduling-sensitive tests from ordinary deterministic tests.
