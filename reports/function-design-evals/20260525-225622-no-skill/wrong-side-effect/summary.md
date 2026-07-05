# No-Skill Control Summary: wrong-side-effect

This control workspace represents a direct implementation without applying the function-design skills.

## Result

- Unit tests: pass
- Design oracle: fail
- Failure mode: added `persist=` behavior switch and kept the old mixed abstraction.

## Evidence

- Unit tests: `verification-output.txt`
- Oracle: `oracle-output.txt`
- Diff from baseline: `diff.patch`
- Workspace: `workspace/`
