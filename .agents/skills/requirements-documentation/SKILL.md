---
name: requirements-documentation
description: "Requirements documentation workflow (requirements brief / spec / SRS). Use to write or update requirement docs with IDs, rationale, acceptance criteria, verification method, and traceability. Always open references/requirements-documentation.md first."
metadata:
  short-description: Requirements documentation
---

## Purpose

Use this skill to produce or update requirement documents that remain verifiable later.

It standardizes:

- requirement IDs
- rationale (“why”)
- acceptance criteria (measurable)
- verification method (test/review/measurement/monitoring)
- traceability (requirements ↔ design ↔ tests)

## When to use

Use this skill when:

- the task changes external behavior and requires requirement updates, or
- you need to create an initial requirements brief/spec for a feature.

## How to use

1) Open `references/requirements-documentation.md`.

2) Choose the smallest doc that fits:
   - Requirements Brief for small changes
   - Requirements Spec for larger changes

3) Write 1–5 requirements first, each with acceptance criteria and verification method.

4) Add a minimal trace table if the change spans multiple components.

## Output expectation

- Each requirement is testable/verifiable.
- Document changes are minimal but sufficient; no large rewrites without necessity.
