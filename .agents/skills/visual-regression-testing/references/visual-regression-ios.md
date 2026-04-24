# iOS visual regression defaults

Use this guidance with `visual-regression-testing` when the detected UI target is iOS.

## Recommended approach

- Use the repository's Swift snapshot workflow and keep record/verify modes explicit.
- Prefer deterministic rendering settings: fixed locale, fonts, trait collections, simulator or device configuration, and appearance mode.

## Workflow

1) Verify snapshots in default mode.
2) Inspect diffs against expected UI changes and any design mock(s).
3) Record new baselines only for intentional changes.
4) Re-run verify after recording.

## Environment note

- iOS snapshot generation is typically macOS/Xcode-bound.
- On Linux or non-macOS environments, defer execution to the CI/macOS runner and document that in the report.

## Example placeholders

- `make ui-verify-ios`
- `make ui-record-ios`

These are examples only; always prefer repository-defined commands.
