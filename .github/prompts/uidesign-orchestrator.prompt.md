# uidesign-orchestrator

Use this prompt when you want the full chain that results in reviewable UI styling evidence.

1) Load `$uidesign-orchestrator`.
2) Follow references strictly (do not invent schemas).
3) Only create missing artifacts; if `<fill>` remains, stop and ask for the missing inputs.
4) Final output must include:
   - which UIUX Pack was used
   - which pattern_id was selected
   - where the UIDesign previews are (path to previews/index.html)
   - what humans should do next (write review_notes.md)
