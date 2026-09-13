# Hot paths and constrained lowering

Inspect actual frequency, bounds, concurrency, copying, allocation, string formatting,
syscalls, blocking, locks, filesystem/network operations and accumulating state. Follow
callers and shared resources, not just changed lines. Optimize only a supported need or
demonstrated regression; frequent calls alone do not justify a cache or new framework.

Separate a clear semantic implementation from target-specific lowering when constraints
require it. Keep equivalence fixtures or an appropriate numerical tolerance/oracle and
validate each materially changed boundary. Lowering, quantization and device execution
can change numerical behavior and error propagation: host success is not target proof.

Check backpressure, dropped work, cancellation, shutdown and degraded behavior where
relevant. A shorter diff is not necessarily the simplest coherent implementation. Preserve
needed diagnostics while preventing the diagnostics from becoming the dominant work.
