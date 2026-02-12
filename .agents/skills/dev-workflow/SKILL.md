---
name: dev-workflow
description: "MANDATORY end-to-end workflow for any code/test change: requirements → design → test list/TDD → implement → verify (build/format/static-analysis/tests) → quality gate. Enforces code-readability, modularity, architecture-boundaries, and error-handling from the start."
metadata:
  short-description: End-to-end dev workflow
---

## Purpose

This skill is the default operating procedure for implementing changes in this repository.

It turns a request into an implementable plan with verifiable outcomes:

requirements → design → test design → implementation → verification → final gate.

## When to use

Use this skill **for any task that changes code and/or tests**. It is mandatory.

## How to use

0) Open `references/dev-workflow.md` and follow it step-by-step.

1) Write the Change Brief and the Requirements (EARS “shall” + acceptance criteria).

1.5) If runtime behavior changes, add an Observability Plan (logs/metrics/traces) and invoke `$observability` when unsure.

1.6) **Bugfix mode (required when task is a bug/regression/flaky/crash/hang):**
   - Invoke `$bug-investigation-and-rca`.
   - Do **not** implement the fix until reproduction/evidence is captured, a leading hypothesis is stated, and a verification plan exists.
   - If only a workaround is proposed, include a follow-up prevention task.

1.75) If the change is structural (new modules, boundary changes, refactors across layers), invoke `$code-smells-and-antipatterns`.

2) Create a Test List (3–10). Decide whether to proceed with TDD.
   - If doing TDD, explicitly invoke `$test-driven-development`.

2.5) **Concurrency & Performance check (mandatory):**
   - If concurrency/parallelism is introduced or changed: invoke `$concurrency-core` and `$thread-safety-tooling`.
   - If ROS2 code is affected: also invoke `$concurrency-ros2`.
   - If Android code is affected: also invoke `$concurrency-android`.
   - If runtime behavior changes: invoke `$observability`.
   - If performance targets are part of the goal: invoke `$nfr-iso25010`.

2.6) **Constrained / low-level synthesis check (mandatory when relevant):**
   - If you are implementing strict-constraint code (alignment/padding, SIMD/intrinsics, kernels, DSL/codegen, strict ABI/hardware APIs),
     or if the task repeatedly fails to compile/test: invoke `$staged-lowering` before large edits.

3) **Legacy check (mandatory):** if tests are missing or behavior is nondeterministic, explicitly invoke `$working-with-legacy-code` *before* refactoring.

4) **C++ header gate (mandatory):** if `.hpp` / `.h` is in scope, explicitly invoke `$code-readability` and apply the mandatory Doxygen rules.

5) Implementation:
   - For readability: invoke `$code-readability` when you need concrete guidance.
   - For modularity / coupling / boundaries: invoke `$modularity`.
   - For Clean Architecture boundaries: invoke `$architecture-boundaries`.
   - For error paths: invoke `$error-handling`.
   - For NFRs: invoke `$nfr-iso25010` when relevant.
   - If requirements docs must be updated: invoke `$requirements-documentation`.

6) Verification: run the repo’s canonical commands for build / format / static analysis / tests until green.

6.5) **UI verification (mandatory when UI changes):**
   - Invoke `$visual-regression-testing`.
   - Invoke the matching platform skill(s): `$visual-regression-ios`, `$visual-regression-android`, and/or `$visual-regression-web`.
   - Run repo-defined UI verify/record commands and include a UI Visual Verification Report with artifact paths.

7) Before submitting, explicitly invoke `$quality-gate` and keep fixing until it reports 0 findings.

## Output expectation

- Your final output must follow AGENTS.md “Required final output”.
- Any skipped checks must include a reason and a reproducible procedure.
