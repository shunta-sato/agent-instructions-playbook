# Function Boundary Design Ledger

## Replaced abstraction: user payload import parsing

Decision: replaced abstraction

Old abstraction:
- `parse_user_payload`

New abstractions:
- `normalize_user_payload`
- `persist_user_payload`
- `preview_user_import`

Reason:
- `parse_user_payload` mixed pure normalization with repository mutation, timestamp assignment, and audit logging.
- Preview import needs normalization without persistence, timestamp writes, or audit entries.
- A flag such as `persist=False` would hide two responsibilities behind one function.

Call-site migration:
- `import_user` now composes `normalize_user_payload` with `persist_user_payload`.
- `update_user_from_admin` now uses the same persistence boundary with explicit `source`.
- `preview_user_import` uses only `normalize_user_payload`.

Do not reintroduce:
- `parse_user_payload`
- `persist=False`
- `skip_persist`
- `dry_run`
- sibling parser names such as `new_parse_user_payload`

Verification:
- `python3 -m unittest discover -s tests`
- `python3 function-design-eval-content/evals/function-design/scripts/run_oracles.py --scenario wrong-side-effect --workspace reports/function-design-evals/20260525-224836/wrong-side-effect/workspace`
