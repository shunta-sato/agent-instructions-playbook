---
name: textbook-quality-gate
description: "Final gate for structured study-note packs. In textbook-full-gate mode, verify textbook note-type contracts, deterministic checker results, representative semantic learning quality, tags, wikilinks, corruption scans, and publish/sync readiness. For narrative or technical-essay packs, use only explicit shared-mechanical-only mode after their workflow semantic review; do not apply textbook headings or textbook semantic checks."
metadata:
  short-description: Study-note pack publication gate
---

## Purpose

Decide whether a structured study-note pack is ready for publication or sync. This is not the repository submission gate; `quality-gate` still handles final repository readiness.

The pack must remain a paraphrased learning artifact, not a transcript. Do not copy long passages from the source. Prefer paraphrased explanation, compact references, and original learning structure. Use short quotations only when necessary and only within applicable copyright limits.

The deterministic checker should catch mechanical and easily detectable structural issues. It must not replace semantic learning review. When a textbook semantic issue cannot be detected mechanically without false positives, record it as requiring `textbook-learning-content-review` rather than failing solely from the checker.

## Gate mode

Choose exactly one mode:

```markdown
Gate mode: textbook-full-gate | shared-mechanical-only
```

### `textbook-full-gate`

Use when:

- the pack intentionally follows textbook note-type contracts
- the source was processed by `textbook-structured-content-workflow`

Run:

- `python3 .agents/skills/textbook-quality-gate/scripts/check_study_notes.py --mode textbook-full-gate <note-root>`
- representative semantic spot-check via `textbook-learning-content-review`
- shared mechanical checks from `references/shared-mechanical-checks.md`
- optional external/Obsidian checks only when requested and available
- repository verification if repo files changed

### `shared-mechanical-only`

Use when:

- narrative or technical essay workflow has already completed semantic review
- the user only needs publish/sync safety checks
- the pack does not follow textbook note-type contracts

Run only source-type neutral checks:

- `python3 .agents/skills/textbook-quality-gate/scripts/check_study_notes.py --mode shared-mechanical-only <note-root>`
- tags/frontmatter sanity
- wikilink syntax
- unresolved local wikilinks when resolvable
- Unicode replacement-character corruption and multilingual text encoding issues
- obvious binary/corruption artifacts in Markdown
- optional external/Obsidian checks only when requested and available
- repository verification if repo files changed

Do not run in `shared-mechanical-only` mode:

- textbook required-heading checks
- definition-only textbook checks
- textbook note-type contract checks
- textbook semantic spot-checks

If an Obsidian integration skill exists in this repository, hand off to it. Otherwise, record external Obsidian or note-link verification commands as optional manual checks.

## Required output

```markdown
Gate decision: submit | no-submit
Gate mode: textbook-full-gate | shared-mechanical-only

Findings:
- [ID] <path> — <failed criterion> — <required fix>

Checks run:
- <command> — pass | fail | not applicable

Textbook semantic checks:
- applicable: yes | no
- representative notes:
  - <path> — pass | fail — <reason>

Shared mechanical checks:
- tags/frontmatter — pass | fail | not applicable
- wikilinks — pass | fail | not applicable
- unresolved links — pass | fail | not applicable
- Unicode replacement-character corruption — pass | fail | not applicable
- external/Obsidian checks — pass | fail | not applicable

Source-workflow semantic review:
- required: yes | no
- artifact:
- decision: submit | no-submit | not applicable

Submit criteria:
- deterministic checker passed when applicable
- semantic review passed in the correct source workflow
- no introduced unresolved links
- no replacement-character corruption
- repository verification passed when repo files changed
```
