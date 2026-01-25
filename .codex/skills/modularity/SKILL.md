---
name: modularity
description: "Modularity handbook (cohesion/coupling/boundaries). Evaluate design at the lowest unit, judge by the worst level, and propose fixes that reduce change ripple. Always open references/modularity.md and cite headings."
metadata:
  short-description: Modularity (cohesion/coupling)
---

## Purpose

Use this skill to evaluate and improve **modularity**: keep responsibilities tightly grouped (cohesion), keep dependencies small and stable (coupling), and keep boundaries explicit.

This skill fixes one common failure mode: judging “module quality” only at a high level. Here, you always evaluate at the **lowest meaningful unit** (function / class / small module) and use the **worst** rating as the truth.

## When to use

Use this skill when:

- You are unsure whether a change made a module “too mixed” or “too entangled”.
- You want to refactor to reduce change ripple, without rewriting everything.
- You are reviewing an AI-written change and need an objective explanation and a concrete fix plan.

## How to use

0) Open `references/modularity.md`. Select **1–3 relevant headings** and cite them by heading name in your reasoning.

1) Decide the evaluation unit (usually a single function, a class, or a small file section). List the units you will judge.

2) For each unit:
   - Rate cohesion at the **worst** level present.
   - Rate coupling at the **worst** level present.
   - Identify boundary leaks (external types, vendor exceptions, “framework objects” flowing inward).

3) Propose the smallest fix that improves the worst rating:
   split time/procedural cohesion into smaller functional units, isolate “translation glue” at boundaries, introduce a thin wrapper, or restructure data flow.

4) Re-check: does the change reduce reader confusion and reduce future change ripple?

## Output expectation

- Provide a short rating summary (worst level + reason) and a fix plan with minimal diffs.
- If you propose a larger change, justify it with: reduced ripple, simpler tests, and clearer boundaries.
