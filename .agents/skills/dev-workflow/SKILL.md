---
name: dev-workflow
description: "Use for delivery-mode code or test changes after feature scope has been governed when applicable. Selects risk, work intent, compatibility mode, and only the specialist branches supported by concrete facts before editing."
metadata:
  short-description: Risk-routed dev workflow
  requires:
    - references/dev-workflow.md
---

## Purpose
Route implementation without letting process or maintenance expand the capability.

## When to use
Use for delivery-mode code/test changes. Feature campaigns and stalled feature
PRs first use `user-value-delivery`; research paths use `research-workflow`.

## How to use
0) Open `references/dev-workflow.md`; use applicable sections and reuse decisions
already established for this task.
1) Record risk, failure criticality, maintenance horizon, work intent, and
compatibility mode from §0, §0a, and §0b.
2) Build the shortest vertical path in §1; use focused tests during iteration.
3) Select only fact-triggered branches from §2, applying §2a and §2b when needed.
4) Record the Route Summary in §3. Add branches only for new blocking evidence.
5) Apply §2c's structure watch. Advisory findings do not expand scope; blocking
hard-guardrail findings require a local fix or bounded waiver.
6) In the existing diff review, remove additions with no current requirement:
future-only abstractions, unneeded compatibility paths, silent error fallbacks,
redundant comments/docstrings, and permanent scratch artifacts. Follow existing
patterns; keep useful helpers, trust-boundary checks, required tests/API docs,
licenses, tool directives, and non-obvious constraints. Do not narrate obvious
code, add comments to untouched code, or require a separate anti-slop checklist.
7) Verify at §0's required depth and hand the candidate to the single final-gate
owner under §6. Re-run affected proof after cleanup; earlier green evidence does
not automatically cover a changed candidate.

## Output expectation
State route/risk and rationale, criticality/horizon, triggered/deferred branches,
structure result, focused proof, verification depth, candidate, and gate owner.
