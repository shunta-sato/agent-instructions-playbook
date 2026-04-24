---
name: observability
description: "Use when a runtime behavior change needs diagnosable signals: async/background jobs, external calls, user-visible operations, or incident-prone flows. Do not use for docs-only or refactor-only changes with no behavior shift."
metadata:
  short-description: Observability plan and checklist
---

## Purpose

Use this skill to make important runtime behavior diagnosable through logs, metrics, traces, correlation identifiers, and safe logging practices.

## When to use

Use this skill when a change adds or changes runtime behavior where operators or developers need evidence to diagnose outcomes, latency, or failures:

- Async jobs, queues, schedulers, workers, or other background work.
- External calls to APIs, databases, filesystems, message brokers, or third-party services.
- User-visible operations where success, failure, or degraded behavior must be explainable.
- Incident-prone flows such as retries, timeouts, fallbacks, rate limits, auth, payments, imports, exports, or migrations.

Do not use this skill for docs-only changes, pure formatting, mechanical refactors, or tests that do not change runtime behavior.

## How to use

0) If this skill is triggered, open `references/observability.md` and follow only the relevant template sections.

1) Live-discover existing instrumentation before adding examples: logging config, metric/tracing libraries, dashboards/queries, external dependency interfaces, schema/config paths, connection state, and relevant version/status output.

2) Define the operations that need to be observable (user-facing or system-facing actions).

3) Identify correlation identifiers (request_id / job_id / trace_id) and ensure they are logged consistently.

4) Add the minimum log events: start / outcome / failure, with required fields.

5) Add metrics for errors and latency (expand to golden signals if relevant).

6) Add trace spans and ensure logs and metrics are correlated via identifiers.

7) Apply safety rules (no secrets/PII; follow OWASP/NIST logging guidance).

8) Control noise (sampling, throttling, or once-only logging).

## Output expectation

- Record decisions in the Observability Plan.
- Include live-discovery evidence: inspected files/commands, version/status output, connection state, and log/metric/trace artifact paths or dashboard/query links.
- Ensure the quality gate’s observability checklist passes.
