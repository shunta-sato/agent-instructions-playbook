---
name: uiux-core
description: "Platform-agnostic UI/UX design + review contract. Produces a deterministic UIUX Pack (ui_contract.yaml, ui_spec.json, auto_review.json, diff_summary.md). Always open references/uiux-core.md."
metadata:
  short-description: UI/UX core contract + deterministic review bundle
---

## Purpose

Define a platform-agnostic UI/UX contract and review workflow that always produces a deterministic UIUX Pack.

## When to use

- New UI creation
- UI refactors
- Navigation or IA changes
- Copy/content changes
- State, error, and recovery design changes

## How to use

1) Open `references/uiux-core.md`.
2) Choose output folder: `uiux/YYYYMMDD-<slug>/` (or `uiux/.config` `output_dir` override when present).
3) Copy templates into the output folder if missing.
4) Fill `ui_contract.yaml` first (constraints + rules).
5) Generate/update `ui_spec.json`.
6) Compute/update `auto_review.json`.
7) Write `diff_summary.md`.
8) If platform-specific constraints are needed, invoke `$uiux-android`, `$uiux-ios`, and/or `$uiux-web`.

## Output expectation

The UIUX Pack exists with all four artifacts, and `auto_review.json` separates machine checks and human review items with explicit `pass`/`warn`/`fail`/`unknown` results.
