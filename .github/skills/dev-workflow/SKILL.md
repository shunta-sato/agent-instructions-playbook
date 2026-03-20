---
name: dev-workflow
description: "MANDATORY risk-routed workflow for any code/test change: classify risk, run required branch checks, verify, then quality gate. Keeps low-risk paths light without dropping high-risk safeguards."
metadata:
  short-description: Risk-routed dev workflow
---

## Purpose

This skill is the default operating procedure for implementing changes in this repository.

It turns a request into an implementable plan with verifiable outcomes:

risk routing → requirements/design depth by risk → implementation → verification → final gate.

## When to use

Use this skill **for any task that changes code and/or tests**. It is mandatory.

## How to use

0) Open `references/dev-workflow.md` and follow it step-by-step.

1) **Route by risk first** (`low` | `normal` | `high`) and record why.

   **Low risk** (small/local, no behavior/API/concurrency/UI/legacy refactor):
   - Required: lightweight Change Brief, scoped requirement bullets, impacted tests, canonical verify command(s), `$quality-gate`.
   - Optional: `$test-driven-development`, `$code-readability`, `$modularity`, `$architecture-boundaries`, `$error-handling`.

   **Normal risk** (default for most tasks):
   - Required: full Change Brief + EARS requirements + acceptance criteria, Test List, canonical verify command(s), `$quality-gate`.
   - Optional: deeper design skills unless a trigger below makes them required.

   **High risk** (cross-boundary, runtime-behavior shift, broad refactor, strict constraints, safety/perf critical):
   - Required: full Change Brief, EARS requirements, explicit failure-path notes, test strategy, observability plan when runtime behavior changes, full verify chain (build/format/static-analysis/tests), `$quality-gate`.
   - Required when complex/long-running: `$execution-plans`.

2) Write requirements/design at the depth required by the selected risk route.

3) Apply trigger-based branches (required only when triggered):

   **Bugfix mode (required when task is a bug/regression/flaky/crash/hang):**
   - Invoke `$bug-investigation-and-rca`.
   - Do **not** implement the fix until reproduction/evidence is captured, a leading hypothesis is stated, and a verification plan exists.
   - If only a workaround is proposed, include a follow-up prevention task.

   **Structural-change scan (required when structural):**
   - If the change is structural (new modules, boundary changes, refactors across layers), invoke `$code-smells-and-antipatterns`.

   **Concurrency & performance (required when triggered):**
   - If concurrency/parallelism is introduced or changed: invoke `$concurrency-core` and `$thread-safety-tooling`.
   - If ROS2 code is affected: also invoke `$concurrency-ros2`.
   - If Android code is affected: also invoke `$concurrency-android`.
   - If runtime behavior changes: invoke `$observability`.
   - If performance targets are part of the goal: invoke `$nfr-iso25010`.

   **Constrained / low-level synthesis (required when triggered):**
   - If you are implementing strict-constraint code (alignment/padding, SIMD/intrinsics, kernels, DSL/codegen, strict ABI/hardware APIs),
     or if the task repeatedly fails to compile/test: invoke `$staged-lowering` before large edits.

   **Legacy check (required when triggered):**
   - If tests are missing or behavior is nondeterministic, explicitly invoke `$working-with-legacy-code` *before* refactoring.

   **C++ header gate (required when triggered):**
   - If `.hpp` / `.h` is in scope, explicitly invoke `$code-readability` and apply the mandatory Doxygen rules.

   **UI verification branch (required when triggered):**
   - If UI changes are in scope, invoke `$visual-regression-testing`.
   - Invoke matching platform skill(s): `$visual-regression-ios`, `$visual-regression-android`, and/or `$visual-regression-web`.
   - Run repo-defined UI verify/record commands and include a UI Visual Verification Report with artifact paths.

4) Create a Test List (3–10) for normal/high risk. For low risk, a compact impacted-test list is acceptable.
   - If doing TDD, explicitly invoke `$test-driven-development`.

5) Implementation:
   - For readability: invoke `$code-readability` when you need concrete guidance.
   - For modularity / coupling / boundaries: invoke `$modularity`.
   - For Clean Architecture boundaries: invoke `$architecture-boundaries`.
   - For error paths: invoke `$error-handling`.
   - For NFRs: invoke `$nfr-iso25010` when relevant.
   - If requirements docs must be updated: invoke `$requirements-documentation`.

6) Verification:
   - Low risk: run the minimal canonical command set that still validates the changed surface.
   - Normal/high risk: run full canonical chain for build / format / static analysis / tests until green.

7) Before submitting, explicitly invoke `$quality-gate` and keep fixing until it reports 0 findings.

## Output expectation

- Your final output must follow AGENTS.md “Required final output”.
- Any skipped checks must include a reason and a reproducible procedure.
