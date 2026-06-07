# Architecture decision analysis reference

Use this reference only when `architecture-decision-analysis` is triggered.

The goal is a lightweight decision record, not a formal architecture review ceremony.

## 1. Decision question

Write the decision as a question.

Good examples:

- Should this workflow remain synchronous or move to a queue?
- Should this storage stay on SQLite or move to PostgreSQL?
- Should this cache be local, distributed, or omitted?
- Should this data be owned by service A or service B?

Reject questions that are too broad:

- How should the whole system be architected?
- What is the best design?
- How can we improve the codebase?

For broad questions, narrow the changed boundary first.

## 2. Quality drivers

Each driver needs:

- scenario
- metric or threshold
- verification method

Template:

| Driver | Scenario | Metric / threshold | Verification |
| --- | --- | --- | --- |
| Latency | During peak search traffic, users receive results without blocking UI feedback | p95 under target threshold | benchmark or integration measurement |
| Availability | When the external provider fails, the operation degrades predictably | fallback path exercised | integration test + failure simulation |
| Operability | On failure, operators can identify the failed dependency and affected operation | logs/metrics/traces include identifiers | observability plan check |
| Physical footprint | During default target-local operation, resource use stays within device budget | CPU, wakeup, memory, write, thermal, or jitter threshold | embedded NFR matrix and resource smoke |

If the metric cannot be written, route to `requirements-engineering`.
If the metric is an embedded physical-footprint budget, route to `embedded-nfr-design`.

## 3. Option comparison

Use at most 3 options.

| Option | Summary | Assumptions |
| --- | --- | --- |
| A | Keep current structure | Current limits remain acceptable |
| B | Introduce queue | Async latency is acceptable |
| C | Split storage responsibility | Migration path is feasible |

Avoid adding a “perfect” option that is not implementable under constraints.

## 4. Risk / tradeoff analysis

Use concrete risks.

Weak:

- Option B is more complex.

Better:

- Option B introduces retry ordering and duplicate processing risk; verification needs idempotency tests and queue-depth monitoring.

Use sensitivity points for assumptions that can change the decision:

- p95 latency target
- write volume
- provider failure rate
- migration downtime tolerance
- data consistency requirement
- on-call support capacity

## 5. Decision outcomes

Allowed outcomes:

- Chosen direction: one option is selected.
- No-decision: evidence is insufficient; list missing evidence.
- Defer-to-requirements: quality drivers or requirements are too vague.

Do not choose an option just to proceed.

## 6. Verification tasks

Choose only relevant tasks:

- tests
- benchmarks
- migration checks
- monitoring / observability
- rollback / fallback
- dependency or boundary checks

Verification tasks must be actionable. Avoid generic tasks such as “test thoroughly”.

Good:

- Add integration test for duplicate queue message handling.
- Measure p95 latency for synchronous request path before and after queue introduction.
- Add metric for external provider timeout count by operation.
- Verify rollback path keeps old table readable until migration completes.

## 7. Handoffs

Use handoffs only when needed:

- `requirements-engineering`: vague requirement, unclear quality driver, missing acceptance criteria.
- `embedded-target-characterization`: embedded physical quality drivers depend on target baselines or measurement surfaces that are missing.
- `embedded-nfr-design`: embedded CPU, memory, wakeup, battery, flash wear, thermal, latency/jitter, or observer-effect budget needed.
- `observability`: selected design needs logs, metrics, traces, correlation identifiers, or dashboards.
- `error-handling`: boundary failure contract, retries, fallbacks, user-visible errors.
- `code-smells-and-antipatterns`: implementation diff must be checked for new or worsened boundary/coupling issues.
- `quality-gate`: final submit readiness and required artifact presence.
