---
name: requirements-engineering
description: "Use when acceptance is ambiguous or non-trivial, or lifecycle, workload, failure impact, or operating constraints expose unresolved quality requirements. Form verifiable functional/NFR conditions before design; do not require a specification for small work with current inherited context."
metadata:
  short-description: Requirements engineering
  resources:
    - references/ears-requirements-to-design.md
    - references/iso25010-quality-scenarios.md
    - references/mobile-quality-scenarios.md
    - references/requirements-briefs-and-specs.md
    - references/quality-context.md
---

## Purpose

Turn the present use into verifiable functional and quality requirements without
creating a full specification for every task. Discover necessary NFRs even when
the request names only a feature; do not invent hypothetical future consumers.

## When to use

Use when acceptance cannot be stated from existing evidence, workload/lifecycle/
operating assumptions change a design decision, risky or cross-component work
needs requirements first, or a brief/spec is requested. Vague words such as fast,
reliable, maintainable, or production-ready require applicable criteria.

Tiny unambiguous work can inherit current context and tests. File/module count
alone does not determine requirement depth. `architecture-decision-analysis`
compares designs after decision-driving requirements are sufficiently understood.

## How to use

1. Reuse the current product/component contract and inspect task deltas. If scope,
   problem ownership, or solution-first framing is unclear, state a small Problem
   Frame. Do not ask again for facts already present in trusted task context.
2. Open only what changes a decision:
   - `references/quality-context.md` for missing/stale context, NFR discovery,
     obligation/evidence separation, sources, thresholds, and handoff semantics;
   - `references/iso25010-quality-scenarios.md` for relevant quality attributes;
   - `references/requirements-briefs-and-specs.md` for requested briefs/specs;
   - `references/ears-requirements-to-design.md` for EARS wording and test seeds;
   - `references/mobile-quality-scenarios.md` for mobile/platform requirements.
3. Establish use/failure impact, lifespan/expected changes, workload/cadence/scale,
   operation/recovery/update, and applicable obligations. Separate confirmed,
   inferred, and unknown facts. Industry labels are not risk classifications.
4. Define only relevant functional/NFR requirements. Quality Targets preserve
   `ID/behavior | applies-to/workload | required/target/out-of-scope | source/status |
   criterion | verification method | result/evidence identity | revisit condition`.
   These fields can live in prose or the existing plan/PR, not a new schema/file.
5. Separate required criteria from optional targets and from measured baselines.
   Do not pick thresholds merely to pass current code. A provisional proposal
   needs its source and resolution/revisit condition, not a production guarantee.
6. For maintainability use expected change/diagnosis/upgrade/handoff scenarios,
   not design scores or lifespan alone. Keep necessary safety and useful comments
   without requiring generic extensibility or redundant narration.
7. Choose proof proportionate to impact and uncertainty: inspection/analysis,
   focused tests/measurements, or target/workload/assurance evidence. Missing
   required proof remains blocking for its intended use, even if labeled unmeasured.
8. Route non-embedded scaling/latency/resource decisions to `performance-review`.
   Route physical target constraints to `embedded-nfr-design` and only missing
   characterization/calibration stages. Do not finalize target-validated claims
   without target evidence; host measurements do not substitute.
9. For cross-platform mobile capability, send stable requirements and quality
   conditions to `mobile-feature-parity`. It owns platform evidence/deviations.
10. Include required quality in DoD before locking the route. Trace it to tests
    (the TDD Test List only when TDD is selected) and `quality-gate`. Newly found
    present-use obligations can revise affected acceptance; preserve source and
    owner authority. Do not let scope lock suppress a necessary quality requirement.

## Output expectation

Return the smallest useful Problem Frame, brief/spec, or plan/PR section with
functional acceptance, relevant Quality Targets, material assumptions/unknowns,
verification and routing. Reuse context references and IDs where they aid handoff.
Do not populate every ISO category, require a numerical NFR score, or duplicate
existing requirements. The gate must receive the same applicability and criteria.
