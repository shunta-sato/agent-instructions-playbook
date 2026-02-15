# uidesign-orchestrator reference — end-to-end orchestration

## Goal

Produce a reviewable UIDesign Pack by orchestrating:
uiux-core → tonemana-catalog → tonemana-apply → uidesign-flow

The orchestrator must be safe:
- only create missing artifacts
- never invent new schemas
- stop if prerequisites are incomplete (`<fill>` remains)

## Canonical schema: ui_spec.json meta.tone_and_manner

`uiux/YYYYMMDD-<slug>/ui_spec.json` MUST include:

```json
{
  "meta": {
    "tone_and_manner": {
      "pattern_id": "neutral-minimal",
      "tonemana_spec_ref": "tonemana/YYYYMMDD-<slug>/tonemana_spec.json",
      "token_refs": {
        "json": "tonemana/catalog/tokens/neutral-minimal.tokens.json",
        "css": "tonemana/catalog/tokens/neutral-minimal.tokens.css"
      }
    }
  }
}
```

Notes:

* `pattern_id` must be one of the catalog ids:
  neutral-minimal, trust-corporate, modern-tech, warm-friendly, natural-organic, premium-elegant, bold-energetic
* token_refs must point to catalog tokens (`*.tokens.json` / `*.tokens.css`)
* do not inline tokens inside ui_spec.json

## Orchestration algorithm (deterministic)

### Step 0 — choose UIUX Pack

* If `uiux/.config` exists and has `output_dir`, use it.
* Else if `uiux/` contains packs, use the lexicographically latest folder name.
* Else create a new pack via `$uiux-core` (ask the minimum questions to fill `ui_contract.yaml` and `ui_spec.json`).

Stop if the chosen UIUX Pack still contains `<fill>` after uiux-core.

### Step 1 — ensure tonemana catalog exists

* If `tonemana/catalog/patterns/*.yaml` and `tonemana/catalog/tokens/*.tokens.*` are missing, run `$tonemana-catalog`.

### Step 2 — ensure tonemana is applied and wired

* Check `ui_spec.json` for the canonical `meta.tone_and_manner` block.
* If missing or pointing to non-existing files, run `$tonemana-apply`:

  * propose 3 candidate patterns, confirm 1 id
  * generate `tonemana/YYYYMMDD-<slug>/...`
  * patch UIUX `ui_spec.json` to include canonical schema

Stop if `meta.tone_and_manner` is still missing after tonemana-apply.

### Step 3 — generate UIDesign Pack

Run `$uidesign-flow` with:

* the chosen UIUX Pack path
* the wired `meta.tone_and_manner` token_refs
* representative screen mapping (entry/form/status)

Stop if UIDesign Pack still contains `<fill>`.

### Step 4 — report next action for humans (required wording)

Always include these links in the completion message:

* `tonemana/catalog/previews/index.html` — 7-pattern switch is available in UI.
* `uidesign/.../previews/index.html` — review starting point.

Always include this short procedure:

1. Open previews and switch pattern/viewport as needed.
2. Turn on `Review Mode` and click elements to add comments.
3. `Export JSON` or `Export Markdown` and use it as input for `review_notes.md`.

If humans request IA/navigation changes, route them to uiux-core (not uidesign-flow).
