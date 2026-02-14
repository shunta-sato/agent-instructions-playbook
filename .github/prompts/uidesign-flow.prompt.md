# uidesign-flow

Use this prompt to bridge an approved tone-and-manner decision into concrete UI styling with reviewable previews.

## Workflow

1) Ensure a UIUX Pack exists (uiux/YYYYMMDD-<slug>/) and is up to date.
2) Ensure ui_spec.json includes meta.tone_and_manner with pattern_id + tonemana_spec_ref + token_refs (json/css).
   - If missing, run `$tonemana-apply` first.
3) Invoke `$uidesign-flow`.
4) Ensure the UIDesign Pack exists with:
   - uidesign_contract.yaml
   - uidesign_spec.json
   - auto_review.json
   - diff_summary.md
   - review_notes.md
   - tokens/resolved.tokens.json + tokens/resolved.tokens.css
   - previews/index.html + components.html + 3 representative screens
5) Ask humans to write feedback into review_notes.md, referencing page + element + state + change.
