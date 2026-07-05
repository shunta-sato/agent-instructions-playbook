# no-op-small-duplication

## Initial bad design

Tests repeat tiny order dictionaries. The duplication is fixture-like and likely clearer inline.

## Task prompt

See `task.md`.

## Expected skill trigger

- `function-boundary-governor`

## Expected final design

- No production refactor.
- No generic helper introduced.
- Ledger or report records no-op / keep-parallel reasoning.
- Tests remain unchanged or minimally updated.

## Forbidden final patterns

- Production helper for test fixture data
- New `common`, `helper`, or `util` function/module

## Verification command

```sh
python evals/function-design/fixtures/no-op-small-duplication/oracle.py <workspace>
```
