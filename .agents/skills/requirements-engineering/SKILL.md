---
name: requirements-engineering
description: "Use for ambiguous or non-trivial feature planning and requirements documentation: problem framing, spec-before-build checks, requirements briefs/specs, EARS-style requirements, acceptance criteria, traceability, and ISO/IEC 25010 quality scenarios. Do not use for tiny unambiguous implementation tasks, architecture option comparison, or diff-focused design review unless requirements output is requested."
metadata:
  short-description: Requirements engineering
  resources:
    - references/ears-requirements-to-design.md
    - references/iso25010-quality-scenarios.md
    - references/requirements-briefs-and-specs.md
---

## Purpose

Use this skill to turn unclear feature work into verifiable requirements and lightweight design inputs. It may start with a small Problem Frame when a request risks solution-first implementation or unclear problem ownership.

It covers:

- small Problem Frames and spec-before-build checks
- requirements briefs, specs, and SRS-style sections
- EARS-style requirement statements
- measurable acceptance criteria and verification methods
- requirement-to-design/test traceability
- Definition of Done (observable completion conditions)
- ISO/IEC 25010 quality scenarios for non-functional requirements

## When to use

### Checkable thresholds

- **ambiguous** = testable acceptance criteria cannot be written from the request alone.
- **non-trivial** = any of: ≥2 modules touched, OR ≥2 user-visible behaviors added/changed, OR a new domain concept is introduced.

Use this skill when:

- a request is ambiguous, cross-component, user-facing, or risky enough to need requirements first
- you are creating or updating a requirements brief/spec
- vague qualities such as "fast", "reliable", "secure", or "usable" need measurable targets
- non-embedded performance expectations need scale assumptions, latency/throughput acceptance criteria, or handoff to `performance-review`
- embedded physical-footprint qualities such as CPU, RAM, wakeups, battery, flash wear, thermal, latency/jitter, or observer effect need high-level requirement wording before NFR design
- requirements must be traceable to design decisions, tests, or monitoring

Do not use it for small, already-clear implementation tasks unless the user asks for requirements documentation. If architecture options must be compared, route to `architecture-decision-analysis`. If NFRs involve embedded physical footprint, route to `embedded-nfr-design` after drafting the smallest useful high-level requirement.

## How to use

1. If the request is solution-first or problem ownership is unclear, write the smallest useful Problem Frame before requirements.
2. Choose the smallest useful output; do not require a full requirements spec for every task.
3. Open only the needed reference:
   - `references/requirements-briefs-and-specs.md` for briefs, specs, IDs, and trace tables
   - `references/ears-requirements-to-design.md` for EARS statements, boundaries, failure paths, and test seeds
   - `references/iso25010-quality-scenarios.md` for measurable quality attributes and NFRs
4. Write 1-5 requirements first unless the task genuinely needs more.
5. For each requirement, include acceptance criteria, a Definition of Done, and a verification method.
6. If an embedded NFR requirement depends on target behavior, do not finalize numeric acceptance criteria until `embedded-target-characterization` exists or the requirement is explicitly unknown/provisional.
7. If the requirement involves embedded CPU, memory, wakeups, battery, flash wear, thermal, latency/jitter, or observer effect, hand off to `embedded-nfr-design` for physical budgets and no-measurement-no-claim handling.
8. If the requirement involves non-embedded request latency, render cost, throughput, data-size scaling, or N+1 risk, hand off to `performance-review` with scale assumptions and acceptance criteria.
9. Trace acceptance criteria into the `test-driven-development` Test List and the `quality-gate` exit criteria when implementation will follow.
9b. Record every measurable quality/NFR target in a gate-checkable Quality Targets list: `metric | target | measurement method | measured result (filled before gate, or not-measured with reason)`. The quality gate blocks submission when a declared target is silently unmeasured or unmet.
10. Add assumptions, open questions, and traceability only where they reduce ambiguity.

## Output expectation

Depending on the task, produce one or more of:

- Problem Frame
- Spec-before-build checklist
- Quality Targets list (metric | target | measurement method | measured result or not-measured reason)
- Requirements Brief or Requirements Spec section
- EARS requirements with IDs, priority, rationale, acceptance criteria, and verification method
- Definition of Done with observable completion conditions
- ISO/IEC 25010 quality scenarios with metrics, thresholds, measurement, tests/monitoring, and design notes
- boundary sketch covering actors, systems, changed components, external dependencies, and out-of-scope areas
- failure paths and seeded test list
- trace table linking requirements to design, tests, and monitoring
