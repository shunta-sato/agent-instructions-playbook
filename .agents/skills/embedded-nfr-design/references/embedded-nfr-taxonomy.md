# Embedded NFR Taxonomy

Use this reference when `embedded-nfr-design` is triggered.

The goal is a physical contract, not a hardware textbook. Keep the result feature-specific and measurable.

## Target Assumptions

Record these before writing budgets:

- target class: microcontroller, embedded Linux, Android device, ROS 2 robot, edge gateway, desktop-as-target, unknown
- power state: AC, battery, battery_low, vehicle power, unknown
- resource visibility: perf/proc available, OS counters available, hardware counters available, external power meter available, none
- deployment mode: production, experimental, development, debug-only
- operating mode: default, burst, degraded, idle

## NFR Dimensions

Use only dimensions relevant to the feature:

| Dimension | Typical question | Example merge rule |
| --- | --- | --- |
| Polling / sampling cadence | Is default cadence safe for always-on target use? | sub-100ms default cadence blocks submit unless explicitly allowed, measured, and justified |
| CPU | What steady-state and burst CPU is allowed? | default CPU over budget blocks submit |
| Wakeups | How many extra wakeups per second are added? | unbounded wakeups block submit |
| RSS / heap | Is memory bounded across time? | unbounded growth blocks submit |
| Hot-path allocation | Does each loop allocate? | per-sample allocation needs justification |
| Storage writes | Does default mode write continuously? | continuous default writes block submit unless required and budgeted |
| Flash wear | Are write rates safe for media lifetime? | missing wear estimate blocks production-ready claim |
| Battery | Is battery drain measured or explicitly unknown? | battery_unknown is not AC |
| Network/radio | Does background radio use wake the device? | hidden background use blocks battery-safe claim |
| Thermal | Can the feature heat the target or throttle work? | feature-caused thermal rise needs degraded mode |
| Latency / jitter | Does the feature disturb real-time or interactive work? | missed timing budget blocks submit |
| Degradation | What changes under low resource conditions? | missing degraded mode blocks production-ready claim |
| Observer overhead | Does measurement/logging change the workload? | unmeasured observer overhead limits claims |

## Budget Rules

- Default mode is the production steady-state budget.
- Burst mode must have a time bound and trigger condition.
- Experimental mode may be unmeasured only when production claims are limited.
- Unknown is a status, not a pass.
- No-measurement-no-claim: do not claim low overhead, battery safety, thermal safety, or production readiness without matching evidence.
- Battery unknown is not AC power.
- Measurement unknown is not pass.
- Host fallback is not target proof.
- Default always-on polling below 100ms is blocked unless explicitly budgeted, measured, justified, and limited by mode.

## Measurement Evidence

Prefer target evidence. Host fallback is acceptable only when the report says what it cannot prove.

Examples:

- CPU: perf, top, pidstat, process accounting, target runtime counters
- Wakeups: powertop, perf sched, proc counters, platform-specific wakeup sources
- Memory: RSS, heap profiler, allocator stats, process status
- Storage: bytes written, fsync count, write amplification estimate, log volume
- Battery/power: power_supply, external meter, platform power stats
- Thermal: thermal zones, throttling indicators, external measurement
- Latency/jitter: timing histogram, missed deadline count, loop timing stats

## Degraded Mode Checklist

Record decisions for:

- battery_low
- memory_pressure
- thermal_pressure
- storage_pressure
- network_unavailable
- measurement_unavailable
- target_profile_unknown

Allowed responses include reducing cadence, disabling nonessential capture, buffering in memory with bounded drops, switching to event-driven mode, emitting once-only warnings, or marking the feature experimental.
