# Physical constraints

Consider applicable CPU time, wakeups, memory growth, hot-path allocations, storage
writes, flash wear, battery, network/radio duty, thermal behavior, latency/jitter,
degradation and observation overhead. This is a discovery vocabulary, not a form
whose every cell must be filled.

Cadence is part of the budget: per-operation cost can become material through
sampling rate, burst duration, continuous runtime and fleet size. Distinguish
steady state from bounded bursts and experimental modes. A short polling interval
is not justified by unit tests alone. Record why default behavior is sustainable.

Budget values need provenance from user needs, upstream limits or applicable policy.
Target measurements characterize capability; they do not redefine a failing
requirement. Unknown/provisional limits cannot establish production readiness.

Check affected battery-low, memory-pressure, thermal-pressure, storage-pressure,
measurement-unavailable and recovery behavior. Missing instrumentation should not
cause unbounded retries or silently disable a required protection. Preserve useful
diagnostics without making the observer the dominant workload.
