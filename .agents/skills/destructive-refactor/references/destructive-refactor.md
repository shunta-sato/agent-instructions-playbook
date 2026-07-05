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
- keeping the old API "just in case" under break-allowed

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

## Deletion checklist (after migration)

- sweep old symbol names across code, tests, docs, and re-exports:
  `python scripts/check_api_removal.py --symbol <old-name> ...`
- under `break-allowed`, the convergence record must include the sweep output (zero hits)


## Break-window declaration (required)

Before entering red-state, record:
- target abstraction
- files allowed to edit
- call sites to migrate
- old names to remove
- forbidden fallback patterns
- planned verification commands
- rollback command/procedure

## Red-state execution rules

- Failures inside declared migration scope are expected during red-state.
- Do not add compatibility wrappers to make intermediate state green.
- Do not fix new smells unless they block convergence.
- Finish planned call-site migration before local failure repair.

## Rollback definition

Rollback means:
- revert only edits made by this skill
- remove temporary wrappers/functions/tests introduced by this skill
- restore old abstraction and call sites
- record rollback reason
- do not leave partial migration artifacts
