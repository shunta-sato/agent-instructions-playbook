---
name: implementation-economy
description: "Use when a change introduces a persistent abstraction, wrapper, adapter, layer, or generic infrastructure, or when supporting implementation risks becoming larger than the remaining user-facing behavior. Do not use for a local helper whose purpose is obvious and confined to the current feature."
metadata:
  short-description: Scope-inversion and abstraction budget
---

## Purpose

Keep implementation proportional to the current contract. This is not a required
audit for ordinary local code, nor a requirement to minimize lines at any cost.

## When to use

Use for a new lasting boundary, speculative generic infrastructure, proposed
layering, or support work that may displace the requested capability. A small
local helper, ordinary reuse, or test fixture does not itself trigger this skill.

## How to use

1. Identify the behavior still missing. Reuse the current DoD and project budget;
   do not invent a file/line quota or separate audit artifact.
2. For a persistent addition, identify its present consumer or explicit contract,
   the concrete complexity it removes, and why the existing/local path is not
   sufficient. One sentence is usually enough; no numerical score is required.
3. Prefer the existing pattern or direct implementation unless evidence supports
   a lasting boundary. One consumer can justify a boundary for a real security,
   resource, platform, or testing constraint; consumer count alone is not a gate.
4. Review support-work growth against necessity, not just size. Stop speculative
   expansion, but do not discard required infrastructure because it exceeds a
   short call site. Ask for a scope decision only for materially different work.
5. In the existing diff review, keep justified additions and remove those with no
   current requirement. Do not review untouched code or launch another audit.

## Speculative additions to reject

Unless required by the current task, supported callers, or applicable policy:
- factories, registries, plugin systems, configuration surfaces, wrappers, and
  dependency injection introduced only for hypothetical future implementations;
- legacy adapters, migration scaffolding, backfills, or fallback paths without a
  supported compatibility obligation; a `preserve` contract still takes priority;
- repeated validation of established internal invariants, catch-all handlers that
  hide failures, or success-shaped defaults for an error the caller must observe;
- permanent harnesses and extra test files promoted from disposable probes;
- preparatory refactors and broad cleanup unrelated to the requested behavior.

Keep validation at real trust boundaries, authorized retries with failure
semantics, necessary resource cleanup, regression tests, and diagnostics for
supported failures. Removing these is not simplicity. A small helper that names
a real concept is not slop; a large deletion is not automatically an improvement.

## Output expectation

Report only material addition/removal decisions and unresolved scope questions in
the current plan or PR. No per-function inventory, numeric score, or standalone
budget is needed unless explicitly required by an actual consumer.
