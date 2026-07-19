---
name: unit-test-design
description: "Use when designing or reviewing unit tests: deciding test cases, boundaries, or coverage a change needs, choosing the E/S/H risk tier, deciding mock vs fake, judging whether a suite is over- or under-built, or fixing flaky/slow unit tests. Do not use for integration/contract/E2E strategy beyond the delegation decision itself, embedded NFR measurement harnesses, or TDD loop mechanics."
metadata:
  short-description: Risk-tiered unit test design
  requires:
    - references/unit-test-case-design.md
    - references/unit-test-operations.md
---

## Purpose

Use this skill to size unit tests right through risk tiers, so effort goes
toward tests that reduce real defect risk instead of maximizing case count
or coverage percentage.

Headline rule: by default, test the **specified behavior + equivalence
partitions + 2-value boundary values**. Escalate to 3-value boundaries,
decision tables, state transitions, or Mutation Testing only for high-risk
areas. There is no repo-wide 100% coverage target — changed code is judged
strictly, and every test case must reduce at least one distinct risk.

## When to use

Use this skill when:
- Designing or reviewing unit tests
- Deciding which cases, boundaries, or coverage a change needs
- Deciding the E/S/H risk tier for a target
- Deciding mock vs fake for a dependency
- Judging whether an existing test suite is over- or under-built
- Fixing flaky or slow unit tests

Do not use this skill for:
- Integration/contract/E2E strategy, beyond the delegation decision itself
- Embedded NFR measurement harnesses — see `$embedded-nfr-harness-design`
- TDD process mechanics — `$test-driven-development` owns the Red/Green
  loop; this skill supplies **which cases** the Test List should contain

## Boundaries

- `test-driven-development` owns the Red/Green/Refactor loop.
- `bug-investigation-and-rca` owns reproduction and root-cause analysis;
  this skill's §11 regression-fix criteria apply to the test it produces.
- `code-readability` owns test readability details (naming polish,
  structure clarity).
- `comment-discipline` owns what test names carry as comments (the *What*).

## How to use

0) Open `references/unit-test-case-design.md` and
   `references/unit-test-operations.md`.
1) Classify the target E / S / H using the §2 risk formula (impact x
   likelihood, ≥6 is high-risk; some categories are high-risk regardless of
   score).
2) Derive cases from the §3 design-basis matrix: specified results,
   equivalence partitions, boundary values, condition combinations, state
   transitions.
3) Apply the §13 stop criteria — add a case only when it adds at least one
   of the 8 listed items.
4) Check the result against the PR review checklist in
   `references/unit-test-case-design.md`.
5) For coverage gates, test-double choice, isolation/speed/flakiness rules,
   test-code style, and regression-fix/advanced-technique criteria, use
   `references/unit-test-operations.md` (§7-§12).

## Output expectation

- State the E/S/H classification with a one-line justification when the
  tier is not obvious.
- List cases mapped to the partition/boundary/rule/transition each one
  covers.
- State which stop criterion each case satisfies, or record an
  accepted-risk statement for anything left untested.
- For test-bearing changes, report the checklist result (pass, or
  findings).
