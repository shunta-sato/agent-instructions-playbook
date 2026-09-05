---
name: comment-discipline
description: "Use only when explicitly asked to clean up AI-narration/redundant comments in a diff, or to adjudicate comment vs. commit-message vs. test-name content for a specific change. The always-on Why-not comment rule lives in AGENTS.md; this skill is the explicit cleanup/adjudication protocol only. Do not use for C++ Doxygen/public-API docs (`code-readability`), or when no explicit comment decision is in scope."
metadata:
  short-description: Comment channel discipline
  visibility: explicit-only
  requires:
    - references/comment-discipline.md
---

## Purpose

Remove redundant narration without removing durable knowledge. Ordinary coding
already follows AGENTS.md and `dev-workflow`; do not load this protocol merely
because a changed file contains comments.

## When to use

Use only for explicitly requested comment cleanup or a specific comment versus
commit/test-name decision. Limit cleanup to the requested diff/scope. Public API
contract documentation belongs to `code-readability`, not this cleanup protocol.

## How to use

0) Open `references/comment-discipline.md`.
1) Inspect new/changed implementation comments. Keep non-obvious constraints,
rejected alternatives, hazards, requirements, or rationale a maintainer needs.
2) Remove prose that only restates the adjacent code, type signature, obvious
purpose, or edit history. Do not add routine Args/Returns/Raises sections to
private helpers or comments to unchanged code just for apparent completeness.
3) Prefer a clear local name when it solves ambiguity. Do not introduce helpers
or restructure unrelated code merely to eliminate a comment.
4) Preserve required public API docs, license/copyright notices, generated-code
markers, and compiler/linter/type-checker directives. Do not delete by keyword
or by a target comment count; a real safety explanation may say "because".
5) Put expected test behavior in names/assertions; retain non-obvious regression
rationale. Put change motivation in the English commit message, not code prose.
6) Reuse the normal diff review and required verification; do not create another
review loop or per-comment audit artifact.

## Output expectation

Summarize the material cleanup and any disputed or deliberately retained note.
Do not list every removed comment or add a replacement explanation for each one.
State verification limits when an annotation/directive change needs a check.
