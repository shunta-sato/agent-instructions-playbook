# tonemana-apply

Select one Tone & Manner pattern, generate a versioned Tonemana Pack, and apply references to a UIUX Pack.

## Workflow

1) Narrow to three candidate patterns, then confirm one `selected_pattern_id`.
2) Create `tonemana/YYYYMMDD-<slug>/` artifacts from templates.
3) Apply `tone_and_manner` references into `ui_contract.yaml` and `ui_spec.json`.
4) Append one Tone & Manner line to UIUX `diff_summary.md`.
5) Record structured human feedback in `review_notes.md`.
