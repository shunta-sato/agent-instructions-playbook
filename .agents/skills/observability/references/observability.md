# Observability template and checklist

Use this template to decide what signals are required and how they correlate.

## 0) Live discovery evidence

Before copying static examples, inspect current repo/runtime reality:

- Instrumentation config/schema paths:
- Logging/metrics/tracing library and version/status output:
- External dependency interface and connection state:
- Existing dashboard/query/log artifact paths:

For embedded, edge, target-local, high-frequency, or always-on instrumentation, route to `embedded-nfr-design` and `embedded-observer-effect-review` before treating the signal as safe to enable by default.

## 1) Operations to observe

- Operation name:
- Purpose / user impact:
- Boundary (entry → exit):

## 2) Correlation identifiers

- Primary identifier (request_id / job_id / trace_id):
- Where it is generated:
- Where it is propagated:

## 3) Logs (minimum required events)

Emit **structured logs** for:

- **start**: operation began
- **outcome**: operation completed (success)
- **failure**: operation failed (error)

Required fields (minimum):

- operation
- identifier(s) (request_id / job_id / trace_id)
- result (success/failure)
- duration_ms
- error_category (if failure)

## 4) Metrics (minimum required)

- errors (counter)
- latency (histogram/timer)

Optional (golden signals when relevant):
- traffic
- saturation

## 5) Traces

- Span boundaries (entry/exit)
- Correlate logs with trace_id/span_id

## 6) Safety rules

- Do **not** log secrets or PII.
- Scrub or hash identifiers where required.
- Follow OWASP Logging Cheat Sheet and NIST SP 800-92 guidance.

## 7) Concurrency observability

- Correlate logs across threads/tasks using trace_id/span_id or job_id.
- Prefer structured logs; avoid logging secrets.
- Measure queue length, worker utilization, and callback latency when applicable.

## 8) Noise control

- Throttle or sample high-frequency logs.
- Prefer boundary logging (once per operation).
- On embedded targets, account for observer overhead before adding target-local default logs, traces, or profiling.

## 9) Measurement purpose and feedback

For each signal, record why it exists and what action it enables.

```markdown
## Measurement Purpose and Feedback

- Signal:
- Decision supported:
- Action owner:
- Expected action when degraded:
- Counter-metric:
- Failure mode / misleading interpretation:
- Artifact path or dashboard/query:
```

Rules:

- Do not add metrics merely because they are easy to emit.
- Prefer signals that support a decision or failure diagnosis.
- Add a counter-metric when one metric can improve while user or operational outcomes degrade.
- Keep this practical. Do not add measurement philosophy.
