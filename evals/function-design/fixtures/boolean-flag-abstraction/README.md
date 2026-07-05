# boolean-flag-abstraction

## Initial bad design

`build_invoice_payload` already has an `include_tax` flag. A new audit export would naturally add another flag or mode, turning one function into several responsibilities.

## Task prompt

See `task.md`.

## Expected skill trigger

- `function-boundary-governor`

## Expected final design

- No new boolean or optional behavior switch is introduced.
- Responsibilities split into clear concept functions.
- Call sites read as domain operations.
- Behavior remains covered.

## Forbidden final patterns

- `include_tax`, `include_notes`, `dryRun`, `legacy`, `mode`
- One function branching between summary, tax, and audit responsibilities

## Verification command

```sh
python evals/function-design/fixtures/boolean-flag-abstraction/oracle.py <workspace>
```
