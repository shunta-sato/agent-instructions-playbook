---
name: function-boundary-governor
description: "Autonomous function-boundary design workflow for functions/helpers/APIs/call sites: decide keep/rename/split/merge/replace/inline/delete/no-op, apply coherent changes, verify, and record boundary decisions. Use design-balance instead for module/class responsibility layout."
metadata:
  short-description: Autonomous function-boundary design
  requires:
    - references/function-boundary-governor.md
  templates:
    - templates/function-design-ledger-entry.md
---

## Purpose

Primary AI-led skill for function implementation quality and function-boundary design.

For module/class responsibility layout, layer count, or reason-to-change mapping, use `design-balance` first. This skill works one level lower, on functions, helpers, APIs, and call sites.

## When to use (trigger conditions)

Use when a change:
- adds/edits functions, helpers, or utilities
- changes public or cross-module APIs
- changes call-site structure
- introduces similar-looking logic
- introduces/modifies side effects inside functions
- introduces generic helper/common/util modules
- refactors function boundaries

Do not use it as the primary tool for module/class responsibility maps or architecture-level option comparison.

## How to use

1) Open `references/function-boundary-governor.md`.
2) Run required discovery from the reference: changed-function inventory, semantic-neighbor search, and call-site discovery.
3) For each affected function, decide one action: `keep | rename | split | merge | replace | inline | delete | no-op`.
4) Use separated positive/risk rubric + decision rules to reject low-coherence refactors.
5) If replacement requires temporary red-state migration, route to `$destructive-refactor`.
6) Apply only scoped edits needed for coherent final design.
7) Verify with required command depth from `$dev-workflow`.
8) Update canonical design ledger path `.agents/design-ledger/function-boundaries.md` using `templates/function-design-ledger-entry.md` when required.

## Delete guidance

`delete` removes a function/helper/API with no replacement; it is valid when call-site discovery confirms zero remaining callers via the existing call-site discovery step. Under `break-allowed`, external callers outside the repo do not count as callers.

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
- Changed functions inventory and semantic neighbors considered.
- Decision per function with action and rationale.
- Action taken: `changed | no-op | delegated-to-destructive-refactor | rollback`.
- Files edited and call sites migrated (if any).
- Old names searched and cleanup result (under `break-allowed`, backed by the `scripts/check_api_removal.py` sweep output rather than prose).
- Whether `$destructive-refactor` was invoked.
- Verification commands/results.
- Ledger update path (`.agents/design-ledger/function-boundaries.md`) or explicit no-update reason.
