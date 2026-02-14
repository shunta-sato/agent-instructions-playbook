# tonemana-catalog reference

## Definition fixed for this repository

- Tone & Manner means a consistency rule-set across visual design and writing style.
- Tone is atmosphere (impression, temperature, color mood), not persona.
- Manner is explicit rules: typography, spacing unit, punctuation, emoji policy, and wording constraints.
- Use `writing_style`, `copy_style`, or `text_rules` for text constraints. Do not use prohibited terminology.

## Why preview HTML is mandatory

A comparable shelf only works when humans can see each pattern side by side. YAML/JSON values are machine-friendly, but visual mismatches are easier to catch in a style-tile-like preview.

## Default 7 patterns (short differences)

1. `neutral-minimal`: safe default, low decoration.
2. `trust-corporate`: high trust, conservative contrast and spacing.
3. `warm-friendly`: softer colors, approachable copy.
4. `modern-tech`: crisp contrast, sharp rhythm.
5. `bold-energetic`: strong accents, campaign-like emphasis.
6. `premium-elegant`: restrained palette, generous whitespace.
7. `natural-organic`: natural hues, gentle texture and phrasing.

## Source of truth and file roles

- `catalog_index.yaml` is the single source of truth for available pattern IDs and labels.
- Humans review `tonemana/catalog/previews/index.html` first.
- AI tools consume structured files under `tonemana/catalog/patterns/*.yaml` and `tonemana/catalog/tokens/*`.
