---
name: uiux-ios
description: "iOS adapter for uiux-core. Adds iOS-specific overrides and checks while preserving deterministic UIUX Pack artifact names."
metadata:
  short-description: iOS UI/UX adapter for UIUX Pack
---

## Purpose

Apply iOS-specific constraints/checks to an existing UIUX Pack.

## When to use

- `ui_contract.yaml` includes `ios` in platforms.
- iOS UI flows/components/navigation are in scope.

## How to use

1) Open `references/uiux-ios.md`.
2) Assume UIUX Pack already exists (created by `$uiux-core`).
3) Update only:
   - `ui_contract.yaml` under `platform_overrides.ios`
   - `auto_review.json` by adding checks with `ios.` prefix.
4) Do not add new artifact names.
