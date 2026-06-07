---
name: architecture-decision-analysis
description: "Use before implementation or during explicit design review when a cross-boundary technical decision requires comparing multiple architecture options against measurable quality drivers, risks, tradeoffs, and verification tasks. Do not use for ordinary implementation, requirements drafting, diff-focused smell review, function/helper/API boundary decisions, observability instrumentation details, or final submit gating."
metadata:
  short-description: Architecture decision analysis
---

## Purpose

Use this skill to make an explicit architecture decision before implementation when multiple structure or technology options affect quality attributes such as performance, availability, reliability, security, operability, maintainability, migration risk, or data ownership.

This skill answers one question:

**Which architecture option should we choose, defer, or reject, and what evidence must verify the choice?**

It is intentionally narrower than general design advice.

## When to use

Use this skill only when all required conditions apply:

Required:

- There are multiple viable architecture or technology options.
- The decision changes cross-boundary structure: database, persistence model, queue, cache, service split, external dependency, synchronization model, communication boundary, data ownership, availability strategy, or deployment/rollback shape.
- The choice affects measurable quality drivers such as latency, throughput, reliability, availability, security, operability, maintainability, or migration risk.
- For embedded or target-local systems, the choice affects physical quality drivers such as CPU, memory, wakeups, battery, flash wear, thermal, latency/jitter, or observer overhead.

Use additionally when one or more of these applies:

- Implementation should not proceed until risks, tradeoffs, verification tasks, and rollback or fallback considerations are recorded.
- The user asks for an ADR, architecture option comparison, technical selection, or design decision.

## Do not use

Do not use this skill for:

- Ambiguous requirements or acceptance criteria only; use `requirements-engineering`.
- Turning vague NFRs into measurable quality scenarios only; use `requirements-engineering`.
- Current-diff maintainability, boundary leak, cohesion, or coupling review; use `code-smells-and-antipatterns`.
- Function/helper/utility/API/call-site shape decisions; keep this outside this skill.
- Flawed abstraction replacement or call-site migration protocols; keep this outside this skill.
- Logs, metrics, traces, or instrumentation details; use `observability`.
- Final submit readiness; use `quality-gate`.
- Simple implementation tasks with a single obvious approach.
- Readability cleanup.

## How to use

1. Define the decision question.
   - State what is being decided.
   - State what is explicitly not being decided.

2. Confirm the decision is architecture-level.
   - If it is only requirements clarification, route to `requirements-engineering`.
   - If it is only diff review, route to `code-smells-and-antipatterns`.
   - If it is only observability detail, route to `observability`.

3. Open `references/architecture-decision-analysis.md`.

4. Identify up to 5 quality drivers.
   - Each driver must have a scenario, metric or threshold, and verification method.
   - If quality drivers are too vague to measure, stop and route to `requirements-engineering`.
   - If quality drivers are embedded physical-footprint NFRs, route to `embedded-nfr-design` for budgets and measurement claims.
   - If architecture options trade off embedded physical drivers but target baselines are missing, route to `embedded-target-characterization` before final decision.

5. Compare up to 3 options.
   - Include assumptions.
   - Include benefits, risks, tradeoffs, and sensitivity points.

6. Decide one of:
   - chosen option
   - no-decision because evidence is insufficient
   - defer to requirements clarification

7. Produce verification tasks.
   - Include tests, benchmarks, migration checks, observability, rollback/fallback, and dependency or boundary checks only where relevant.

8. Record handoffs to neighboring skills only when needed.

## Output expectation

Return an Architecture Decision Analysis Record:

```markdown
## Architecture Decision Analysis

### 1. Decision question
- Deciding:
- Not deciding:

### 2. Context and constraints
- Current state:
- Constraints:
- Open uncertainties:

### 3. Quality drivers
| Driver | Scenario | Metric / threshold | Verification |
|---|---|---|---|

### 4. Candidate options
| Option | Summary | Assumptions |
|---|---|---|

### 5. Risk / tradeoff analysis
| Option | Benefits | Risks | Tradeoffs | Sensitivity points |
|---|---|---|---|---|

### 6. Decision
- Chosen direction: option | no-decision | defer-to-requirements
- Rationale:
- Rejected options and why:

### 7. Verification tasks
- Tests:
- Benchmarks:
- Migration checks:
- Monitoring / observability:
- Rollback / fallback:
- Dependency or boundary checks:

### 8. Handoffs
- requirements-engineering:
- observability:
- embedded-target-characterization:
- embedded-nfr-design:
- error-handling:
- code-smells-and-antipatterns:
- quality-gate:
```

## Caps

- Candidate options: maximum 3.
- Quality drivers: maximum 5.
- Verification tasks: maximum 7.
- Do not perform full-codebase audits.
- Do not design function boundaries.
- Do not write broad architecture essays.
- If no measurable quality driver exists, do not force this skill.
