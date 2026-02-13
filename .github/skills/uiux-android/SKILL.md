---
name: uiux-android
description: "Android adapter for uiux-core. Adds Android-specific overrides and checks while preserving deterministic UIUX Pack artifact names."
metadata:
  short-description: Android UI/UX adapter for UIUX Pack
---

## Purpose

Apply Android-specific constraints/checks to an existing UIUX Pack.

## When to use

- `ui_contract.yaml` includes `android` in platforms.
- Android UI flows/components/navigation are in scope.

## How to use

1) Open `references/uiux-android.md`.
2) Assume UIUX Pack already exists (created by `$uiux-core`).
3) Update only:
   - `ui_contract.yaml` under `platform_overrides.android`
   - `auto_review.json` by adding checks with `android.` prefix.
4) Do not add new artifact names.
