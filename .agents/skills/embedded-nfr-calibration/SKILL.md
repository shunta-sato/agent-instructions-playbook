---
name: embedded-nfr-calibration
description: "Use after target characterization or operating-envelope discovery to derive embedded NFR budgets with provenance, confidence, and revisit conditions. Do not use to invent budgets without target evidence unless explicitly marking them provisional."
metadata:
  short-description: Embedded NFR calibration
---

## Purpose

Use this skill to derive or revise embedded NFR budgets from target evidence.

It answers one question:

**Which budget values are production constraints, where did they come from, how confident are they, and when must they be revisited?**

## When to use

Use this skill when:

- physical budget values need to be set or revised
- target baselines or operating envelope results exist
- default, burst, or degraded budgets must be calibrated
- existing budgets have no provenance
- budgets were guessed, copied from a template, or only host-measured

Do not use it when no target evidence exists and the task is only project bootstrap, unless budgets are explicitly marked provisional or unknown.

Use `embedded-system-familiarization` when budget calibration depends on target capability, workload mapping, bottleneck/margin analysis, and architecture constraints, not only numeric baseline reports.

## How to use

1. Gather inputs:
   - target characterization
   - operating envelope reports
   - user-mandated constraints
   - standard or platform guidance
2. Fill `templates/nfr-calibration.md`.
3. Create or update `templates/calibrated-nfr.yaml` in the project budget path.
4. For each production budget, record source, evidence, confidence, rationale, and revisit conditions.
5. If a source is `placeholder_unknown`, forbid production-ready, low-overhead, battery-safe, flash-safe, or thermally-safe claims.
6. Check that the budget source supports the claim level.
7. Hand off calibrated budgets to `embedded-nfr-design`, `embedded-nfr-harness-design`, and `embedded-nfr-gate`.

## Outputs

Produce or update:

- `requirements/nfr/<feature>.yaml`
- `docs/nfr/<feature>.md`
- `reports/nfr-calibration/<feature>.md`

## Budget Sources

Allowed source values:

- `measured`
- `calibrated_from_target_baseline`
- `inferred_from_operating_envelope`
- `user_mandated`
- `standard_or_platform_guidance`
- `placeholder_unknown`

## Rules

- No production budget without provenance.
- `placeholder_unknown` blocks production-ready claims.
- Host fallback is not target proof.
- `standard_or_platform_guidance` alone does not support target-validated or production-ready resource-safety claims.
- `production-ready` requires measured or target-baseline-calibrated sources plus relevant operating-envelope evidence.
- Revisit budgets when target class, workload profile, power mode, or measurement method changes.
