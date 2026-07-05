---
name: visual-regression-testing
description: "Use when UI changes require repo-defined snapshot or visual-diff verification, baseline review, or a UI Visual Verification Report."
metadata:
  short-description: Tool-agnostic UI visual verification contract
  requires:
    - references/visual-regression-android.md
    - references/visual-regression-ios.md
    - references/visual-regression-testing.md
    - references/visual-regression-web.md
---

## Purpose

Use this skill to enforce a consistent UI visual verification contract without hard-coding a specific test framework.

## When to use

- Any UI code changed (iOS/SwiftUI, Android/Compose/XML, web UI/components/styles).
- The request mentions pixel perfect, UI matches design, snapshot, or screenshot.

## How to use

1) Open `references/visual-regression-testing.md`.
2) For Android, iOS, or web targets, also open the matching platform reference in `references/`.
3) Discover the live UI verify/record interface from repo commands, CI config, tool help, and snapshot config before trusting examples.
4) Review produced artifacts and compare against baselines/design mocks.
5) Update baselines only for intentional UI changes.
6) Output the required report format exactly.

## Gotchas

- **Common pitfall:** skipping snapshot verification even though UI changed.
  **Instead:** run the repo-defined UI verification command and always check whether diffs exist.
- **Common pitfall:** recording failed snapshots in bulk without root-cause review.
  **Instead:** review diff images and apply only intended changes to baseline.
- **Common pitfall:** omitting artifact paths in reports, preventing reviewer recheck.
  **Instead:** explicitly include compare result, update status, and relative artifact paths in output format.
- **Common pitfall:** assuming visual differences are environment-only and leaving them unresolved.
  **Instead:** separate font/resolution/theme/locale differences and record reproduction conditions before judgment.
- **Common pitfall:** trusting stale snapshot commands or artifact paths.
  **Instead:** capture the command source, tool versions, device/browser connection state, config/baseline paths, and produced artifact paths.

## Output expectation

Produce a `## UI Visual Verification Report` with exactly these fields (see `references/visual-regression-testing.md` for the mandatory format):
- Platform: `ios|android|web`
- Environment: OS + key tool versions
- Live discovery evidence: command source + config/baseline path + device/browser/CI state
- Command(s) executed
- Snapshot output path(s)
- Baseline updated?: `yes|no`
- Review summary: reasoning for accepted diffs, or why the check could not run and how CI should cover it
