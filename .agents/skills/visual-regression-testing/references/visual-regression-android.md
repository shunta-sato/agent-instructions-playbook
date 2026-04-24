# Android visual regression defaults

Use this guidance with `visual-regression-testing` when the detected UI target is Android.

## Recommended default

Prefer JVM-based screenshot tests over emulator-based screenshots when the repository supports them, because they are usually more deterministic and faster in CI.

## Common tracks

### Paparazzi

- Record snapshots: `./gradlew record...`
- Verify snapshots: `./gradlew verify...`

### Roborazzi

- Record snapshots: `./gradlew record...`
- Verify snapshots: `./gradlew verify...`

Replace `...` with repository-provided Gradle tasks. Do not invent task names when canonical repo commands exist.

## Workflow

1) Run verify task(s) first.
2) Review diff artifacts against intended UI changes and any design mock(s).
3) Record only intentional diffs.
4) Re-run verify and include artifact paths in the report.
