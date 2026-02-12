# ui-verify

Use this prompt when UI code changes or when asked for screenshot/snapshot/pixel-perfect validation.

## Workflow

1) Identify platform(s): iOS, Android, web.
2) Invoke `$visual-regression-testing`.
3) Invoke matching platform skill(s): `$visual-regression-ios`, `$visual-regression-android`, `$visual-regression-web`.
4) Run repo-defined verify command(s), collect artifact paths, and review visual diffs.
5) Update baselines only for intentional changes.
6) Output the exact **UI Visual Verification Report** format.
