# Requirements → Design quick templates

This file is the reference for the `requirements-to-design` skill. When unsure, use these templates as the “shape” of your output.

## 1) EARS requirement sentence templates

The goal is to reduce drift in natural language and make requirements directly implementable.

- Ubiquitous: `The system shall ...`
- Event-driven: `When <event>, the system shall ...`
- State-driven: `While <state>, the system shall ...`
- Optional feature: `Where <feature is enabled>, the system shall ...`
- Unwanted behavior: `If <unwanted condition>, the system shall ...`

Writing tips:

- Do not cram too much into one sentence (split).
- Do not blur the subject/responsibility scope (“system/server/client/etc.” must be clear).
- If you cannot write measurable acceptance criteria, you likely lack design assumptions.

## 2) Acceptance criteria template (measurable)

For each requirement, provide at least:

- Success: <observable result> (status/return value/DB write/log/etc.)
- Failure: <failure type> (DomainError/HTTP 400/retry/fallback/etc.) and the information needed to diagnose cause

## 3) Quality scenario (short form)

Use only when non-functional concerns matter; limit to 0–3.

- Context/Background: in what situation
- Source/Stimulus: what happens
- Metric/Acceptance Criteria: what metric defines success (e.g., p95 < 200ms, error rate < 0.1%)

## 4) Quality scenario (long form, only when needed)

A more precise form:

- Source (stimulus source)
- Stimulus
- Artifact (target)
- Environment (conditions)
- Response
- Response measure (measurement)

## 5) Boundary sketch (C4-level is enough)

If you cannot draw, text is acceptable.

### Context (relationship with external world)

- Actors: who uses it
- External systems: what it integrates with
- System under change: the box you change in this task

### Container (large internal boxes)

- App/Service/CLI/DB/Queue, etc.
- Communications between boxes (HTTP, gRPC, DB, file I/O)

## 6) Minimal Clean Architecture mapping

- Inner/core code must not know outer types/exceptions (HTTP/DB/framework).
- Convert to DTOs at the boundary before passing inward.
- Translate external exceptions into your domain errors at the boundary (do not leak vendor exceptions inward).

When unsure:

- boundary design → `$architecture-boundaries`
- error translation → `$error-handling`

## 7) Test List seed (handoff to TDD)

A Test List is not “write all tests first”. It is a plan: list variants and complete them one by one.

- basic case
- edge cases (empty/max/missing)
- failure paths (external I/O failure, permissions, consistency violations)
- checks that existing behavior is not broken

Next step: invoke `$test-driven-development` and proceed one item at a time.
