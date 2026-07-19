---
name: japanese-tech-writing
description: "Use when Japanese technical prose is drafted or revised in this repo: a PR title/body in 日本語, a Japanese review comment or reply, a Japanese issue, or Japanese content under plans/, reports/, or a README/doc. Applies house norms for formatting, paragraph/argument structure, rigor, reader load, restraint, and banning LLM-ish phrasing. Do not use for commit messages, code, identifiers, code comments, or English prose."
metadata:
  short-description: Japanese technical writing conventions
  requires:
    - references/japanese-tech-writing.md
---

## Purpose

Use this skill to keep Japanese technical prose in this repository aligned with a single
house style for formatting, argument rigor, and restraint. The norms are adapted (not
copied) from an external Japanese technical-writing gist; the operational checklist and
its provenance note live in `references/japanese-tech-writing.md`.

## When to use

Use when at least one trigger applies:

- Drafting or revising a PR title/body written in 日本語.
- Writing or replying to a Japanese code-review comment.
- Writing a Japanese GitHub issue.
- Writing or revising Japanese content under `plans/`, `reports/`, or a Japanese README/doc.

## Scope boundaries

- Applies to Japanese technical prose only: PR titles/bodies, review comments and replies,
  issues, `plans/`, `reports/`, and Japanese README/docs.
- Commit messages stay English (existing repository convention) — out of scope.
- Code, identifiers, and code comments are out of scope (owned by other skills).
- English-language documents are out of scope.
- PR bodies use ordinary Markdown paragraphs, not one-sentence-per-line; the 一文一行
  formatting rule applies only to source Markdown docs (`plans/`, `reports/`,
  README/docs). Every other rule (argument rigor, redundancy removal, no LLM-ish
  phrasing, heading conventions) still applies to PR bodies.

## How to use

0) Open `references/japanese-tech-writing.md`. Where interpretation conflicts, the source
   gist takes precedence per its provenance note.
1) Identify the artifact type (PR body, review comment, issue, or doc) and apply the
   matching formatting rule: one-sentence-per-line for docs, ordinary paragraphs for PR
   bodies.
2) Draft or revise against the reference checklist. On a revision pass, prioritize
   argument rigor and paragraph structure first, then LLM-ish phrasing and redundancy,
   then formatting/heading polish.
3) Re-read once for reader honesty: no hidden artificiality, no unverified claim stated
   as settled fact.

## Output expectation

- The Japanese prose follows the reference checklist; for non-trivial edits, note which
  checklist sections you actively revised for.
- Any rule you deliberately did not apply is named with a one-line reason.
- For PR bodies, confirm ordinary paragraph formatting (not one-sentence-per-line) while
  every non-formatting rule still holds.
