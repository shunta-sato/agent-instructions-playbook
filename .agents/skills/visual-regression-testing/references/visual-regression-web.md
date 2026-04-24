# Web visual regression defaults

Use this guidance with `visual-regression-testing` when the detected UI target is web.

## Recommended default

Use Playwright screenshot snapshots when the repository does not define another web visual regression tool.

## Typical workflow

- Verify snapshots: `npx playwright test`
- Record or update baselines intentionally: `npx playwright test --update-snapshots`

## Environment warning

Baseline generation should run in a stable environment because OS, font rendering, and browser differences can cause false diffs.

## Workflow reminders

1) Run verify first.
2) Compare diffs against intended UI changes and any design mock(s).
3) Update baselines only for expected changes.
4) Re-run verify and include snapshot artifact paths in the report.
