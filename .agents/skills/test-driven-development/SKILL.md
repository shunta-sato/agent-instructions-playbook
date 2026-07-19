---
name: test-driven-development
description: "Use when doing TDD or when dev-workflow routes implementation through a Test List."
metadata:
  short-description: Test-driven development workflow
  requires:
    - references/test-driven-development.md
---

## Purpose

Use this skill to keep TDD as a repeatable procedure: you do not “jump ahead” into a large implementation.

The workflow is: **Test List → pick one → Red → Green → Refactor → update the list → repeat**.

## When to use

Use this skill when:

- You are adding new behavior and can drive it from tests.
- You are about to refactor and want tests to protect the behavior.
- You want to keep changes small and verifiable.

## How to use

0) Open `references/test-driven-development.md`. Start from the template.

1) Write a Test List first (3–10 items). Seed it from acceptance criteria or Definition of Done when available, and seed/bound the case list with `$unit-test-design` (risk tier, partitions/boundaries, stop criteria). Pick the smallest item.

2) Red: write the failing test with a clear name and intent.
   - Place the test where `$project-structure` conventions put it (unit test beside its module, integration test in the test directory). Never accumulate tests in an entrypoint file such as `main.rs`.

3) Green: implement the simplest code to pass.

4) Refactor: improve readability / modularity while keeping tests green. If `implementation-economy` is active, stay within the complexity budget or update the audit before continuing.

5) Repeat: update the Test List (split or reorder), then go back to step 2.

## Output expectation

- Always show the current Test List and which item you are implementing now.
- Keep each iteration small; avoid combining multiple behaviors in one step.
