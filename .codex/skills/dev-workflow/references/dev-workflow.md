# Dev workflow templates

This file is the reference template for `$dev-workflow`.
When in doubt, come back here and **only fill the blanks**.

## 0) Change Brief (one paragraph)

- Purpose:
- Inputs:
- Outputs:
- Constraints (performance/safety/compatibility/ops/etc.):
- Assumptions (separate unknowns explicitly):
- Boundaries (UI/HTTP/DB/external services):

## 1) Requirements (EARS + acceptance criteria)

### EARS (“shall” statements)

- R1: When/While/Where/If ..., the system shall ...
- R2:
- R3:

### Acceptance criteria (measurable)

- R1 success:
- R1 failure:
- R2 success:
- R2 failure:

## 2) Constraints (5–9 bullets / MUST statements)

- MUST:
- MUST:
- MUST:

Examples: readability / modularity / boundaries / error handling / test design / documentation.

## 3) Design sketch (minimal design memo)

- Touched/added places (files, functions, classes):
- Added/changed units and roles (one sentence each):
- Boundary crossings:
- DTOs/interfaces (only if needed):
- Failure paths (exceptions/return values/branches):
- Testing strategy:

## 3.5) Observability plan (mandatory when runtime behavior changes)

- Operations to observe (user-facing or system-facing actions):
- Identifiers for correlation (request_id/job_id/trace_id):
- Logs (minimum: start / outcome / failure) with required fields:
- Metrics (minimum: errors + latency; add golden signals if relevant):
- Traces (span boundaries and correlation to logs/metrics):
- Safety (no secrets/PII; OWASP/NIST logging guidance):

### Requirements-doc plan (only when requirements change)

- Docs to update (paths):
- Added/changed requirement IDs (R-xxx):
- Acceptance criteria update points (success/failure):
- Verification method updates (tests/measurement/monitoring):
- Trace updates (requirement IDs → design/tests):
- If unsure, explicitly invoke `$requirements-documentation` and decide the minimal diff via its templates.

### Comment/documentation plan (C++ / MUST when touching C++)

- `.hpp`: add Doxygen for all declarations (public/private; classes/structs, functions, fields, constants)
- `.cpp`: split into cohesion paragraphs and add an intent comment per paragraph
- Boundaries/coupling points: annotate the “contract” (assumptions/failures/rationale) where leaving the module or external I/O/library
- Constants: record meaning/unit/range (or rationale) via naming and/or comments
- Unit tests: make the “why” and the “what” readable

## 4) Test List (3–10 items)

- [ ] 1)
- [ ] 2)
- [ ] 3)

First item to implement:
- Now:

## 4.5) Legacy notes (when `$working-with-legacy-code` was used)

- Safety net (characterization/regression tests):
- Seams (substitution points):
- Extract/Sprout (choice + rationale):
- Risk (remaining uncertainty):

## 5) How to test (commands and results)

Run in this order (as far as possible):

1) build
2) format (auto-format)
3) static analysis
4) tests

How to decide commands:

- First, use the repo’s canonical unified commands (e.g., `make check`, `./tools/check`)
- If not available, use environment tools (formatter/static analyzers/test runners)
- Do not silently skip. If you cannot run something, state the reason and how to enable it.

- Build:
- Format:
- Static analysis:
- Tests:
