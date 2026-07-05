# wrong-side-effect

## Initial bad design

`normalize_and_save_user` mixes pure user normalization with persistence mutation. Existing import behavior depends on persistence, while a new preview flow needs normalization without writes.

## Task prompt

See `task.md`.

## Expected skill trigger

- `function-boundary-governor`
- `destructive-refactor`

## Expected final design

- Pure normalization is separated from effectful persistence.
- Existing persistence behavior is preserved through a clearly effectful call site.
- Old mixed abstraction is deleted, not kept beside a new sibling.
- Call sites migrate to `normalize_user` or `save_normalized_user`.
- Tests cover pure normalization and persistence behavior.
- Ledger records the replaced abstraction.

## Forbidden final patterns

- `normalize_and_save_user` production references
- `withoutSideEffects`, `dryRun`, `skipPersist`, `x2`, `newX`
- Boolean flag used to suppress persistence

## Verification command

```sh
python evals/function-design/fixtures/wrong-side-effect/oracle.py <workspace>
```
