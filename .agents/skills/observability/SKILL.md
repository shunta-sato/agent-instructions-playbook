---
name: observability
description: "Add diagnosable runtime signals (logs/metrics/traces) with correlation IDs and safe logging practices."
metadata:
  short-description: Observability plan and checklist
---

## Purpose

Use this skill to make runtime behavior diagnosable by adding logs, metrics, and traces with clear correlation.

## When to use

- Any change that affects runtime behavior or error handling.
- Any time you are unsure which observability signals are required.

## How to use

0) Open `references/observability.md` and follow the templates.

1) Define the operations that need to be observable (user-facing or system-facing actions).

2) Identify correlation identifiers (request_id / job_id / trace_id) and ensure they are logged consistently.

3) Add the minimum log events: start / outcome / failure, with required fields.

4) Add metrics for errors and latency (expand to golden signals if relevant).

5) Add trace spans and ensure logs and metrics are correlated via identifiers.

6) Apply safety rules (no secrets/PII; follow OWASP/NIST logging guidance).

7) Control noise (sampling, throttling, or once-only logging).

## Output expectation

- Record decisions in the Observability Plan.
- Ensure the quality gate’s observability checklist passes.
