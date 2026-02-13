# uiux-core

Use this prompt for UI/UX design and review tasks that require a deterministic UIUX Pack output.

## Workflow

1) Identify target platform(s): Android, iOS, web (one or more).
2) Invoke `$uiux-core`.
3) Invoke platform adapter skill(s) as needed: `$uiux-android`, `$uiux-ios`, `$uiux-web`.
4) Ensure the UIUX Pack exists and is updated in the chosen output directory with:
   - `ui_contract.yaml`
   - `ui_spec.json`
   - `auto_review.json`
   - `diff_summary.md`
5) Summarize outcomes for human reviewers, clearly separating machine-checkable results and human judgement items.
