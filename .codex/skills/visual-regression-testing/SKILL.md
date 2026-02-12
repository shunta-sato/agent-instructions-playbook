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
