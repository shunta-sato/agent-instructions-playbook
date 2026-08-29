---
name: observability
description: "Use when a real operating failure boundary introduced or changed by the candidate cannot be diagnosed with existing signals, or when an explicit operational claim requires measurement. Do not trigger solely because runtime behavior changed."
metadata:
  short-description: Boundary-focused observability
  requires:
    - references/observability.md
---

## Purpose

Add the minimum signal needed to diagnose a concrete operation or support an
explicit operational claim. Observability is not automatic instrumentation for
each runtime change.

## When to use

Use when existing logs, metrics, traces, return values, or platform diagnostics
cannot distinguish a realistic success, failure, timeout, retry, or degraded path
that matters to the current DoD. Also use when the submission makes an explicit
latency, reliability, or production-readiness claim that needs measurement.

Do not use for behavior already diagnosable at the operating boundary, local
prototype code without such a claim, or speculative future operations.

## How to use

0) Open `references/observability.md` and select only relevant sections.
1. Name the operation, actor, failure path, and decision the signal supports.
2. Inspect existing signals before adding a library, dashboard, or framework.
3. Add the smallest useful signal: often one outcome event or one metric is
enough. Logs, metrics, and traces are not a mandatory trio.
4. Include correlation, safe fields, sampling/noise control, and an owner/action
only where the operation requires them.
5. For target-local or high-frequency instrumentation, route physical observer
effect before adding it.
6. Record the evidence in the active plan or PR unless a durable operational
artifact is genuinely required.

## Output expectation

Return the concrete diagnostic gap, existing signals inspected, minimum signal
added or `no change needed`, safety/noise controls, decision supported, evidence
location, and claim limitation.
