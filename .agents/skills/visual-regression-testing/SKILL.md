---
name: visual-regression-testing
description: "Run repo-defined UI snapshot verification, review visual diffs, update baselines only when intended, and produce a deterministic UI Visual Verification Report."
metadata:
  short-description: Tool-agnostic UI visual verification contract
---

## Purpose

Use this skill to enforce a consistent UI visual verification contract without hard-coding a specific test framework.

## When to use

- Any UI code changed (iOS/SwiftUI, Android/Compose/XML, web UI/components/styles).
- The request mentions pixel perfect, UI matches design, snapshot, or screenshot.

## How to use

1) Open `references/visual-regression-testing.md`.
2) Discover and run the repo’s canonical UI verify/record interface.
3) Review produced artifacts and compare against baselines/design mocks.
4) Update baselines only for intentional UI changes.
5) Output the required report format exactly.

## Gotchas

- **ありがち:** UI が変わっているのに snapshot verify を飛ばす。  
  **代わりに:** repo 定義の UI verify コマンドを実行し、差分の有無を必ず確認する。
- **ありがち:** 失敗した snapshot を原因確認せず一括で record する。  
  **代わりに:** 差分画像をレビューして「意図した変更のみ」を baseline に反映する。
- **ありがち:** レポートに artifact path がなく、レビュアーが再確認できない。  
  **代わりに:** compare 結果・更新有無・artifact の相対パスを出力フォーマットへ明記する。
- **ありがち:** デザイン差異を「テスト環境差」と決めつけて放置する。  
  **代わりに:** フォント/解像度/テーマ/ロケール差を切り分け、再現条件を記録してから判断する。
