---
name: implementation-economy
description: "Use when a change introduces a persistent abstraction, wrapper, adapter, layer, or generic infrastructure, or when supporting implementation risks becoming larger than the remaining user-facing behavior. Do not use for a local helper whose purpose is obvious and confined to the current feature."
metadata:
  short-description: Scope-inversion and abstraction budget
---

## Purpose

Keep implementation cost proportionate to the capability and its expected
maintenance horizon. This skill is not a required audit for ordinary local code.

## When to use

Use when at least one applies:

- a persistent class, module, interface, wrapper, adapter, or indirection is new;
- generic infrastructure is proposed for one immediate use;
- support code, harness work, or preparatory refactoring approaches the size of
  the remaining user-facing implementation;
- a review asks for broader generalization or another abstraction layer.

A small local helper, ordinary reuse, or test fixture does not trigger this skill
unless it creates a lasting boundary or scope-inversion risk.

## How to use

1. State the user-facing implementation still missing.
2. Set a compact budget: production files/lines, persistent abstractions, and
   support work.
3. For each persistent abstraction, give one sentence covering the present
   consumer, complexity removed, and why local code is insufficient.
4. Prefer deletion, reuse, inlining, or a local implementation when the expected
   maintenance horizon does not justify a durable boundary.
5. Activate the scope-inversion stop when support work becomes larger than the
   remaining capability. Publish the current reviewable state and request a scope
   decision rather than continuing.
6. After implementation, list only persistent additions and mark
   `keep | inline | merge | delete | defer`.

Record this in the active plan or PR. A standalone budget/audit artifact is not
required unless another tool consumes it or the decision is material and durable.

## Output expectation

Return the remaining user-facing work, compact budget, persistent-abstraction
decisions, actual support cost, and whether the scope-inversion stop activated.
