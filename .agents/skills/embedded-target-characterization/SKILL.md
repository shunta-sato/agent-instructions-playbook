---
name: embedded-target-characterization
description: "Use before embedded NFR budgeting when the target system, workload, measurement surfaces, resource headroom, or normal operating baseline are not yet characterized. Do not use for generic implementation work with known target budgets."
metadata:
  short-description: Embedded target characterization
  requires:
    - templates/target-characterization-report.schema.json
    - templates/target-characterization.md
---

## Purpose

Use this skill to learn the real embedded, edge, or target-local system before setting production NFR budgets.

It answers one question:

**What target facts, baselines, measurement surfaces, unavailable signals, and safety constraints must budget work rely on?**

## When to use

Use this skill when:

- starting NFR work for a real embedded, edge, robot-local, Android, ROS 2, kernel, driver, sensor, logger, recorder, or target daemon system
- `target_profiles/<target>.yaml` is missing, placeholder-heavy, stale, or copied from a template
- normal workload baseline, resource headroom, or measurement surfaces are unknown
- budget values are being guessed
- `embedded-project-constitution` exists but target-specific evidence is missing

Do not use it for pure docs/schema work, generic cloud/backend NFRs, or target work whose current characterization and baselines already exist.

For broader target-learning efforts that also need hardware capability mapping, workload mapping, bottleneck/margin analysis, and architecture constraints, use `embedded-system-familiarization` first.

Do not use for host-side CLIs, batch tools, servers, or ordinary daemons that have no physical target constraint. Work is embedded only when an actual constraint exists: battery/power budget, thermal limit, flash-wear limit, real-time deadline, constrained target CPU/RAM, or a physically separate target device. Logger/recorder/collector/sampler/polling vocabulary alone does not make work embedded; when in doubt and no physical constraint is named, treat the work as non-embedded and use the general skills (`$performance-review`, `$observability`).

## How to use

1. Identify the target and safe discovery boundary.
2. Fill `templates/target-characterization.md`.
3. Create or update `target_profiles/<target>.yaml`.
4. Capture baseline report paths for idle and nominal workload.
5. Record known unavailable signals and do-not-probe constraints.
6. Write machine-readable summary data using `templates/target-characterization-report.schema.json` when a JSON report is useful.
7. Hand off:
   - `embedded-operating-envelope-discovery` when normal/degraded/failure boundaries are unknown
   - `embedded-nfr-calibration` when budgets must be derived from target evidence
   - `embedded-nfr-design` once target context is known or explicitly provisional

## Output expectation

Produce or update:

- `docs/targets/<target>/target-characterization.md`
- `target_profiles/<target>.yaml`
- `baselines/resource/<target>/idle.json`
- `baselines/resource/<target>/nominal_workload.json`
- `reports/target-characterization/<target>.json`

## Rules

- Characterization can record unknowns, but unknown is not pass.
- Host fallback is not target proof.
- Do not probe unsafe workloads just to fill a template.
- Budgets derived without characterization must remain provisional or unknown.
