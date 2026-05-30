---
name: textbook-learning-content-review
description: "Review textbook-style Markdown learning notes for semantic usefulness. Use for concept, method, pattern, antipattern, chapter, and review notes that should explain why an idea matters, when to use it, inputs/outputs, examples, pitfalls, relationships, and self-check prompts. Do not use for narrative problem-framing notes, technical essay notes, Markdown linting, Obsidian link checks, or final pack submission gates."
metadata:
  short-description: Textbook note semantic usefulness review
---

## Purpose

Review textbook-style Markdown learning notes for semantic usefulness and application value.

The reviewed output must remain a paraphrased learning artifact, not a transcript. Do not copy long passages from the source. Prefer paraphrased explanation, compact references, and original learning structure. Use short quotations only when necessary and only within applicable copyright limits.

## When to use

Use this skill when:

- reviewing one or more textbook-style notes
- a note may be definition-only, thin, mechanically summarized, or not actionable
- the user asks whether a note is useful for learning or application
- a generated textbook note type needs semantic review

Do not use when:

- the source is narrative/problem-framing
- the source is technical essay
- the task is a final pack gate
- the task is link/tag/format checking
- the task is Obsidian registration only

## How to use

1. Determine each note type and apply the relevant contract from `../textbook-structured-content-workflow/references/note-type-contracts.md`.
2. Review whether the note supports use, diagnosis, decision-making, and transfer.
3. Report findings for missing semantic learning value, not Markdown style alone.
4. Pass only when there are no Blocker findings and no unresolved Major findings.

## Review rubric

Report findings when:

- the note only defines the term
- a method/process lists steps but not decisions enabled
- no use situation is visible
- inputs/outputs are missing
- a concept is disconnected from the source argument
- examples are missing where abstraction would be unclear
- pitfalls/misuse are missing
- practice questions are generic
- links exist but the semantic relationship is unclear

## Severity

- Blocker: note is definition-only, misleading, or cannot support application.
- Major: key context, use condition, input/output, pitfall, or source-argument link is missing.
- Minor: examples, links, or prompts need improvement but core learning value exists.

## Required output

```markdown
## Textbook Learning Content Review

- Decision: pass | fail
- Scope:
- Note type contract applied:
- Notes reviewed:

### Finding N
- Severity: blocker | major | minor
- Path:
- Heading:
- Failed criterion:
- Why it harms learning:
- Required fix:
- Example of acceptable improvement:

## Pass criteria

- No blocker findings.
- No unresolved major findings.
- The note supports the sentence:
  "In my project, I would use this idea when ___, with inputs ___,
  to decide or detect ___, while watching out for ___."
```
