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
