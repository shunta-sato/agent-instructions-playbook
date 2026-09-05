---
name: dev-workflow
description: "Use for delivery-mode code or test changes after feature scope has been governed when applicable. Selects risk, work intent, compatibility mode, and only the specialist branches supported by concrete facts before editing."
metadata:
  short-description: Risk-routed dev workflow
  requires:
    - references/dev-workflow.md
---

## Purpose

Route implementation work without allowing process, review, or maintenance
concerns to silently expand the requested capability.

## When to use

Use for delivery-mode code or test changes. Feature campaigns, backlog work, and
stalled feature PRs first use `user-value-delivery`; research paths use
`research-workflow` until promotion.

## How to use

0) Open `references/dev-workflow.md`; use applicable sections and reuse decisions
already established for this task.

1) Record risk, failure criticality, maintenance horizon, work intent, and
compatibility mode from §0, §0a, and §0b.

2) Build the shortest vertical path in §1. Use focused tests while iterating.

3) Select only fact-triggered branches from §2, applying §2a and §2b when
embedded or overlapping decisions exist.

4) Record the Route Summary in §3 before implementation. The route is then
locked; add a branch only for newly discovered blocking evidence.

5) Apply the structure watch in §2c. Advisory findings do not expand a feature;
blocking hard-guardrail findings require a local fix or bounded waiver.

6) During the existing diff review, remove additions with no current requirement:
future-only abstractions, unneeded compatibility paths, silent error fallbacks,
redundant comments/docstrings, and permanent scratch artifacts. Follow existing
patterns; keep useful helpers, trust-boundary checks, required tests/API docs,
licenses, tool directives, and non-obvious constraints. Do not narrate obvious
code, add comments to untouched code, or require a separate anti-slop checklist.

7) Verify at the depth selected in §0 and hand the identified candidate to the
single final-gate owner under §6. Re-run affected proof after any cleanup edit;
an earlier green result does not cover a changed candidate automatically.

## Output expectation

State the selected route, risk and rationale, failure criticality, maintenance
horizon, triggered branches, deferred branches, structure result, focused proof,
verification depth, candidate identity, and final-gate owner.
