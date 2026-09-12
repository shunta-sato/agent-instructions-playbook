# Observe the observer

Instrumentation can change allocation, locks, scheduling, I/O, wakeups, radio activity,
thermal state and the tail latency being measured. Distinguish feature cost from collector
cost. Preserve a minimally observed baseline when the measurement itself is material.

Choose bounded sampling, aggregation, buffers and export cadence from the actual budget.
Avoid unbounded queues or per-event durable writes on a hot path unless required and
measured. Buffering trades overhead against loss and shutdown behavior; record the trade.

Where feasible compare instrumentation off/on under matched conditions, including burst
and pressure. A stable average does not prove absence of tail or thermal effects. If a
counter cannot be observed without changing behavior, report that limitation rather than
asserting zero cost. Collector success is not proof that the target remained unperturbed.
