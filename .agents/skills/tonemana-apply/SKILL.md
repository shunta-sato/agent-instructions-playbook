---
name: tonemana-apply
description: "Apply a selected Tone & Manner pattern to an existing UIUX Pack by producing a versioned Tonemana Pack and wiring references into UIUX artifacts. Use when a human has selected, or asks to choose and apply, a tone/manner pattern for a UI project."
metadata:
  short-description: Apply tone/manner choice to UIUX Pack
  resources:
    - references/tonemana-apply.md
  templates:
    - templates/auto_review.json
    - templates/diff_summary.md
    - templates/review_notes.md
    - templates/tonemana_contract.yaml
    - templates/tonemana_spec.json
---

# tonemana-apply

## Goal
Freeze one Tone & Manner decision as a versioned pack and apply it to the UIUX pack via references.
Treat tone as atmosphere and manner as explicit rules. Keep text constraints under writing_style/copy_style/text_rules.

## Inputs
- Required: `selected_pattern_id`, `uiux_pack_path`
- Optional: `overrides`, `touchpoints`

## Output expectation
- `tonemana/YYYYMMDD-<slug>/tonemana_contract.yaml`
- `tonemana/YYYYMMDD-<slug>/tonemana_spec.json`
- `tonemana/YYYYMMDD-<slug>/auto_review.json`
- `tonemana/YYYYMMDD-<slug>/diff_summary.md`
- Updates UIUX pack: `ui_contract.yaml`, `ui_spec.json`, `diff_summary.md`

## Steps

Open `references/tonemana-apply.md` when running the selection flow and wizard questions below.

1) Ensure catalog exists (`tonemana/catalog/`). If missing, run tonemana-catalog behavior (create from templates).
2) Create `tonemana/YYYYMMDD-<slug>/` pack.
3) Update UIUX pack files to reference the chosen pattern and pack.
4) Write a short diff summary.

## Wizard (max 5 questions)
1) Confirm selected pattern id (one of 7)
2) Confirm touchpoints in scope
3) Confirm fixed assets (brand colors/fonts)
4) Confirm writing style constraints (polite/neutral/casual)
5) Confirm accessibility baseline
