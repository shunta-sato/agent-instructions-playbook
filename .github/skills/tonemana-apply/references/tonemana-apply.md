# tonemana-apply reference

## Selection flow

- Do not show all seven patterns first.
- Propose three candidates based on touchpoints and constraints, then confirm one pattern id.
- Keep decision load low; use concise tradeoff notes.

## Human feedback recording

Use `review_notes.md` as the structured place for human review comments.
Record gaps under fixed buckets so adjustments are traceable:

- color
- spacing
- typography
- corner_radius
- shadow
- photography
- iconography
- writing_style

Every note should point to a concrete target by ID, file path, or heading so edits are unambiguous.

## Override policy

- Keep catalog assets immutable.
- Store only minimal overrides in `tonemana_spec.json` (`tokens_patch`, `writing_style_patch`).
- Never mutate source pattern templates when applying to a specific pack.

## UIUX wiring (required)

When applying a pattern to a project, update the target UIUX Pack `ui_spec.json` to include this canonical block:

```json
{
  "meta": {
    "tone_and_manner": {
      "pattern_id": "<selected_pattern_id>",
      "tonemana_spec_ref": "tonemana/YYYYMMDD-<slug>/tonemana_spec.json",
      "token_refs": {
        "json": "tonemana/catalog/tokens/<selected_pattern_id>.tokens.json",
        "css": "tonemana/catalog/tokens/<selected_pattern_id>.tokens.css"
      }
    }
  }
}
```

Rules:

* `pattern_id` must match the catalog id
* token_refs must point to catalog `*.tokens.*`
* do not write token values into ui_spec.json (reference only)
