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

## Gotchas

- **ありがち:** bugfix なのに再現手順・失敗証拠を残さずに修正へ進む。  
  **代わりに:** `$bug-investigation-and-rca` を先に実行し、再現ログ/失敗テスト/スタックトレースのどれかを記録してから実装する。
- **ありがち:** UI 変更でスナップショット差分を確認せず、baseline をまとめて更新する。  
  **代わりに:** `$visual-regression-testing` を実行し、意図した差分だけを確認して baseline 更新理由をレポートに明記する。
- **ありがち:** 並行処理を触ったのに通常テストだけで完了扱いにする。  
  **代わりに:** `$concurrency-core` と `$thread-safety-tooling` を呼び、終了条件・キャンセル経路・競合検証（TSan 等）の実行結果を残す。
- **ありがち:** テストが弱い legacy 箇所を直接リファクタして挙動を壊す。  
  **代わりに:** `$working-with-legacy-code` を先に適用し、characterization test/決定論化 seam を作ってから変更する。
- **ありがち:** verify コマンドを省略して「時間がない」で終了する。  
  **代わりに:** スキップした各コマンドに対して「なぜ今実行不能か」と「他者が再現できる実行手順」を最終出力に必ず書く。
- **ありがち:** リスクを low で固定して必要 branch を回避する。  
  **代わりに:** 変更が API/挙動/UI/並行性/境界に触れた時点で risk を normal/high に再判定し、必須 branch を追加実行する。

## Output expectation

- Your final output must follow AGENTS.md “Required final output”.
- Any skipped checks must include a reason and a reproducible procedure.
