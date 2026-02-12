---
name: quality-gate
description: "MANDATORY final gate before submission: make checks all green (build/format/static-analysis/tests) and review readability, modularity, boundaries, and error paths. Produce the required self-review with concrete checklists."
metadata:
  short-description: Final quality gate
---

## Purpose

Use this skill as the last step before submitting a change.

It combines two things:

1) verification (build/format/static-analysis/tests)
2) a structured review against this repo’s standards

## When to use

Invoke this skill **before every submission**. It is mandatory.

## How to use

0) Open `references/quality-gate.md` and run the checklist.

1) Run the canonical commands for build / format / static analysis / tests.
   - If a command cannot be run, explain why and provide a reproducible procedure.

2) Review the diff with the checklists:
   - Readability (naming, comments, control flow, tests)
   - Modularity / coupling / boundaries (worst-level rating)
   - Boundary error handling (translation, no swallowed failures)
   - Concurrency (plan, shutdown/cancellation, observability, verification)
   - Observability (logs/metrics/traces for runtime behavior changes)
   - UI verification gate (report exists, snapshot status is explicit, artifacts listed)
   - Documentation (requirements / acceptance criteria / verification method)
   - Constrained code synthesis (when applicable): staged-lowering plan + per-pass verification log exists; edge cases handled in a dedicated pass
  - Bugfix evidence + report (when bugfix mode triggered):
    - Bug Report exists (PR description, issue comment, or docs file).
    - Report includes repro (or why impossible), evidence, Five Whys root cause, verification, and at least one measurable prevention action.
    - Workaround-only changes include documented risk, removal plan, and follow-up tracking task.

3) If you changed C++:
   - `.hpp`: verify Doxygen completeness for all declarations (including private).
   - `.cpp`: verify intent-first comments and a magic-value audit.

4) Fix findings and repeat until 0 findings remain.

## Output expectation

- Output “0 findings” only when checks and checklist are fully satisfied.
- Otherwise, list each finding with: location, why it matters, and the concrete fix applied (or the reason it remains).
