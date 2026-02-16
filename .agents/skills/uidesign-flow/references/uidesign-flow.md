# uidesign-flow reference — from tone-and-manner to reviewable UI styling

## Core premise

Humans can only approve UI styling reliably if they can **see** controlled examples and give feedback in a structured way.

This skill creates a stable bridge:
- tokens snapshot (what values drive the look)
- component preview (small parts)
- representative screens (how parts look in context)
- a feedback template (how humans should respond)

## Inputs (required)

A UIUX Pack with `ui_spec.json` containing:

```json
{
  "meta": {
    "tone_and_manner": {
      "pattern_id": "neutral-minimal",
      "tonemana_spec_ref": "tonemana/20260214-example/tonemana_spec.json",
      "token_refs": {
        "json": "tonemana/catalog/tokens/neutral-minimal.tokens.json",
        "css": "tonemana/catalog/tokens/neutral-minimal.tokens.css"
      }
    }
  }
}
```

If this block is missing, stop and run `$tonemana-apply` first.

## Outputs (deterministic UIDesign Pack)

Folder: `uidesign/YYYYMMDD-<slug>/`

Must include:

* `uidesign_contract.yaml`
* `uidesign_spec.json`
* `auto_review.json`
* `diff_summary.md`
* `review_notes.md`
* `previews/review/review.css`
* `previews/review/review_store.js`
* `previews/review/review_export.js`
* `previews/review/review_ui.js`
* `tokens/resolved.tokens.json`
* `tokens/resolved.tokens.css`
* `previews/index.html`
* `previews/components.html`
* `previews/screens/entry.html`
* `previews/screens/form.html`
* `previews/screens/status.html`
* `previews/preview.css`
* `previews/preview.js`

## Representative screens (default 3)

Pick 3 screen IDs from the UIUX spec and map them as:

* entry: “first-time entry / overview / list”
* form: “input + validation + error”
* status: “in-progress / success / failure + recovery”

The HTML is for review. It does not have to match product code structure, but it must be stable and comparable.

## Feedback rules (human)

Humans review directly in browser Review Mode and export `review_notes.generated.md` / `annotations.json`.

For exceptional manual edits in `review_notes.md`, keep annotation IDs and always include page + element.

Review feedback should include:

* page reference (components.html or which screen html)
* element reference (button, input, alert, card…)
* state reference (default / disabled / loading / error)
* what to change (concrete) + why (short)

Do not request navigation/IA changes here. That goes to uiux-core.

## Machine checks (auto_review.json)

Minimum checks:

* UIUX Pack refs exist and contain meta.tone_and_manner
* token snapshot files exist (resolved.tokens.*)
* preview files exist
* no `<fill>` remains in UIDesign Pack
* representative screens mapping is filled (3 IDs)

Mark `unknown` only when the check truly cannot be computed; explain why.
