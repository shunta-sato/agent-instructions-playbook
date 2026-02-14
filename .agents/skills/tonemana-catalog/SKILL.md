---
name: tonemana-catalog
description: Create or update a Tone & Manner catalog (7 default patterns) with preview HTML so humans can compare visually.
inputs:
  required:
    - project_name
    - primary_touchpoints
  optional:
    - existing_brand_assets
    - accessibility_target
outputs:
  - tonemana/catalog/catalog_index.yaml
  - tonemana/catalog/patterns/*.yaml
  - tonemana/catalog/tokens/*.tokens.json
  - tonemana/catalog/tokens/*.tokens.css
  - tonemana/catalog/previews/index.html
---

# tonemana-catalog

## Goal
Create a reusable, comparable Tone & Manner catalog inside the project.
Tone = atmosphere (visual impression). Manner = explicit rules. Keep terminology aligned with writing_style/copy_style/text_rules.

## How to run
- Generate `tonemana/catalog/` from templates.
- Keep IDs stable. Do not delete user-added patterns.

## Wizard (max 5 questions)
1) What touchpoints are in scope? (product-ui / marketing-site / sns / docs)
2) Any fixed brand assets? (logo, primary color, font)
3) Writing style baseline? (polite / neutral / casual)
4) Accessibility baseline? (WCAG2.2-AA default)
5) Light/dark mode needed? (yes/no)

## Output
- The catalog and preview HTML.
