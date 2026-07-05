---
name: observability
description: "Use when a runtime behavior change needs diagnosable signals: async/background jobs, external calls, user-visible operations, or incident-prone flows. Do not use for docs-only or refactor-only changes with no behavior shift."
metadata:
  short-description: Observability plan and checklist
  requires:
    - references/observability.md
---

## Purpose

Use this skill to make important runtime behavior diagnosable through logs, metrics, traces, correlation identifiers, and safe logging practices.

## When to use

Use this skill when a change adds or changes runtime behavior where operators or developers need evidence to diagnose outcomes, latency, or failures:

- Async jobs, queues, schedulers, workers, or other background work.
- External calls to APIs, databases, filesystems, message brokers, or third-party services.
- User-visible operations where success, failure, or degraded behavior must be explainable.
- Incident-prone flows such as retries, timeouts, fallbacks, rate limits, auth, payments, imports, exports, or migrations.
- Target-local instrumentation for embedded/edge systems, only after routing physical-footprint risk through the embedded NFR skills below.
- Latency/error signals needed to monitor a `performance-review` decision after shipping.

Do not use this skill for docs-only changes, pure formatting, mechanical refactors, or tests that do not change runtime behavior.

## How to use

0) If this skill is triggered, open `references/observability.md` and follow only the relevant template sections.

0a) If instrumentation is embedded, edge, target-local, high-frequency, or always-on, route first to `embedded-nfr-design` and `embedded-observer-effect-review`. Observability signals can change scheduler, power, wakeups, thermal, I/O, and memory behavior on targets.

1) Live-discover existing instrumentation before adding examples: logging config, metric/tracing libraries, dashboards/queries, external dependency interfaces, schema/config paths, connection state, and relevant version/status output.

2) Define the operations that need to be observable (user-facing or system-facing actions).

3) Identify correlation identifiers (request_id / job_id / trace_id) and ensure they are logged consistently.

4) Add the minimum log events: start / outcome / failure, with required fields.

5) Add metrics for errors and latency (expand to golden signals if relevant).

6) Add trace spans and ensure logs and metrics are correlated via identifiers.

7) For each signal, record the decision it supports, the owner/action when degraded, a counter-metric when relevant, and any misleading interpretation risk.

7a) If the signal supports a `performance-review` decision, record the reviewed hot path, the cost assumption being watched, and the threshold or trend that should reopen the decision.

8) Apply safety rules (no secrets/PII; follow OWASP/NIST logging guidance).

9) Control noise (sampling, throttling, or once-only logging).

## Output expectation

- Record decisions in the Observability Plan.
- Include measurement purpose and feedback for each signal: decision supported, action owner, expected action when degraded, counter-metric where relevant, misleading interpretation risk, and artifact path or dashboard/query.
- Include live-discovery evidence: inspected files/commands, version/status output, connection state, and log/metric/trace artifact paths or dashboard/query links.
- Ensure the quality gate’s observability checklist passes.
