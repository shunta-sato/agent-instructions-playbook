# Non-functional requirements guideline (ISO/IEC 25010)

This document is a template to keep non-functional requirements (quality attributes) explicit when an AI agent adds or changes code.

It uses ISO/IEC 25010 “product quality model (8 characteristics)” as the outline. For each item, fill the same fields:

**metric / threshold / measurement method / tests & monitoring / design notes**

## Common writing rules

Quality requirements are less likely to drift if you write a short scenario first, then end with measurable conditions.

- Write 1–2 sentences in the order: **context → stimulus → response → measurable condition**, then fill the table.
- Set thresholds based on “what hurts”: not only averages, but **worst case, percentiles (p95/p99), and deadline-miss rate**.
- A threshold that cannot be tested or monitored is incomplete. Decide *how to measure first*.
- Quality attributes trade off. When you raise one, record the design rationale and the cost it increases elsewhere.

> Note: thresholds (numbers) depend on product, load, cost, and risk. This document provides a fillable shape first; values can be set later.

---

## Functional suitability

ISO/IEC 25010: Functional suitability

| Item | Metric | Threshold | Measurement method | Tests / monitoring | Design notes |
|---|---|---|---|---|---|
| Functional completeness | requirement/user-story implementation rate; acceptance test pass rate | must requirements: 100%; acceptance tests: 100% | count via requirements ↔ tests mapping | run acceptance tests in CI; warn on uncovered requirements | define requirement boundaries; fix input conditions at entry points (API/UI) |
| Functional correctness | critical bug count; spec deviation rate | P0/P1 bugs: 0; deviation: 0 | verify via unit/integration/property tests | regression tests; monitor exception/error rates | make edge cases explicit; lock failure paths early |
| Functional appropriateness | primary task completion rate; unnecessary steps count | completion ≥ X%; steps ≤ Y | measure via user testing | monitor funnel/operation logs | reflect “user goal” in naming and UI; reduce detours |

---

## Performance efficiency

ISO/IEC 25010: Performance efficiency

| Item | Metric | Threshold | Measurement method | Tests / monitoring | Design notes |
|---|---|---|---|---|---|
| Time behavior | latency p95/p99; throughput; deadline-miss rate | p95 ≤ X ms, p99 ≤ Y ms; miss rate ≤ Z% | load tests for percentiles; tracing for breakdown | load tests in CI; monitor latency percentiles and timeout rate in prod | reduce work (cache); add resources (scale); control resource usage (priority/scheduling/queue limits) |
| Resource utilization | CPU/memory/I/O/network usage; queue length | peak CPU ≤ X%; memory ≤ Y%; queue length ≤ Z | profiling + metrics | prod metrics + alerts; leak detection | identify bottleneck resource and optimize locally; queues must have caps |
| Capacity | concurrent connections; req/s; data-size limits | concurrent ≥ X; req/s ≥ Y; define graceful degradation beyond limits | ramp tests to see failure mode | capacity tests; monitor scaling conditions and saturation | do not break beyond limits; decide reject/delay/degrade behavior upfront |

---

## Compatibility

ISO/IEC 25010: Compatibility

| Item | Metric | Threshold | Measurement method | Tests / monitoring | Design notes |
|---|---|---|---|---|---|
| Co-existence | resource interference (CPU/mem); port conflicts; contention rate | over-allocation: 0; conflicts: 0 | run side-by-side in same environment | container/VM resource monitoring | reduce shared resources (ports/files/DB); define caps |
| Interoperability | integration success rate; compatibility-break count; conversion-failure rate | success ≥ X%; breaking changes: 0 | contract tests; schema validation; interoperability tests | monitor integration error rate; capture failing payloads for diagnosis | align not only syntax but semantics; put discovery and interface management (conversion/mediation) at boundaries |

---

## Usability

ISO/IEC 25010: Usability

| Item | Metric | Threshold | Measurement method | Tests / monitoring | Design notes |
|---|---|---|---|---|---|
| Appropriateness recognizability | first-time user understanding rate; drop-off rate | understanding ≥ X%; drop-off ≤ Y% | measure via first-time task test | monitor onboarding funnel | state “what you can do” clearly on the first screen; standardize terminology |
| Learnability | time to reach goal task on first attempt | ≤ X minutes | user testing timing | monitor help-view rate and “confused” actions | make it safe to try and easy to recover (undo/redo) |
| Operability | task completion rate; operation error rate; undo count | completion ≥ X%; error ≤ Y% | measure on representative tasks | UI event logs; monitor failure hotspots | allow pause/resume for long operations; reduce repetition via batch/aggregation |
| User error protection | accidental destructive action rate; recovery success rate | accidental ≤ X%; recovery ≥ Y% | validate with misuse scenarios | monitor destructive-action frequency and failures | confirmations, previews, safe defaults; retain state needed for undo |
| User interface aesthetics | design-rule violations; consistency violations | critical violations: 0 | UI review + UI tests | screenshot regression tests | reuse components; same meaning → same appearance |
| Accessibility | WCAG conformance; alternative operation coverage | WCAG 2.2 AA+ | automated + manual checks | accessibility regression tests | include keyboard nav, screen readers, and color contrast from the start |

---

## Reliability

ISO/IEC 25010: Reliability

| Item | Metric | Threshold | Measurement method | Tests / monitoring | Design notes |
|---|---|---|---|---|---|
| Maturity | incident count; failure rate; MTBF | critical incidents ≤ X/month; failure rate ≤ Y% | prod data + incident records | incident mgmt; monitor error rates | make failures observable; eliminate recurrence |
| Availability | uptime; success rate; continuous downtime | uptime ≥ X%; continuous downtime ≤ Y minutes | synthetic monitoring + real traffic | monitor vs targets; alert on breach | design as a chain: detect (monitor/heartbeat) → recover (restart/failover) → prevent (redundancy) |
| Fault tolerance | function retention under partial failure; graceful degradation success | retain primary functions ≥ X% | fault injection tests | chaos experiments; monitor dependency failure rates | isolate dependencies; stop cascades via timeouts and circuit breaking |
| Recoverability | MTTR; post-recovery consistency; rollback time | MTTR ≤ X minutes; consistency violations: 0 | incident drills | recovery drills; backup verification | enable resync; automate recovery; codify procedures |

---

## Security

ISO/IEC 25010: Security

| Item | Metric | Threshold | Measurement method | Tests / monitoring | Design notes |
|---|---|---|---|---|---|
| Confidentiality | encryption coverage; unauthorized access count | encrypt sensitive data: 100%; unauthorized: 0 | design review + configuration inspection | monitor access-denied logs | protect at rest and in transit; minimize data crossing boundaries |
| Integrity | tamper detection coverage; consistency-check coverage | tamper detection: 100% | signatures/hashes/integrity checks | monitor integrity-failure logs | validate message integrity; fail closed |
| Non-repudiation | audit log missing rate for critical actions | missing: 0 | validate audit log requirements | alert on audit log gaps | record “who did what”; store logs in tamper-resistant location |
| Accountability | traceability rate; correlation ID coverage | traceable ≥ X%; correlation IDs: 100% | verify end-to-end tracing works | monitor correlation ID gaps | keep subject identification → auth → authorization → audit consistent |
| Authenticity | authentication strength; unauthorized login rate | strong auth applied; unauthorized rate ≤ X | threat analysis + verification criteria | monitor suspicious login/anomaly detection | design auth/authz/audit together; detect intrusion and react |

---

## Maintainability

ISO/IEC 25010: Maintainability

| Item | Metric | Threshold | Measurement method | Tests / monitoring | Design notes |
|---|---|---|---|---|---|
| Modularity | cyclic dependency count; coupling metrics; boundary violations | cycles: 0; boundary violations: 0 | dependency graph + static analysis | dependency checks in CI | narrow responsibilities; separate concerns; reduce cross-boundary dependencies |
| Reusability | reuse rate of shared components; duplication rate | duplication ≤ X% | duplication detection + design review | duplication checks in CI | avoid premature generalization; share only when responsibilities align |
| Analysability | time to identify cause (MTTI); time to identify impact scope | MTTI ≤ X minutes | measure from incident response history | logs/metrics/traces monitoring | standardize observability; keep dependency flow traceable |
| Modifiability | change lead time; change success rate; post-change regression rate | small change ≤ X hours; regression ≤ Y% | measure on representative changes | regression tests + post-change monitoring | reduce coupling; localize changes; if adding mediation layers, measure perf cost |
| Testability | test runtime; coverage; flake rate | CI tests ≤ X minutes; coverage ≥ Y%; flake ≤ Z% | test run logs | monitor test failure/flake rate | make state observable/controllable (record/replay, test interfaces, externalized state, reduce nondeterminism) |

---

## Portability

ISO/IEC 25010: Portability

| Item | Metric | Threshold | Measurement method | Tests / monitoring | Design notes |
|---|---|---|---|---|---|
| Adaptability | environment-dependent code count; switchability via config | dependency points < X; configurable ≥ Y% | count via code search and build config | verify across multiple envs in CI | isolate platform dependencies; note potential performance cost |
| Installability | install success rate; install time | success ≥ X%; time ≤ Y minutes | automated install on clean environment | install tests per release | automate install steps; declare external dependencies |
| Replaceability | time to swap key components; breaking-change count | swap ≤ X days; breaking changes: 0 | swap exercises | compatibility tests | keep interfaces small; confine external dependencies to boundaries |

---

## References

- Software Architecture in Practice, 3rd Edition
- ISO/IEC 25010 (System and software quality models)
- Google SRE (SLI/SLO)
- OWASP ASVS
- W3C WCAG 2.2
