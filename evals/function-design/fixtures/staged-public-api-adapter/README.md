# staged-public-api-adapter

## Initial bad design

`build_account_record` is a public API-shaped function used by internal callers even though its contract is flawed. Internal code can migrate now, but external callers need temporary compatibility.

## Task prompt

See `task.md`.

## Expected skill trigger

- `function-boundary-governor`
- `destructive-refactor`

## Expected final design

- Internal call sites migrate to `build_customer_profile`.
- Public adapter remains only as a thin staged compatibility layer.
- Adapter has tests and a ledgered removal condition.
- No broad compatibility layer is introduced.

## Forbidden final patterns

- Internal callers still using `build_account_record`
- Adapter without staged migration ledger
- Broad `compat`, `legacy`, or `shim` layer around the module

## Verification command

```sh
python evals/function-design/fixtures/staged-public-api-adapter/oracle.py <workspace>
```
