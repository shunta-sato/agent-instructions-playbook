---
name: tonemana-catalog
description: "Create or update a comparable Tone & Manner catalog with 7 default patterns, tokens, and preview HTML. Use before choosing a visual/voice pattern for UIUX or UIDesign work."
metadata:
  short-description: Tone & Manner catalog + previews
  requires:
    - references/tonemana-catalog.md
    - templates/catalog_index.yaml
    - templates/patterns/bold-energetic.yaml
    - templates/patterns/modern-tech.yaml
    - templates/patterns/natural-organic.yaml
    - templates/patterns/neutral-minimal.yaml
    - templates/patterns/premium-elegant.yaml
    - templates/patterns/trust-corporate.yaml
    - templates/patterns/warm-friendly.yaml
    - templates/previews/index.html
    - templates/previews/style-tile.css
    - templates/tokens/bold-energetic.tokens.css
    - templates/tokens/bold-energetic.tokens.json
    - templates/tokens/modern-tech.tokens.css
    - templates/tokens/modern-tech.tokens.json
    - templates/tokens/natural-organic.tokens.css
    - templates/tokens/natural-organic.tokens.json
    - templates/tokens/neutral-minimal.tokens.css
    - templates/tokens/neutral-minimal.tokens.json
    - templates/tokens/premium-elegant.tokens.css
    - templates/tokens/premium-elegant.tokens.json
    - templates/tokens/trust-corporate.tokens.css
    - templates/tokens/trust-corporate.tokens.json
    - templates/tokens/warm-friendly.tokens.css
    - templates/tokens/warm-friendly.tokens.json
---

# tonemana-catalog

## Goal
Create a reusable, comparable Tone & Manner catalog inside the project.
Tone = atmosphere (visual impression). Manner = explicit rules. Keep terminology aligned with writing_style/copy_style/text_rules.

## Inputs
- Required: `project_name`, `primary_touchpoints`
- Optional: `existing_brand_assets`, `accessibility_target`

## Output expectation
- `tonemana/catalog/catalog_index.yaml`
- `tonemana/catalog/patterns/*.yaml`
- `tonemana/catalog/tokens/*.tokens.json`
- `tonemana/catalog/tokens/*.tokens.css`
- `tonemana/catalog/previews/index.html`

## How to run
- Generate `tonemana/catalog/` from templates.
- Keep IDs stable. Do not delete user-added patterns.

## Wizard (max 5 questions)
1) What touchpoints are in scope? (product-ui / marketing-site / sns / docs)
2) Any fixed brand assets? (logo, primary color, font)
3) Writing style baseline? (polite / neutral / casual)
4) Accessibility baseline? (WCAG2.2-AA default)
5) Light/dark mode needed? (yes/no)

## Final response
- The catalog and preview HTML.
