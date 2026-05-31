---
name: technical-essay-study-workflow
description: "Create or review structured study notes from technical essay collections, engineering blogs, opinionated practice books, industry criticism, and experience-based software or engineering writing where the learning unit is claim → reasoning → anecdote/context → practice or applicability limit. Do not use for systematic textbook taxonomies or for problem-framing sources whose lesson depends on misframing → reframing → consequence."
metadata:
  short-description: Technical essay study-note workflow
---

## Purpose

Create or review privacy-safe study notes from technical essay collections, engineering blogs, opinionated practice writing, industry criticism, and experience reports.

The output is a paraphrased learning artifact, not a transcript. Do not copy long passages from the source. Prefer paraphrased explanation, compact references, and original learning structure. Use short quotations only when necessary and only within applicable copyright limits.

## When to use

Use this skill when:

- the source is made of essays, blog posts, columns, criticism, experience reports, or opinionated practice writing
- learning depends on author claim, reasoning path, anecdote/example, practice advice, historical context, or applicability limit
- the user asks to separate timeless advice from time-bound technology, market, or organizational assumptions
- the user asks for principle/practice/checklist extraction from essays

Do not use when:

- the source is stable textbook taxonomy; route to `textbook-structured-content-workflow`
- the source primarily teaches through misframing/reframing cases; route to `problem-framing-narrative-study-workflow`
- the task is final mechanical publish/sync gate; route to `textbook-quality-gate` in `shared-mechanical-only` mode
- the task is single textbook note semantic review; route to `textbook-learning-content-review`

## Hybrid source routing

Classify by durable learning unit, not prose style.

- If the source has anecdotes but the durable units are stable concepts, methods, or patterns, use `textbook-structured-content-workflow`.
- If the source is essay-like but the durable unit is misframing → reframing → consequence, use `problem-framing-narrative-study-workflow`.
- If the source discusses problem setting but the durable unit is author claim → reasoning → practice/context, use `technical-essay-study-workflow`.
- If one source contains mixed units, choose the primary workflow for the pack and record secondary note types explicitly. Do not run multiple workflows over the same note root without a clear partition.

## How to use

1. Classify the source with `references/source-classification.md` and record why technical essay, why not textbook, and why not narrative/problem-framing.
2. Identify `<source-path>` and `<target-pack>` with relative paths or placeholders only.
3. Map notes into root/index/review, part/theme, essay, principle/claim, practice/method, strategy/market, historical-context, and checklist.
4. Open and apply `references/note-contracts.md`.
5. Preserve the reasoning path, not just the conclusion.
6. Separate reusable advice from time-bound technology, market, or organizational assumptions.
7. Include limits, counterpressure, and present-day applicability.
8. Link essay notes to practices, claims, historical contexts, and checklists.
9. Produce the semantic review report.
10. Require `textbook-quality-gate` in `shared-mechanical-only` mode before publish or sync.

## Required output

```markdown
## Technical Essay Study Pack Report

- Source:
- Source path: <relative-or-placeholder-path>
- Target pack:
- Source classification: technical essay
- Why technical essay:
- Why not textbook:
- Why not narrative/problem-framing:
- Essay-study layer map:
  - root/index/review:
  - part/theme:
  - essay:
  - principle/claim:
  - practice/method:
  - strategy/market:
  - historical-context:
  - checklist:
- Files created/updated:
- Present-day applicability notes:
- Mechanical checks required before publish/sync: yes | no
- PII/copyright safeguards applied:

## Technical Essay Semantic Review Report

- Gate decision: submit | no-submit
- Notes sampled:
  - essay:
  - principle/claim:
  - practice/method:
  - strategy/historical-context:
  - checklist/review:
- Findings:
  - [ID] <path> — <failed criterion> — <required fix>
- Failure modes checked:
  - quote-list reduction
  - slogan-only principle
  - generic textbook outline
  - missing author claim
  - missing reasoning path
  - missing context or anecdote
  - missing present-day applicability
  - missing limits/counterpressure
  - old technology or market claim treated as timeless advice
```
