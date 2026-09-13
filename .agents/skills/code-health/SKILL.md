---
name: code-health
description: "Prevent unjustified complexity when extending shared behavior, adding similar code or permanent abstractions, or integrating delegated changes. Not a whole-repository polish gate."
---

# Code health under continued change

Judge the retained design against current use, actual compatibility obligations and
plausible maintenance work. Passing tests proves observed behavior, not maintainability.
A capable supervisor is responsible for the integrated design, including its own plan.

## Choose the owner before adding another implementation

Inspect the existing rule, state owner, callers and relevant tests. Distinguish identical
business meaning from coincidentally similar syntax. Extend or reshape the existing owner
when that expresses this change better; related internal refactoring is part of delivery.
Do not require a refactoring pass or generalize for imagined future consumers. Preserve
intentional duplication when the behaviors change for different reasons.

New wrappers, compatibility paths, fallback behavior, configuration and dependencies need
a present consumer, constraint or demonstrated benefit. Unknown external consumers require
investigation, not assumed absence or invented support. A break-allowed scope permits removal
of the superseded path; it does not waive persistent-data or external-service obligations.
Comments preserve reasons, invariants, hazards and public usage, not a narration of each line.
Do not compress code or remove useful explanation merely to reduce lines.

## Delegate without losing design responsibility

Partition by ownership and dependency, not only disjoint files. Give workers the outcome,
shared rule owner, preserved/replaceable contracts, relevant proof and authority to make
necessary internal changes. They may challenge the decomposition with evidence. Coordinate
shared-owner changes instead of letting each worker invent its own adapter or rule copy.
Do not assume a parent's Skill context automatically reaches a child.

Review actual integrated code and affected callers/tests, not just worker summaries or
check counts. Inspect the supervisor's proposed architecture too. Use an independent review
when the consequence justifies it; another model is not automatically an independent oracle.
Do not hardcode model-family stereotypes, fixed role rosters or reviewer quotas.

## Resolve concrete findings and finish

Use `references/review.md` for examples or a consequential design question. A useful finding
identifies the location, actual burden/failure/change scenario, and a bounded alternative
with its trade-offs. A score or preference without a mechanism is not a blocking finding.

Protect behavior with the agreed acceptance/E2E and focused tests while removing accidental
complexity. For important shared changes, inspect or exercise a representative next edit or
diagnosis in a disposable branch. Do not ship that hypothetical feature or require this drill
for every edit. Keep legitimate constraints, error behavior and performance evidence intact.

Finish once required behavior/proof and the selected concrete findings are resolved. Leave
unrelated debt alone; do not demand universal zero warnings or an infinite cleanup pass.
For an explicitly degraded codebase, use a bounded rehabilitation scope rather than turning
an ordinary feature request into a rewrite. Report material design changes in the current PR.
