---
name: destructive-refactor
description: "AI-led replacement protocol for flawed abstractions, allowing temporary red state while migrating call sites and converging back to green or rollback."
metadata:
  short-description: Replace flawed abstraction safely
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

3) Break window (explicit temporary red state allowed)
- allow temporary typecheck/build/test failure
- forbid unrelated repairs
- forbid compatibility shims unless staged migration is explicitly required
- forbid scope widening beyond chosen abstraction
- do not chase one-by-one failures before planned migration pass completes

4) Migration
- update all call sites
- move side effects to correct boundary
- preserve externally observable behavior unless intentionally changed and tested
- add/update tests

5) Convergence
- run required verification depth
- if same failure recurs twice, rollback this skill's edits
- delete obsolete wrappers/functions
- search for old and temporary names

6) Ledger update
- record replaced abstractions
- record intentional duplication
- record staged adapters + removal condition

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
