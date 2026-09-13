# Physical constraints are derived, not presets

Relevant dimensions can include CPU time, resident/peak memory, wakeups, allocation,
latency/jitter, deadlines, energy, battery, thermal throttling, network/radio activity,
storage writes and flash endurance. Select dimensions from actual use and shared-resource
effects. Logger, daemon or polling vocabulary alone does not select an embedded policy.

Cadence × per-operation cost × concurrent instances × sustained runtime can reveal
an important aggregate load even when a single call is cheap. Distinguish steady state,
startup and bounded burst. Account for queue growth, missed periods and degradation.

There is no universal polling interval, CPU percentage, byte budget or p99 target.
Derive requirements from supported use, upstream budgets and applicable product policy.
Keep a measured baseline separate from an acceptance threshold. Do not move a requirement
to make the current implementation pass. Short-lived code can still need strict safety
proof; long-lived code does not automatically need an extensibility framework.
