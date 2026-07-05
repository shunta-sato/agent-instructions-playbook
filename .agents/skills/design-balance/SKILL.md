---
name: design-balance
description: "Use before feature-level implementation that adds two or more classes/modules, introduces a new layer/interface, or adds a second reason-to-change to an existing class/module. Do not use for function-only helper/API decisions or cross-boundary architecture option comparison."
metadata:
  short-description: Responsibility layout design
---

## Purpose

Use this skill to choose the right module/class shape before implementation grows into either too many layers or one oversized unit.

It answers one question:

**Which units should exist, what is each unit responsible for, and why would each unit change?**

## When to use

Use this skill when a change:

- adds two or more classes/modules/files with distinct roles
- introduces a new layer, interface, adapter, or coordinator
- adds a new responsibility to an existing class/module
- risks a large class, god object, unclear service/manager hub, or excess layering
- needs names checked against responsibilities

### Checkable thresholds

- **large class/module** = any of: >400 lines (the structure budget), OR >7 public functions/methods, OR ≥3 distinct reasons to change.
- **god object / unclear hub** = a unit that ≥3 otherwise-unrelated modules depend on AND that owns ≥3 distinct reasons to change.
- **excess layering** = a layer that only forwards calls without transforming data or enforcing an invariant, OR a single operation crossing >3 internal layers.

Do not use it for:

- function/helper/API boundary decisions only; use `function-boundary-governor`
- cross-boundary architecture or technology choices; use `architecture-decision-analysis`
- pure readability cleanup with no module/class responsibility change

## How to use

1. List the feature's required responsibilities in plain words.

2. Draft a **Responsibility Map**:

   | Unit | Name | Responsibility sentence | Reason to change | Dependency direction |
   |---|---|---|---|---|
   | `<class/module>` | `<name>` | `<one sentence>` | `<single reason>` | `<depends on / depended on by>` |

3. Apply the balance rules:
   - If a responsibility sentence needs "and", mode flags, or unrelated verbs, split the unit.
   - If two units share the same reason to change and do not protect a real boundary, merge them.
   - Add a layer or interface only when the units on each side have different reasons to change.
   - If the name does not predict the responsibility sentence, rename before implementing.
   - Keep dependency direction pointing toward stable policy and away from volatile details.

4. Check risk separately from benefit:
   - Benefit: clearer change locality, invariant ownership, call-site readability, testability.
   - Risk: extra files, parameter pressure, boundary leakage, naming vagueness, review cost.

5. Decide `keep-layout`, `split`, `merge`, `rename`, `remove-layer`, or `defer-no-op`.

6. Hand off to `implementation-economy` for complexity budget pressure and to `code-smells-and-antipatterns` for current-diff maintainability findings.

## Output expectation

Return:

- Responsibility Map table.
- Layout decision with rejected alternatives.
- Any units renamed, split, merged, removed, or intentionally left as-is.
