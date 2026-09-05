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

AI-led skill for concrete function-boundary decisions, not a mandatory review of
all function edits. Use `design-balance` for module/class ownership; this skill
works on functions, helpers, APIs, and their callers.

## When to use (trigger conditions)

Load an explicitly named skill before acting. Apply the boundary protocol for:
- explicit function-boundary design, review, or refactoring;
- public/cross-module API changes or multi-call-site replacement;
- a concrete responsibility or side-effect boundary problem in the current task.

Routine local edits and textual similarity alone do not trigger the protocol.
Check local inputs/outputs, errors, and effects without a score, full inventory,
or ledger. An explicit boundary review may correctly conclude no-op.

## How to use

1) Open `references/function-boundary-governor.md`.
2) Confirm the trigger and inspect the affected boundary, callers, and semantic
neighbors. If there is no boundary decision, return a scoped no-op to the caller.
3) Decide `keep | rename | split | merge | replace | inline | delete | no-op`
from observed contracts, present design benefit, and decisive verification.
4) Apply the reference's evidence-based decision rules. Do not assign points or
use an aggregate score to authorize a change; missing safety evidence cannot be
compensated by readability or reuse benefits.
5) Route replacement/convergence to `$destructive-refactor` when applicable,
including temporary red-state migration. Honor the recorded compatibility mode.
6) Make scoped changes, verify at `$dev-workflow`'s required depth, and record
material boundary decisions in `.agents/design-ledger/function-boundaries.md`
using `templates/function-design-ledger-entry.md` when required.

## Delete guidance

Delete only after call-site discovery establishes no remaining required callers.
A `break-allowed` waiver covers only its stated contract/scope; do not ignore
known external obligations beyond that waiver. Preserve or explicitly stage
compatibility otherwise.

## Hard rules

- AI-led: decide and act autonomously inside authorized scope and compatibility.
- No-op is valid for speculative design work; it does not excuse an unmet DoD.
- Reject merging textual similarity with different error behavior or side effects.
- Reject vague names or boolean flags/options that hide distinct concepts.
- Do not retain superseded old/new APIs without a recorded staged migration.
  Intentional parallel concepts are not superseded APIs.
- Keep required characterization, caller migration, convergence, and rollback
  evidence. Resolve missing proof rather than inventing a favorable score.

## Output expectation

For a scope-only no-op, report the reason and continue the calling workflow. For
an actual boundary decision, report relevant callers, action and contract-based
rationale, edits/migration, verification, and ledger path or no-update reason.
Under `break-allowed`, back obsolete-name cleanup with the applicable
`scripts/check_api_removal.py` sweep; state whether `$destructive-refactor` was
used. Reuse the plan/PR instead of duplicating evidence in a scoring worksheet.
