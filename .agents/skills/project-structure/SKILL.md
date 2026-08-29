---
name: project-structure
description: "Use when placing a new source module or test, when a feature adds a distinct responsibility to an oversized file, or when the structure checker reports a hard finding. Advisories prompt local placement judgment without automatically expanding feature scope."
metadata:
  short-description: Two-tier structure guardrails
  resources:
    - references/project-structure-rust.md
---

## Purpose

Prevent unbounded file growth without turning each feature into a historical
codebase decomposition.

`design-balance` decides responsibility ownership. This skill decides physical
placement and whether a local split is needed now.

## Two-tier budget

`python scripts/check_structure.py` supports two modes:

| Surface | Advisory | Feature hard guardrail |
| --- | ---: | ---: |
| source file total lines | 600 | 1500 |
| entrypoint logic lines | 150 | 400 |
| Rust inline-test lines | 300 | 800 |

- `--mode feature`: advisory thresholds return success. New/crossed hard
  guardrails block; a file already above a hard guardrail may grow by at most 50
  net metric lines before the checker treats the change as material worsening.
- `--mode strict`: advisory thresholds are blocking. Use for refactor,
  structure-hardening, or a project policy that explicitly requires it.

Project flags may choose different limits. Generated or vendor-owned paths need a
bounded repository waiver rather than silent exclusion.

## Feature policy

A feature PR must not make structure materially worse, but it does not need to
make surrounding code ideal.

- A pre-existing advisory is not feature scope by itself.
- Existing hard debt may still receive bug fixes and small changes inside its
  current responsibility; the feature checker compares against the base revision.
- Crossing a hard guardrail or adding more than 50 net metric lines to existing
  hard debt blocks mechanically.
- Do not add a distinct new responsibility to an already oversized file; place
  it in a sibling module.
- When safe implementation requires a split, extract only the narrow current
  seam. Do not decompose unrelated historical code.
- A new, crossed, or materially worsened hard-guardrail finding requires a local
  fix or bounded waiver before submit.
- Repeated friction, a second consumer, durable public use, or a hard threshold
  can promote debt into a separate refactor/hardening deliverable.

## How to use

1. Mark the change as `entrypoint | library module | test | config/build glue`.
2. For Rust placement, open `references/project-structure-rust.md`.
3. For feature work, use
   `python scripts/check_structure.py --working-tree --mode feature`.
4. Inspect advisories for a newly added responsibility. Record `accepted debt`,
   `local extraction`, or `new sibling module`.
5. Fix or waive hard findings. Route only the actual ownership/function-move
   decision to `design-balance` or `function-boundary-governor`.

## Output expectation

Return created/split files with roles, checker mode and result, advisory
dispositions, hard findings and fixes/waivers, and any narrow routing handoff.
Do not describe advisory debt as a clean structure pass.
