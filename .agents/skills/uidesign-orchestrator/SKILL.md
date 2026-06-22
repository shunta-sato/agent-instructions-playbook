---
name: uidesign-orchestrator
description: "Use only for explicit end-to-end UI evidence orchestration across UIUX, Tone & Manner, and UIDesign packs. Do not trigger for ordinary single-step UIUX, Tone & Manner, or UIDesign work."
metadata:
  short-description: Explicit UI evidence orchestration
---

## Purpose

This skill coordinates the full UI evidence pipeline. It is explicit-only and is not a replacement for the individual UIUX, Tone & Manner, or UIDesign skills.

Use it only when the work must produce or verify all three connected artifacts:
- UIUX Pack
- Tone & Manner catalog/project pack
- UIDesign Pack

It also ensures the UIUX Pack is wired to Tone & Manner via `meta.tone_and_manner`. It does not change information architecture (IA); IA changes belong to `uiux-core`.

## When to use

Use only when the request explicitly calls for end-to-end orchestration or all connected UI evidence artifacts.

- The user asks for the full UI evidence pipeline, end-to-end orchestration, or all UI evidence artifacts.
- The request requires creating, verifying, and wiring together UIUX, Tone & Manner, and UIDesign outputs.
- A review program explicitly asks for this wrapper to coordinate the individual skills.

## When not to use

- For UIUX structure, IA, flows, wireframes, or transition agreement only, use `uiux-core`.
- For Tone & Manner cataloging, selection, or application only, use `tonemana-catalog` or `tonemana-apply`.
- For visual tokens, HTML previews, styling review notes, or UIDesign output only, use `uidesign-flow`.
- For copy tone, visual taste, or single-step design feedback that does not require the full artifact chain, use the relevant individual skill.
- Do not infer this orchestrator just because more than one UI skill could be useful.

## Workflow (high-level)

1) Preflight: locate or create a fill-free UIUX Pack.
2) Ensure the Tone & Manner catalog exists (`tonemana-catalog`).
3) Ensure the project Tone & Manner pack exists and UIUX wiring is present (`tonemana-apply`).
4) Generate or update the UIDesign Pack (`uidesign-flow`).
5) Report changed paths and the review order.

## Required completion message

Always include:
- `uiux/<pack>/previews/flow-map.html` (transition agreement entry point)
- `uidesign/<pack>/previews/index.html` (visual styling review entry point)
- `tonemana/catalog/previews/index.html` (mention UI-based 7-pattern switching)
- A short reminder: agree transitions first, then compare tone-and-manner in Review Mode (`Export JSON/Markdown`).
