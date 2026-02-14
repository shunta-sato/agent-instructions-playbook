---
name: uidesign-flow
description: "Bridge an approved tone-and-manner decision into concrete UI styling via tokens + visual previews. Produces a deterministic UIDesign Pack (uidesign_contract.yaml, uidesign_spec.json, auto_review.json, diff_summary.md, review_notes.md, tokens/*, previews/*). Always open references/uidesign-flow.md."
metadata:
  short-description: tonemana → tokens → component+screen previews
---

## Purpose

Turn a tone-and-manner decision into **reviewable UI styling evidence**:
- snapshot tokens used for styling
- render a component preview page
- render 3 representative screens
- produce a deterministic review bundle (UIDesign Pack)

This skill does **not** change IA (screens, navigation, decision points). That belongs to uiux-core.

## When to use

- A UIUX Pack exists but “it works but looks off”
- You need a stable bridge artifact for human feedback
- You want consistent review outputs across Android/iOS/Web projects

## Workflow

1) Locate the target UIUX Pack folder (uiux/YYYYMMDD-<slug>/).
2) Verify `ui_spec.json` includes `meta.tone_and_manner` with:
   - `pattern_id`
   - `tonemana_spec_ref`
   - `token_refs.json` and `token_refs.css`
   If missing, invoke `$tonemana-apply` first (do not proceed).
3) Create output folder `uidesign/YYYYMMDD-<slug>/` (or `uidesign/.config` output_dir override when present).
4) Copy templates into the output folder if missing.
5) Snapshot tokens into:
   - `tokens/resolved.tokens.json`
   - `tokens/resolved.tokens.css`
   (Copy from `meta.tone_and_manner.token_refs.*` so previews are stable.)
6) Generate visual previews (HTML, no external deps):
   - `previews/components.html`
   - `previews/screens/entry.html`
   - `previews/screens/form.html`
   - `previews/screens/status.html`
   - `previews/index.html` as a hub
7) Fill `uidesign_contract.yaml` then update `uidesign_spec.json`.
8) Compute/update `auto_review.json` (machine checks vs human judgement).
9) Write `diff_summary.md`.
10) Hand off to humans:
   - Humans write feedback into `review_notes.md` using the provided structure.

## Output expectation

`uidesign/YYYYMMDD-<slug>/` exists with all required artifacts and previews, and the pack is review-ready without additional tooling.
