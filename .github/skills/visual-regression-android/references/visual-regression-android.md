# Android visual regression defaults

Use this reference with `$visual-regression-testing` for Android-specific guidance.

## Recommended default

Prefer JVM-based screenshot tests (no emulator) for deterministic and faster CI verification.

## Example tracks

### Track A: Paparazzi

- Record snapshots: `./gradlew record...`
- Verify snapshots: `./gradlew verify...`

### Track B: Roborazzi (Compose preview/task flows)

- Record snapshots: `./gradlew record...`
- Verify snapshots: `./gradlew verify...`

Replace `...` with repository-provided tasks.

## Workflow

1) Run verify task(s) first.
2) Review diff artifacts and compare with intended UI changes/mock(s).
3) Record only intentional diffs.
4) Re-run verify and include artifact paths in the report.
