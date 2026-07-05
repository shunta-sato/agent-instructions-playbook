# intentional-parallelism

## Initial bad design

Two parsing functions look similar but intentionally differ in error behavior. One is strict for required fields; the other is lenient for optional fields.

## Task prompt

See `task.md`.

## Expected skill trigger

- `function-boundary-governor`

## Expected final design

- Functions remain parallel.
- No shared generic helper or boolean mode flag is introduced.
- Behavior remains unchanged.
- Ledger records intentional duplication / keep-parallel reasoning.

## Forbidden final patterns

- `_parse_int(required=...)`
- `parse_int(..., required=True)`
- Generic shared helper hiding different error behavior

## Verification command

```sh
python evals/function-design/fixtures/intentional-parallelism/oracle.py <workspace>
```
