---
name: uiux-flow-preview
description: "Generate a Google Map-like transition review preview (flow-map.html) from ui_spec.json with pan/zoom, minimap, focus traversal, and Review Mode integration. Always open references/uiux-flow-preview.md."
metadata:
  short-description: Transition map preview with pan/zoom + focus review
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
