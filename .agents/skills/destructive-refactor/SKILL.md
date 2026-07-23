---
name: destructive-refactor
description: "AI-led replacement protocol for flawed abstractions, allowing temporary red state while migrating call sites and converging back to green or rollback."
metadata:
  short-description: Replace flawed abstraction safely
  resources:
    - references/destructive-refactor.md
---

## Purpose

Use this skill to replace a flawed function abstraction end-to-end.

## When to use

Use when:
- existing function is close but has wrong side effects
- reuse would require flags/options/branching
- sibling functions are accumulating
- clean design requires deleting/rewriting old function
- all call sites must migrate
- old name no longer matches responsibility

## Protocol

Open `references/destructive-refactor.md` when running this protocol.

1) Baseline
- identify target abstraction and call sites
- record side effects, error behavior, return contract, invariants
- run baseline tests where possible

2) Target design
- define new name + responsibility
- define owned invariants
- define allowed side effects + error behavior
- define call-site contract
- declare old function/behavior slated for deletion

3) Break window declaration (required artifact; explicit temporary red state allowed)
- declare: target abstraction, files allowed to edit, call sites to migrate, old names to remove, forbidden fallback patterns, planned verification commands, rollback procedure
- allow temporary typecheck/build/test failure
- forbid unrelated repairs
- forbid compatibility shims unless staged migration is explicitly required and ledgered
- forbid scope widening beyond chosen abstraction
- during red state, do not fix newly discovered smells unless they block convergence
- complete planned migration pass before one-by-one failure repair

Compat-mode rule: if compat-mode is not already recorded, request it from the router (dev-workflow step 1b) instead of assuming `preserve`. Under `break-allowed`, delete — do not deprecate: compatibility shims, deprecated markers, re-export aliases, and parallel old/new versions are defects, not caution. The staged-migration ledger escape hatch (forbid compatibility shims "unless staged migration is explicitly required and ledgered") applies ONLY under compat-mode `staged` and is unavailable under `break-allowed`.

4) Migration
- update all call sites
- move side effects to correct boundary
- preserve externally observable behavior unless intentionally changed and tested
- add/update tests

5) Convergence
- run required verification depth
- if same failure recurs twice, rollback this skill's edits using the declared rollback procedure
- rollback means: revert only this skill's edits, remove temporary wrappers/functions/tests from this skill, restore old abstraction and call sites, leave no partial migration artifacts, and record rollback reason
- delete obsolete wrappers/functions
- search for old and temporary names

6) Ledger update
- record replaced abstractions
- record intentional duplication
- record staged adapters + removal condition
- write to canonical ledger path `.agents/design-ledger/function-boundaries.md`

## Output expectation

Include:
- decision: `replaced | no-op | rollback`
- old abstraction
- new abstraction
- deleted functions
- migrated call sites
- temporary red state used: yes/no
- verification commands/results
- ledger updates
