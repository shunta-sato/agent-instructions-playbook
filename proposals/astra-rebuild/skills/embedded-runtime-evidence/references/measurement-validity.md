# Measurement validity

Bind a result to source/build, target/revision, workload, configuration, environment,
method and observation interval. Retain exact artifact identity across collection,
validation and reporting; latest filename or co-presence is not causal evidence.

Compare instrumented and uninstrumented baselines when observer cost can matter.
Account for logging, allocation, copying, syscalls, wakeups, filesystem/radio I/O
and blocking in the measured path. Calibrate the observer where possible and state
what cannot be observed. Measurement unavailability is not a zero-overhead result.

Use adequate samples and representative load for percentile/deadline claims.
Host simulation, synthetic traffic and short idle runs prove only their conditions;
do not extrapolate them to battery safety, thermal stability, flash endurance or
real-time deadlines without the necessary evidence.

Reuse results while their validity conditions hold; remeasure only affected claims
after changes. Distinguish a valid measurement, meeting a threshold, and overall
release authorization. These are separate decisions.
