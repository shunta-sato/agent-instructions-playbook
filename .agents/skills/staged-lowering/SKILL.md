---
name: staged-lowering
description: "Staged lowering workflow for constrained code synthesis. Use when implementing low-level or strict-constraint code (kernels, SIMD/intrinsics, alignment/padding rules, codegen/DSLs, strict ABI or hardware APIs), or when direct implementation repeatedly fails to compile/test. Produces a small IR/DSL sketch and lowers it in 3–5 passes with per-pass compile/test feedback and a verification log."
metadata:
  short-description: Staged lowering for constrained code
---

## Purpose

Use this skill to implement constrained code reliably by *reducing the problem before writing final code*:
define a small IR/DSL sketch, then translate it into production code in staged passes with verification after each pass.

## When to use

Use this skill when:
- you must follow strict low-level constraints (alignment/padding, memory layout, ABI, intrinsics, kernel-style pipelines)
- you are building or changing a DSL/codegen/transpiler, or a boundary with a strict API surface
- you keep hitting compile/test failures and the fix path is becoming guessy

## How to use

0) Open `references/staged-lowering.md` and follow the template.

1) Write a **Staged Lowering Plan**:
   - Hard constraints (non-negotiable)
   - IR/DSL sketch (minimal, structured)
   - Pass plan (3–5 passes)
   - Per-pass verification commands (compile/lint/unit tests)

2) Implement pass-by-pass:
   - Do not proceed until the current pass compiles/tests.
   - Keep the structure stable; change only what the current pass owns.

3) Record a **Per-pass Verification Log** (commands + key results).

4) If runtime behavior changes, invoke `$observability`.
   If you need help with comment/constant rules, invoke `$code-readability`.

## Output expectation

- The final output includes:
  - Staged Lowering Plan (filled)
  - Per-pass Verification Log
- The implementation keeps responsibilities separated by pass (no mixed concerns).
- Magic values are replaced with named constants/enums, and comments explain intent/assumptions/pitfalls.
