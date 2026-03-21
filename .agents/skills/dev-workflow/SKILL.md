---
name: dev-workflow
description: "MANDATORY routing workflow for any code/test change: classify risk and execute only the required triggered branches, then hand off to quality-gate."
metadata:
  short-description: Risk-routed dev workflow
---

## Purpose

This skill is the router for implementation work in this repository.

It decides **which branch workflows are required** for the current task.

## When to use

Use this skill **for any task that changes code and/or tests**. It is mandatory.

## How to use

0) Open `references/dev-workflow.md` and fill it top-down.

1) Route by risk first (`low` | `normal` | `high`) and record why.
   - The output of this step is: required planning depth + required verification depth.

2) Apply **required trigger-based branches** only when facts trigger them.
   - bug/regression/flaky/crash/hang → `$bug-investigation-and-rca`
   - structural boundary/refactor change → `$code-smells-and-antipatterns`
   - concurrency/parallelism change → `$concurrency-core` + `$thread-safety-tooling` (+ variant skills)
   - runtime behavior change → `$observability`
   - strict-constraint low-level code or repeated compile/test loops → `$staged-lowering`
   - legacy/no reliable tests/nondeterminism → `$working-with-legacy-code`
   - UI change → `$visual-regression-testing` + matching platform visual skill(s)
   - C++ headers touched → `$code-readability` (Doxygen gate)

3) Execute implementation with the selected route + required branches.

4) Run canonical verification at the depth required by the selected risk route.

5) Hand off to `$quality-gate` for final submission readiness.

## Gotchas

- **Common pitfall:** following optional skill lists after routing and blurring required-branch decisions.  
  **Instead:** maintain only-triggered branches as required and do not execute untriggered branches.
- **Common pitfall:** forcing low risk and bypassing required branches.  
  **Instead:** re-evaluate risk when API/behavior/UI/concurrency/boundary changes appear, and add required branches.
- **Common pitfall:** trying to make pass/fail decisions in dev-workflow.  
  **Instead:** limit dev-workflow to specifying required verification depth; delegate final judgment to `$quality-gate`.

## Output expectation

- Output must make the required route obvious:
  - selected risk and rationale
  - triggered required branches
  - verification depth to run before gate
- Final submit/no-submit judgment belongs to `$quality-gate`.
