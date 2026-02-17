---
name: uidesign-orchestrator
description: "Orchestrate end-to-end UI design evidence generation: ensure UIUX Pack exists, ensure Tone & Manner is selected and wired, then generate a deterministic UIDesign Pack (tokens snapshot + HTML previews + review notes). Always open references/uidesign-orchestrator.md."
metadata:
  short-description: uiux → tonemana → uidesign (orchestration)
---

## Purpose

This is an orchestration wrapper that produces a reviewable UI styling bundle.

It ensures:
1) UIUX Pack exists and is fill-free
2) Tone & Manner assets exist (catalog + project tonemana pack)
3) UIUX Pack is wired to Tone & Manner via `meta.tone_and_manner`
4) UIDesign Pack is generated via `uidesign-flow`

This skill does not change information architecture (IA). IA changes belong to `uiux-core`.

## Workflow (high-level)

1) Preflight: locate or create a UIUX Pack
2) Ensure catalog exists (`tonemana-catalog`)
3) Ensure tone-and-manner pack + UIUX wiring (`tonemana-apply`)
4) Generate/update UIDesign Pack (`uidesign-flow`)
5) Report what changed and where humans should review

## Required completion message

Always include:
- `uiux/<pack>/previews/flow-map.html` (transition agreement entry point)
- `uidesign/<pack>/previews/index.html` (visual styling review entry point)
- `tonemana/catalog/previews/index.html` (mention UI-based 7-pattern switching)
- A short reminder: agree transitions first, then compare tone-and-manner in Review Mode (`Export JSON/Markdown`).
