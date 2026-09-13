# Android lifetime and cancellation

Identify the lifecycle owner, cancellation boundary, dispatcher/executor, shared mutable
state and externally visible completion semantics. Avoid detached work that outlives its
intended owner. Propagate cooperative cancellation; a broad error handler must not turn
cancellation into success, indefinite retry or a swallowed failure.

Select lifecycle-bound work, persistent scheduled work or platform services from the
actual requirement and supported OS versions. Do not infer durability from a coroutine
or copy a scheduling API without checking the project's current dependencies. Exercise
rotation/recreation, backgrounding, stop/restart and competing callbacks when relevant.

A main-thread check is not proof of race freedom or lifecycle correctness. Verify ordering,
ownership and idempotence at the affected boundary; use the existing project's testing
tools and current platform documentation for concrete API syntax.
