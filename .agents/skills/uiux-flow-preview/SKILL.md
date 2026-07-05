---
name: uiux-flow-preview
description: "Use when a UIUX Pack needs a transition-map preview from ui_spec.json with pan/zoom, minimap, focus traversal, and Review Mode."
metadata:
  short-description: Transition map preview with pan/zoom + focus review
  requires:
    - references/uiux-flow-preview.md
    - templates/previews/flow-map.css
    - templates/previews/flow-map.html
    - templates/previews/flow-map.js
    - templates/previews/flow-map_focus.js
    - templates/previews/flow-map_minimap.js
    - templates/previews/flow-map_panzoom.js
    - templates/previews/review/review.css
    - templates/previews/review/review_export.js
    - templates/previews/review/review_store.js
    - templates/previews/review/review_ui.js
---

## Purpose

Create a static, review-ready transition map (`flow-map.html`) for UIUX Packs so teams can agree on information architecture before visual polish.

## When to use

- UIUX Pack has multiple screens and static flow diagrams are hard to review.
- You need node/edge-level Review Mode comments on transitions.
- You need a local `file://`-openable HTML preview without CDN dependencies.

## Workflow

1) Open `references/uiux-flow-preview.md`.
2) Read `uiux/<pack>/ui_spec.json` and map:
   - `information_architecture.screens`
   - `information_architecture.navigation`
   - `information_architecture.decision_points`
3) Copy templates into `uiux/<pack>/previews/` if missing.
4) Embed `window.UIUX_SPEC = {...}` directly in `flow-map.html` (no fetch).
5) Keep Review Mode assets local (`previews/review/*`).
6) Ensure pan/zoom updates dispatch `rv:viewportChanged` so review pins track transformed elements.

## Output expectation

- `uiux/<pack>/previews/flow-map.html` exists, is `file://`-openable, and embeds `window.UIUX_SPEC` directly (no fetch).
- The preview reflects `information_architecture.screens`, `.navigation`, and `.decision_points` from `ui_spec.json`.
- Review Mode assets (`previews/review/*`) are local, with no CDN dependencies.
- Pan/zoom interactions dispatch `rv:viewportChanged` so review pins track transformed elements.
