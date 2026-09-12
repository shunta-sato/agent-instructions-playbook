---
name: runtime-performance
description: "Investigate a latency, throughput, resource-growth, or scaling requirement or a concrete performance regression."
---

# Runtime performance

Establish the supported workload, cadence, concurrency, duration and scale, plus the
user-visible consequence. Separate required limits, baseline observations and desired
improvements. Do not invent a percentile, benchmark target, or universal tuning budget.

Use bounded-complexity inspection for a known small path; measure when scaling,
accumulation, waits, allocation/copying, I/O or regression risk changes the decision.
A credible hot path can warrant investigation without explicit performance wording.
Match source/build, configuration, environment, workload, warmup and observation
window for comparisons. Report variability and insufficient samples honestly.

Optimize the measured bottleneck and revalidate affected behavior. Do not introduce
caches, batching, indirection or a generic harness without a current need. Required
performance proof is not optional polish; optional improvements do not prevent finish.
Physical power, thermal, flash, or target-deadline questions are covered by the
separately selected `embedded-runtime-evidence` skill, not an automatic second stage.
