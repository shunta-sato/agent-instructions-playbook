---
name: dev-workflow
description: "Use for delivery-mode code or test changes after feature scope has been governed when applicable. Establish or inherit quality context, then select risk, intent, compatibility, and fact-triggered specialist branches before editing."
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
0) Open `references/dev-workflow.md`; reuse current context and applicable decisions.
1) Apply §0–§0c: risk, criticality, lifecycle/changes, intent, compatibility, and
quality context. Missing workload or required quality is not automatically low risk.
2) Build §1's vertical path with functional and required NFR acceptance.
3) Select fact-triggered branches from §2; use §2a and §2b when needed.
4) Record §3's route summary. New present-use evidence can revise the affected DoD.
5) Apply §2c's structure watch; advisory findings do not enlarge scope.
6) In the existing diff review, remove future-only abstractions, unneeded legacy
paths, silent error fallbacks, redundant comments/docstrings, and permanent scratch
artifacts. Keep quality-required boundaries, useful helpers, tests/API contracts,
licenses, tool directives, and non-obvious constraints. No separate slop checklist.
7) Verify the selected contract and hand the candidate to §6's single gate owner.
Re-run affected proof after cleanup or changes to workload/target assumptions.

## Output expectation
State route/risk and rationale, criticality/horizon, quality-context deltas,
triggered branches, material deferrals, focused proof, candidate, and gate owner.
