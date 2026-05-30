---
name: textbook-structured-content-workflow
description: "Create or refresh structured textbook study notes from books, PDFs, OCR text, or existing Markdown packs. Use for expository or technical textbook sources whose durable learning units are stable concepts, methods, processes, patterns, antipatterns, or chapter-level explanations within a systematic taxonomy. Do not use as the primary workflow for narrative, case-based, parable, dialogue, puzzle, problem-framing, technical-essay, blog, industry-criticism, or argument-first sources; use the corresponding narrative or technical-essay workflow."
metadata:
  short-description: Textbook-style study-note pack workflow
---

## Purpose

Create or refresh privacy-safe, textbook-style Markdown learning packs from generic books, articles, PDFs, OCR text, or existing Markdown packs.

The output is a paraphrased learning artifact, not a transcript. Do not copy long passages from the source. Prefer paraphrased explanation, compact references, and original learning structure. Use short quotations only when necessary and only within applicable copyright limits.

## When to use

Use this skill when:

- the source is mostly expository
- durable learning units are stable concepts, methods, patterns, antipatterns, processes, or systematic chapter explanations
- the task asks to create, refresh, reorganize, or review a textbook-style learning pack
- the source has indexes, chapters, terms, methods, exercises, pattern catalogs, or review prompts

Do not use when:

- the learning unit is `misframing → reframing → consequence → reader application`; route to `problem-framing-narrative-study-workflow`
- the learning unit is `claim → reasoning → anecdote/context → practice/applicability limit`; route to `technical-essay-study-workflow`
- the task is only reviewing one textbook note; route to `textbook-learning-content-review`
- the task is final pack validation; route to `textbook-quality-gate`
- the task is only Obsidian link/tag registration and no content transformation

## Hybrid source routing

Classify by durable learning unit, not prose style.

- If the source has anecdotes but the durable units are stable concepts, methods, or patterns, use `textbook-structured-content-workflow`.
- If the source is essay-like but the durable unit is misframing → reframing → consequence, use `problem-framing-narrative-study-workflow`.
- If the source discusses problem setting but the durable unit is author claim → reasoning → practice/context, use `technical-essay-study-workflow`.
- If one source contains mixed units, choose the primary workflow for the pack and record secondary note types explicitly. Do not run multiple workflows over the same note root without a clear partition.

## How to use

1. Classify the source shape and record why it is textbook-style, why not narrative/problem-framing, and why not technical essay.
2. Identify `<source-path>` and `<target-pack>` with relative paths or placeholders only.
3. Map notes into: root/index, chapter, concept, method/process, pattern/antipattern, mini-pattern/mini-antipattern, and review.
4. Open and apply `references/note-type-contracts.md`.
5. Preserve existing frontmatter, tags, and links when safe; never invent private paths, private note names, or source text.
6. Produce paraphrased learning content that explains use, conditions, decisions enabled, failure modes, next actions, and semantic links.
7. Avoid definition-only notes and mechanically summarized outlines.
8. Send representative notes to `textbook-learning-content-review` for semantic review.
9. Require `textbook-quality-gate` before publish or sync.
10. If an Obsidian integration skill exists in this repository, hand off to it. Otherwise, record external Obsidian or note-link verification commands as optional manual checks.

## Required output

```markdown
## Textbook Pack Build Report

- Source:
- Source path: <relative-or-placeholder-path>
- Target pack:
- Source classification: textbook-style
- Why textbook:
- Why not narrative/problem-framing:
- Why not technical essay:
- Note-type map:
  - root/index:
  - chapter:
  - concept:
  - method/process:
  - pattern/antipattern:
  - review:
- Files created/updated:
- Contracts applied:
- Representative notes sent to textbook-learning-content-review:
- Quality gate required before publish/sync: yes | no
- Obsidian or external sync requested: yes | no
- PII/copyright safeguards applied:
```
