---
name: test-driven-development
description: "Use when TDD is explicitly requested, required by the applicable project policy, or selected as the task's test-first route. Preserve Red-Green evidence without test-count quotas. Merely adding or editing tests does not trigger this skill."
metadata:
  short-description: Test-driven development workflow
  requires:
    - references/test-driven-development.md
---

## Purpose

Use this skill to keep TDD as a repeatable procedure: you do not “jump ahead” into a large implementation.

The workflow is: **Test List → pick one → Red → Green → Refactor → update the list → repeat**.

## When to use

Use this skill when TDD is explicitly requested, required by the applicable
project policy, or selected as the task's test-first route. Ordinary code/test
edits and behavior-preserving refactoring do not automatically select TDD.
They still require the acceptance and regression proof selected by `dev-workflow`.
An explicit TDD request retains the Red → Green sequence.

## How to use

0) Open `references/test-driven-development.md`. Start from the template.

1) Write a Test List from acceptance criteria, regressions, and realistic boundary failures. There is no minimum or maximum item quota; one item is sufficient when it covers the required behavior. Do not omit required safety or repository checks.
   - Use `unit-test-design` only when strategy, boundary partitions, coverage policy, test doubles, or flakiness requires judgment. A straightforward regression test does not require another skill.
   - Pick the smallest decisive item; do not invent cases to fill a list.

2) Red: write and run the failing test; confirm it fails for the expected reason before changing production code. If execution is unavailable, report the missing evidence rather than claiming Red or Green.
   - Follow existing repository test placement. Use `project-structure` only for a placement decision or blocking structure finding; do not accumulate tests in an entrypoint such as `main.rs`.

3) Green: implement the simplest code to pass.

4) Refactor only when a scoped improvement is needed; keep tests green and avoid unrelated cleanup. If `implementation-economy` is active, stay within its budget or update the audit before continuing.

5) Update the Test List as evidence changes and repeat for remaining required cases. Stop when acceptance, regressions, and realistic failure paths are covered; keep the routed final verification.

## Output expectation

- Show the Test List initially, when its scope materially changes, and at handoff; do not repeat the unchanged list after every tool call.
- Report the selected item, actual Red/Green results, and remaining cases or limits.
- Keep each iteration small; avoid combining multiple behaviors in one step.
