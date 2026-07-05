# No-Skill Control Summary: intentional-parallelism

This control workspace represents a direct DRY refactor without applying the function-design skills.

## Result

- Unit tests: pass
- Design oracle: fail
- Failure mode: introduced a generic `parse_discount_code` helper with a `strict=` behavior switch.

## Evidence

- Unit tests: `verification-output.txt`
- Oracle: `oracle-output.txt`
- Diff from baseline: `diff.patch`
- Workspace: `workspace/`
