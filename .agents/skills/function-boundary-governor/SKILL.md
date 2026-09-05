---
name: function-boundary-governor
description: "Use for explicitly requested function-boundary design/review, public or cross-module API changes, multi-call-site replacement, or a concrete responsibility/side-effect boundary problem in the current task. Do not trigger for routine local edits or textual similarity alone. Use design-balance for module/class ownership."
metadata:
  short-description: Autonomous function-boundary design
  requires:
    - references/function-boundary-governor.md
  templates:
    - templates/function-design-ledger-entry.md
---

## Purpose

AI-led skill for concrete function-boundary decisions, not a mandatory review of every function edit.

For module/class responsibility layout, layer count, or reason-to-change mapping, use `design-balance` first. This skill works one level lower, on functions, helpers, APIs, and call sites.

## When to use (trigger conditions)

Load an explicitly named skill before acting. Apply the boundary protocol when:
- function-boundary design, review, or refactoring is explicitly requested;
- a public/cross-module API changes or multiple call sites need replacement;
- the current task exposes a concrete boundary problem, such as moving responsibility or side effects, or a behavior flag hiding distinct concepts.

Routine function additions/edits, local bug fixes, variable renames, formatting,
generated output, and textual similarity alone do not trigger this protocol.
For those edits, check responsibility, inputs/outputs, error behavior, and side
effects locally and retain focused regression proof; do not require a scoring
rubric, function inventory, or design-ledger entry solely because code changed.
An explicit boundary review still applies even when its correct outcome is no-op.
Use `design-balance` for module/class ownership, not this skill as a substitute.

## How to use

1) Open `references/function-boundary-governor.md`.
2) Confirm a trigger above. If an explicit invocation reveals no boundary decision, report that scoped no-op and return to the calling workflow. Otherwise inventory the affected boundary, relevant semantic neighbors, and callers as required by the reference.
3) For each function in that boundary, decide one action: `keep | rename | split | merge | replace | inline | delete | no-op`.
4) Use separated positive/risk rubric + decision rules to reject low-coherence refactors.
5) If replacement requires temporary red-state migration, route to `$destructive-refactor`.
6) Apply only scoped edits needed for coherent final design.
7) Verify with required command depth from `$dev-workflow`.
8) Update canonical design ledger path `.agents/design-ledger/function-boundaries.md` using `templates/function-design-ledger-entry.md` when required.

## Delete guidance

`delete` removes a function/helper/API with no replacement; it is valid when call-site discovery confirms zero remaining callers via the existing call-site discovery step. Under `break-allowed`, external callers outside the repo do not count as callers.

## Hard rules

- AI-led: decide and act autonomously within the authorized scope and recorded compatibility mode; a design preference does not authorize a breaking change or destructive external action.
- No-op is valid when evidence is insufficient or changes are not beneficial.
- Reject refactors when similarity is only textual.
- Reject abstractions requiring vague names (`common`, `util`, `helper`, `handle`, `process`, `manage`).
- Reject abstractions that require boolean flags/optional behavior switches to hide semantic differences.
- Reject merges when error behavior, side effects, or call-site clarity differ.
- Do not preserve both old/new abstractions unless staged migration is explicitly recorded in the ledger.

## Output expectation

For a scope-only no-op, give the reason and return to the calling workflow; do not fabricate discovery or ledger evidence. For a triggered boundary decision, return:
- Changed functions inventory and semantic neighbors considered.
- Decision per function with action and rationale.
- Action taken: `changed | no-op | delegated-to-destructive-refactor | rollback`.
- Files edited and call sites migrated (if any).
- Old names searched and cleanup result (under `break-allowed`, backed by the `scripts/check_api_removal.py` sweep output rather than prose).
- Whether `$destructive-refactor` was invoked.
- Verification commands/results.
- Ledger update path (`.agents/design-ledger/function-boundaries.md`) or explicit no-update reason.
