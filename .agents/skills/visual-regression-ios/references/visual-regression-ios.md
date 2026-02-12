# iOS visual regression defaults

Use this reference with `$visual-regression-testing` for platform-specific defaults.

## Recommended approach

- Use a Swift snapshot testing library and keep record/verify modes explicit.
- Prefer deterministic rendering settings (fixed locale, fonts, trait collections, simulator/device config).

## Workflow

1) Verify snapshots (default mode).
2) Inspect diffs against expected UI changes and provided design mock(s).
3) Record new baselines only for intentional changes.
4) Re-run verify after recording.

## Environment note

- iOS snapshot generation is typically macOS/Xcode-bound.
- On Linux or non-macOS environments, defer execution to CI/macOS runner and document that in the report.

## Example command placeholders

- `make ui-verify-ios`
- `make ui-record-ios`

These are examples only; always prefer repository-defined commands.
