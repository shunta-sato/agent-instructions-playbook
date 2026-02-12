# Visual regression testing (tool-agnostic contract)

This reference defines a platform-agnostic UI verification contract based on **repo-provided commands**.

## Required contract

The repository must expose one canonical interface:

### Option A: Make targets
- `make ui-verify` (generate + compare; fails on diff)
- `make ui-record` (intentionally update baselines)
- `make ui-artifacts` (optional; collect artifacts)

### Option B: Script entrypoints
- `./tools/ui/verify.sh`
- `./tools/ui/record.sh`

## Discovery order

1) Prefer Make targets when available.
2) Otherwise use `./tools/ui/verify.sh` and `./tools/ui/record.sh`.
3) If neither exists, fail fast with a clear remediation note for maintainers.

## Required execution flow

1) Detect changed UI surface and target platform(s): `ios | android | web`.
2) Run verify command.
3) Capture snapshot outputs/artifact paths.
4) If verify fails on visual diff:
   - inspect diffs and compare with requested behavior and design mock(s), when provided,
   - record whether diff is expected or a defect.
5) Only when expected: run baseline update command and re-run verify.
6) Produce the report in the exact format below.

## Exact output format (mandatory)

```markdown
## UI Visual Verification Report
- Platform: ios|android|web
- Environment: OS + key tool versions
- Command(s) executed:
- Snapshot output path(s):
- Baseline updated?: yes|no
- Review summary:
  - If diff: why accepted or what to fix
  - If cannot run: why + how CI should cover it
```

## Notes

- Keep tool choice configurable in the repository; this skill only defines the contract.
- Prefer deterministic environments (container or pinned CI runner) for baseline generation.
- If local execution is impossible, document the exact CI job that must validate snapshots.
