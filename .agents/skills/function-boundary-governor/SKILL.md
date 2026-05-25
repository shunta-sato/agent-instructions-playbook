---
name: function-boundary-governor
description: "Autonomous function-boundary design workflow: decide keep/rename/split/merge/replace/inline/no-op, apply coherent changes, verify, and record boundary decisions."
metadata:
  short-description: Autonomous function-boundary design
---

## Purpose

Primary AI-led skill for function implementation quality and function-boundary design.

## When to use (trigger conditions)

Use when a change:
- adds/edits functions, helpers, or utilities
- changes public or cross-module APIs
- changes call-site structure
- introduces similar-looking logic
- introduces/modifies side effects inside functions
- introduces generic helper/common/util modules
- refactors function boundaries

## How to use

1) Open `references/function-boundary-governor.md`.
2) For each affected function, decide one action: `keep | rename | split | merge | replace | inline | no-op`.
3) Use the rubric to score design quality and reject low-coherence refactors.
4) If replacement requires temporary red-state migration, route to `$destructive-refactor`.
5) Apply only scoped edits needed for coherent final design.
6) Verify with required command depth from `$dev-workflow`.
7) Update design ledger using `templates/function-design-ledger-entry.md` when decisions are likely to recur.

## Hard rules

- AI-led: decide and act autonomously; do not switch to human option selection.
- No-op is valid when evidence is insufficient or changes are not beneficial.
- Reject refactors when similarity is only textual.
- Reject abstractions requiring vague names (`common`, `util`, `helper`, `handle`, `process`, `manage`).
- Reject abstractions that require boolean flags/optional behavior switches to hide semantic differences.
- Reject merges when error behavior, side effects, or call-site clarity differ.
- Do not preserve both old/new abstractions unless staged migration is explicitly recorded in the ledger.

## Output expectation

Return:
- Decision table of affected functions with chosen action and rationale.
- Whether `$destructive-refactor` was invoked.
- Verification commands/results.
- Ledger updates (or explicit no-update reason).
