# Observability template and checklist

Use this template to decide what signals are required and how they correlate.

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

## 7) Noise control

- Throttle or sample high-frequency logs.
- Prefer boundary logging (once per operation).
