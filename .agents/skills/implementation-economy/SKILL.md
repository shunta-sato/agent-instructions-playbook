---
name: implementation-economy
description: "Use before and after normal/high-risk implementation when a complexity budget is needed: declare new classes/helpers/wrappers/indirection/estimated lines, justify each new abstraction, and delete or inline abstractions that are not worth their weight. Do not use for low-risk one-file changes with no new abstraction, public API change, or behavior expansion."
metadata:
  short-description: Implementation complexity budget
---

## Purpose

Use this skill to keep implementation scope small enough to review, test, and maintain.

It answers one question:

**Is each new abstraction or layer worth the future cost it adds?**

## When to use

Use this skill when one or more applies:

- `dev-workflow` selects the normal/high-risk default implementation lane.
- The implementation adds classes, modules, helpers, wrappers, adapters, or new indirection.
- The implementation could solve the problem either by reusing existing code or by adding a new abstraction.
- A review asks for less code, less layering, fewer helpers, or simpler implementation.

Do not use it for low-risk edits that touch one file, add no abstraction, keep public APIs unchanged, and do not expand behavior.

## How to use

1. Before editing, write a **Complexity Budget**:
   - changed files target
   - new classes/modules target
   - new helpers/wrappers/adapters target
   - new indirection layers target
   - rough production/test line budget
   - When working under an ExecPlan with quantitative targets, reconcile this
     change-level budget with the plan's contribution decomposition (the net
     line budgets across phases must sum to the plan target, or the plan
     forecast must be updated).

2. Prefer reuse, deletion, inlining, or local changes before adding a new abstraction.

3. For each new abstraction, write a one-line **worth-its-weight** justification:
   - what complexity it removes
   - what duplication or boundary risk it prevents
   - why the existing code cannot carry the behavior cleanly

4. After implementation, produce a **Post-Implementation Economy Audit**:

   | New abstraction | Justification | Decision | Evidence |
   |---|---|---|---|
   | `<name>` | `<why it is worth its weight>` | `keep/delete/inline/merge` | `<tests, call sites, or diff evidence>` |

5. If the implementation exceeds the budget, first delete, inline, or merge unjustified abstractions. If the budget must grow, record the reason and the smallest acceptable increase.

6. Hand off to `design-balance` when module/class responsibility layout is unclear, and to `function-boundary-governor` when function/helper/API shape is the main decision.

## Output expectation

Return:

- Complexity Budget (5 lines).
- Post-Implementation Economy Audit table.
- Any budget overruns and what was deleted, inlined, merged, or intentionally kept.
