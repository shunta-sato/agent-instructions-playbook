# <Title> — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- What are we trying to achieve (user impact / system outcome)?
- Why now?

## Scope

### In scope
- ...

### Out of scope / non-goals
- ...

## Constraints / Quality targets

- Latency / throughput / resource budgets:
- Safety/security/privacy:
- Compatibility / rollout constraints:
- Operability (logs/metrics/traces, on-call expectations):

## Context & Orientation

- Key paths / entry points:
- Existing behavior:
- Conventions to follow:
- Unknowns (explicit):

## Design

### Boundary sketch

- Components involved (and their roles):
- Boundary crossings (UI/HTTP/DB/external services):
- DTOs / interfaces (if any):
- Error handling strategy (boundary translation, failure modes):

### Observability

- Logs (start/outcome/failure) + required fields/correlation IDs:
- Metrics (errors + latency; golden signals if relevant):
- Traces (span boundaries, correlation to logs/metrics):

### Testing strategy

- Unit tests:
- Integration tests:
- Stress / concurrency tests (if relevant):
- Manual verification (only if unavoidable):

## Milestones (high-level plan)

Write 3–7 milestones in prose (one sentence each).
Example:
1. Define DTOs and boundary interfaces; add characterization tests.
2. Implement core logic behind a seam; add unit tests.
3. Wire adapters; add observability; add integration tests.
4. Verify and document; run final quality gate.

## Progress (WBS)

Use a checkbox list. Each item should have a concrete deliverable and verification note.

- [ ] (P0) ... — deliverable: ... — verify: ...
- [ ] (P1) ...
- [ ] (P2) ...

## Surprises & Discoveries

Record unexpected constraints, gotchas, and newly learned facts (with evidence when possible).

- YYYY-MM-DD: ...

## Decision log

Record decisions and trade-offs (and why).

- YYYY-MM-DD: Decision ... because ...
  - Options considered:
  - Chosen:
  - Consequences:

## Handoff (update at every stop)

- Current branch / commit:
- What is done:
- What is not done:
- How to run:
- How to test:
- Known risks / open questions:
- Next 1–3 steps (be specific):
- Pointers (files/dirs to read first):

## Validation & Acceptance

List the measurable acceptance criteria and how they are verified.

- AC1: ...
  - Verification:
- AC2: ...

## Outcomes & Retrospective (fill when done)

- What shipped / merged:
- What went well:
- What went wrong:
- Follow-ups / tech debt tickets:
