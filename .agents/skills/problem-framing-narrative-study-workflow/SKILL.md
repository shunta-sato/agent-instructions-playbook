---
name: problem-framing-narrative-study-workflow
description: "Create or review structured study notes from narrative, case-based, parable, dialogue, puzzle, or problem-framing sources where the learning unit is misframing → reframing → consequence → reader application. Do not use for ordinary expository textbooks, technical pattern catalogs, or technical essay collections whose primary unit is claim → reasoning → practice/context; use the corresponding textbook or technical-essay workflow."
metadata:
  short-description: Narrative problem-framing study workflow
---

## Purpose

Create or review privacy-safe study notes from narrative/problem-framing sources where learning depends on a case, apparent problem, hidden frame, reframing move, consequence, and reader application.

The output is a paraphrased learning artifact, not a transcript. Do not copy long passages from the source. Prefer paraphrased explanation, compact references, and original learning structure. Use short quotations only when necessary and only within applicable copyright limits.

## When to use

Use this skill when:

- the source teaches through story, case, puzzle, dialogue, parable, or problem-framing situations
- learning depends on apparent problem, hidden frame, ownership, reframing, and consequence
- removing the story leaves only a vague slogan
- the user asks to produce case notes, diagnostic questions, heuristics, worksheets, or reframing prompts

Do not use when:

- the source is a stable concept/method/pattern taxonomy; route to `textbook-structured-content-workflow`
- the source is an argument-first technical essay collection; route to `technical-essay-study-workflow`
- the task is only mechanical link/tag check; route to `textbook-quality-gate` in `shared-mechanical-only` mode
- the task is only one textbook-style note review; route to `textbook-learning-content-review`

## Hybrid source routing

Classify by durable learning unit, not prose style.

- If the source has anecdotes but the durable units are stable concepts, methods, or patterns, use `textbook-structured-content-workflow`.
- If the source is essay-like but the durable unit is misframing → reframing → consequence, use `problem-framing-narrative-study-workflow`.
- If the source discusses problem setting but the durable unit is author claim → reasoning → practice/context, use `technical-essay-study-workflow`.
- If one source contains mixed units, choose the primary workflow for the pack and record secondary note types explicitly. Do not run multiple workflows over the same note root without a clear partition.

## How to use

1. Classify the source as narrative/problem-framing and record why not textbook and why not technical essay.
2. Identify `<source-path>` and `<target-pack>` with relative paths or placeholders only.
3. Map notes into part/gate, case/story, heuristic/principle, diagnostic question, worksheet/application template, and review/index.
4. Open and apply `references/note-contracts.md`.
5. Paraphrase cases without transcribing source passages.
6. Preserve apparent problem, actors, hidden frame, reframing move, and consequence.
7. Write heuristics as usable questions, not slogans.
8. Create application worksheets that help the reader apply the reframing move.
9. Perform semantic review and produce the required report.
10. Require `textbook-quality-gate` in `shared-mechanical-only` mode before publish or sync.

## Required output

```markdown
## Narrative Study Pack Report

- Source:
- Source path: <relative-or-placeholder-path>
- Target pack:
- Source classification: narrative/problem-framing
- Why narrative/problem-framing:
- Why not textbook:
- Why not technical essay:
- Framing layer map:
  - part/gate:
  - case/story:
  - heuristic/principle:
  - diagnostic question:
  - worksheet/application template:
  - review/index:
- Files created/updated:
- Contracts applied:
- Mechanical checks required before publish/sync: yes | no
- PII/copyright safeguards applied:

## Narrative Semantic Review Report

- Gate decision: submit | no-submit
- Notes sampled:
  - part/gate:
  - case/story:
  - heuristic/question:
  - worksheet:
- Findings:
  - [ID] <path> — <failed criterion> — <required fix>
- Failure modes checked:
  - quote-list reduction
  - slogan-only heuristic
  - plot-summary-only case
  - missing apparent problem
  - missing hidden frame
  - missing ownership/origin
  - missing reframing move
  - missing reader application question
```
