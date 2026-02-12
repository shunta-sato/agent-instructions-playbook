---
name: architecture-boundaries
description: "Clean Architecture boundaries handbook (dependency direction, DIP, DTO, boundary placement). Use when designing or reviewing boundaries. Always open references/architecture-boundaries.md and cite headings."
metadata:
  short-description: Architecture boundaries (Clean Architecture)
---

## Purpose

Use this skill to design boundaries that prevent change ripple: keep the core logic independent from volatile outer layers (UI/DB/frameworks/services).

It follows Clean Architecture ideas: dependency direction, dependency inversion, and simple data transfer across boundaries.

## When to use

Use this skill when:

- You are introducing or changing an integration with a DB, external service, or framework.
- You need to define a new interface boundary, wrapper, or adapter.
- You are reviewing code that leaks framework types or vendor errors into core logic.

## How to use

0) Open `references/architecture-boundaries.md`. Select **1–3 relevant headings** and cite them by heading name in your reasoning.

1) Identify the boundary crossing points (where external things meet your code).

2) Ensure dependency direction is outward → inward:
   inner code should not import outer-layer types.

3) Define a small interface in the inner layer and implement it in the outer layer (DIP).

4) Use simple DTOs for boundary data. Convert at the boundary; do not pass framework objects inward.

## Output expectation

- Provide a boundary diagram or a short mapping (outer types → DTO → core types).
- Show how errors are translated at the boundary.
