---
name: code-smells-and-antipatterns
description: "Detect new or worsened code smells / design anti-patterns in the current diff, explain why they matter, and propose the smallest fix. Use for non-trivial structural changes, refactors, or when maintainability regresses."
metadata:
  short-description: Smells & anti-patterns triage
---

## Purpose

This skill is a triage tool to reduce maintainability risk by finding “reader-stoppers” at the design level, not to enable big refactors.

## When to use (trigger conditions)

Agents MUST use this skill when any of the following applies:

- New module/subsystem or new “main” class is introduced.
- A change introduces or edits public APIs or cross-module boundaries.
- A change increases indirection/flags/config branching, or creates new “manager/service” hubs.
- A refactor moves logic across files or layers (controller/usecase/domain/adapters/etc.).
- Review request explicitly mentions: smell / anti-pattern / god object / big ball of mud / anemic domain model / shotgun surgery / etc.

If none applies, do not force it.

## How to use (procedure; must be stepwise)

1) Identify the **units** impacted by the diff (files + key functions/classes).
2) Scan for **new or worsened** smells only.
3) Produce **up to 3 findings**, each with:
   - name (smell/anti-pattern label)
   - “why this looks like it” (evidence from diff)
   - risk if left as-is
   - smallest fix (prefer minimal diff)
   - which existing skill to invoke for the fix (`$code-readability`, `$modularity`, `$architecture-boundaries`, `$working-with-legacy-code`, `$error-handling`, `$observability`, `$test-driven-development`)
4) If you choose NOT to fix now, you MUST state:
   - why it is not new/worsened, or
   - why fixing now would increase risk, and
   - what to monitor (tests/metrics/logs) until a planned follow-up.

## Output expectation (strict format)

Require the output to include:

## Smells & Anti-patterns Review
- Scope: (changed units)
- Findings: (0–3 items)

For each finding:
### Finding N: <label> (type: smell|design anti-pattern|architecture anti-pattern; impact: blocker|important|nice-to-have)
- Introduced/Worsened by this diff?: yes|no
- Evidence (diff-level):
- Why it matters here:
- Smallest fix:
- Skill to apply:
- If not fixing now (only allowed if not introduced/worsened): justification + follow-up note

If there are 0 findings:
- State: “No new/worsened smells found” and list what you checked.
