---
name: requirements-engineering
description: "Use for ambiguous or non-trivial feature planning and requirements documentation: problem framing, spec-before-build checks, requirements briefs/specs, EARS-style requirements, acceptance criteria, traceability, and ISO/IEC 25010 quality scenarios. Do not use for tiny unambiguous implementation tasks, architecture option comparison, or diff-focused design review unless requirements output is requested."
metadata:
  short-description: Requirements engineering
---

## Purpose

Use this skill to turn unclear feature work into verifiable requirements and lightweight design inputs. It may start with a small Problem Frame when a request risks solution-first implementation or unclear problem ownership.

It covers:

- small Problem Frames and spec-before-build checks
- requirements briefs, specs, and SRS-style sections
- EARS-style requirement statements
- measurable acceptance criteria and verification methods
- requirement-to-design/test traceability
- ISO/IEC 25010 quality scenarios for non-functional requirements

## When to use

Use this skill when:

- a request is ambiguous, cross-component, user-facing, or risky enough to need requirements first
- you are creating or updating a requirements brief/spec
- vague qualities such as "fast", "reliable", "secure", or "usable" need measurable targets
- requirements must be traceable to design decisions, tests, or monitoring

Do not use it for small, already-clear implementation tasks unless the user asks for requirements documentation. If architecture options must be compared, route to `architecture-decision-analysis`.

## How to use

1. If the request is solution-first or problem ownership is unclear, write the smallest useful Problem Frame before requirements.
2. Choose the smallest useful output; do not require a full requirements spec for every task.
3. Open only the needed reference:
   - `references/requirements-briefs-and-specs.md` for briefs, specs, IDs, and trace tables
   - `references/ears-requirements-to-design.md` for EARS statements, boundaries, failure paths, and test seeds
   - `references/iso25010-quality-scenarios.md` for measurable quality attributes and NFRs
4. Write 1-5 requirements first unless the task genuinely needs more.
5. For each requirement, include acceptance criteria and a verification method.
6. Add assumptions, open questions, and traceability only where they reduce ambiguity.

## Outputs

Depending on the task, produce one or more of:

- Problem Frame
- Spec-before-build checklist
- Requirements Brief or Requirements Spec section
- EARS requirements with IDs, priority, rationale, acceptance criteria, and verification method
- ISO/IEC 25010 quality scenarios with metrics, thresholds, measurement, tests/monitoring, and design notes
- boundary sketch covering actors, systems, changed components, external dependencies, and out-of-scope areas
- failure paths and seeded test list
- trace table linking requirements to design, tests, and monitoring
