---
name: uiux-core
description: "Platform-agnostic UI/UX design + review contract. Produces a deterministic UIUX Pack (ui_contract.yaml, ui_spec.json, auto_review.json, diff_summary.md). Always open references/uiux-core.md; also open references/uiux-platform-adapters.md when the task targets web, iOS, or Android."
metadata:
  short-description: UI/UX core contract + deterministic review bundle
---

## Purpose

Define a UI/UX contract and review workflow that always produces a deterministic UIUX Pack.

## When to use

- New UI creation
- UI refactors
- Navigation or IA changes
- Copy/content changes
- State, error, and recovery design changes

## How to use

1) Open `references/uiux-core.md`.
2) If the task targets Web, iOS, or Android, open `references/uiux-platform-adapters.md` and apply only the matching platform section(s).
3) Choose output folder: `uiux/YYYYMMDD-<slug>/` (or `uiux/.config` `output_dir` override when present).
4) Copy templates into the output folder if missing.
5) Fill `ui_contract.yaml` first (constraints, rules, and any `platform_overrides`).
6) Generate/update `ui_spec.json`.
7) Compute/update `auto_review.json`, including platform-prefixed checks when applicable.
8) Write `diff_summary.md`.

## Output expectation

The UIUX Pack exists with all four artifacts, and `auto_review.json` separates machine checks and human review items with explicit `pass`/`warn`/`fail`/`unknown` results.
