# Destructive refactor runbook

## Baseline artifact

Capture before edits:
- target abstraction name
- full call-site list
- side effects
- error behavior
- return contract
- invariants
- baseline verification commands + output

## Red-state discipline

Allowed:
- temporary compile/type/test failures during planned migration window

Forbidden:
- compatibility wrappers/shims not declared as staged migration
- unrelated fixes
- drifting scope
- preserving old/new siblings permanently

## Convergence and rollback

- Migrate all call sites first.
- Then run canonical verification depth from dev-workflow.
- Track recurring failures by signature.
- If same signature appears twice after attempted fix, rollback this refactor.

## Finalization checks

- old abstraction deleted or staged with ledger entry
- no `newX`, `legacyX`, `x2`, `commonX`, `helper`, `util` leftovers
- no boolean-flag API hiding semantic differences
- design ledger updated
