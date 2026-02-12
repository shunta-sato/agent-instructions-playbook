# Web visual regression defaults

Use this reference with `$visual-regression-testing` for web platform defaults.

## Recommended default

Use Playwright screenshot snapshots as the default verification mechanism.

## Typical workflow

- Verify snapshots: `npx playwright test`
- Record/update baselines intentionally: `npx playwright test --update-snapshots`

## Environment warning

Baseline generation should run in a stable environment because OS, font rendering, and browser differences can cause false diffs.

## Workflow reminders

1) Run verify first.
2) Compare diffs against intended UI changes and any provided design mock(s).
3) Update baselines only for expected changes.
4) Re-run verify and include snapshot artifact paths in the report.
