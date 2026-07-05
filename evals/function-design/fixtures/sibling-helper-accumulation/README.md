# sibling-helper-accumulation

## Initial bad design

Several money-formatting helpers repeat the same concept because previous changes avoided replacing the abstraction.

## Task prompt

See `task.md`.

## Expected skill trigger

- `function-boundary-governor`

## Expected final design

- No new sibling helper is added.
- Similar helpers are replaced by a domain concept, `format_money`.
- Call sites migrate.
- Obsolete helpers are deleted.
- Final names are domain concepts, not `common`, `helper`, `handle`, `process`, or `util`.
- Ledger records merge/replace.

## Forbidden final patterns

- `format_subscription_total` added beside old helpers
- Vague function names containing `common`, `helper`, `handle`, `process`, or `util`

## Verification command

```sh
python evals/function-design/fixtures/sibling-helper-accumulation/oracle.py <workspace>
```
