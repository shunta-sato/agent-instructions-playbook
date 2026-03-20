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

- **ありがち:** routing 後に optional スキル一覧を追ってしまい、必須 branch 判定がぼやける。  
  **代わりに:** 「trigger が立った branch だけ必須」を維持し、trigger 無し branch は実行しない。
- **ありがち:** low risk を固定して必要 branch を回避する。  
  **代わりに:** API/挙動/UI/並行性/境界変更が見えた時点で risk を再判定し、必要 branch を追加する。
- **ありがち:** verify 結果の良し悪し判定まで dev-workflow で抱え込む。  
  **代わりに:** dev-workflow は「必要な verify 深度の指定」までに限定し、最終判定は `$quality-gate` に委譲する。

## Output expectation

- Output must make the required route obvious:
  - selected risk and rationale
  - triggered required branches
  - verification depth to run before gate
- Final submit/no-submit judgment belongs to `$quality-gate`.
