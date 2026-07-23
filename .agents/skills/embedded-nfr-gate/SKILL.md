---
name: embedded-nfr-gate
description: "Use before final submit readiness when embedded NFR design or harness work was triggered, to decide submit/no-submit from physical budgets, measurements, unknowns, and claims. Do not use as a generic quality gate."
metadata:
  short-description: Embedded NFR submit gate
  templates:
    - templates/nfr-gate-report.md
---

## Purpose

Use this skill to make a final embedded NFR decision before `quality-gate`.

It answers one question:

**Can this embedded-facing change be submitted with its current physical budgets, measurement evidence, and claims?**

## When to use

Use this skill when one of these skills was triggered:

- `embedded-nfr-design`
- `embedded-nfr-harness-design`
- `embedded-hot-path-review`
- `embedded-observer-effect-review`
- `embedded-project-constitution` plus feature-level embedded runtime changes or production-readiness claims

Use it also when a PR contains target-local runtime behavior plus claims such as "low overhead", "battery safe", "lightweight", "flash safe", or "production ready".

If only `embedded-project-constitution` was triggered and no feature implementation or production-readiness claim is being submitted, record `constitution-only: no feature gate required` and hand off constitution artifact checks to `quality-gate`.

Do not use this skill for non-embedded final readiness; use `quality-gate`.

Do not use for host-side CLIs, batch tools, servers, or ordinary daemons that have no physical target constraint. Work is embedded only when an actual constraint exists: battery/power budget, thermal limit, flash-wear limit, real-time deadline, constrained target CPU/RAM, or a physically separate target device. Logger/recorder/collector/sampler/polling vocabulary alone does not make work embedded; when in doubt and no physical constraint is named, treat the work as non-embedded and use the general skills (`$performance-review`, `$observability`).

## How to use

1. Gather required artifacts:
   - NFR matrix
   - physical budget file
   - target profile or explicit missing-target reason
   - resource harness plan or explicit no-measurement reason
   - resource report when measurement is claimed
   - target characterization when production claims depend on target behavior
   - calibration report when numeric production budgets are claimed
   - hot-path report when loop/polling/sampling risk exists
   - observer-effect report when instrumentation can perturb workload
2. Compare measurements against budgets.
3. Search changed docs/user-visible text for resource claims and verify evidence supports each claim.
4. Apply hard rules:
   - no-measurement-no-claim
   - battery_unknown is not AC
   - measurement unknown is not pass
   - host fallback is not target proof
   - any target-local background behavior without default, burst, experimental-only, or debug-only mode classification blocks submit
   - default mode over budget blocks submit
   - unbounded wakeups block submit
   - continuous default disk writes need budget and flash-wear evidence
   - high-frequency default polling needs budget, measurement, and justification
   - production budget source `placeholder_unknown` blocks submit unless feature is experimental-only
   - missing target characterization with production-ready claims blocks submit
   - host-only evidence for target battery-safe claims blocks submit
   - stale target characterization, changed workload/power mode/measurement method, or triggered `revisit_when` blocks production-ready claims until recalibrated
5. Decide:
   - `submit`: budgets pass and claims are measured or limited
   - `no-submit`: budget exceeded, artifact missing, or unsupported claim remains
   - `experimental-only`: production claims removed and unknowns are explicit
6. Write `reports/resource/nfr-gate-report.md` using `templates/nfr-gate-report.md`.
7. Hand off the report path to `quality-gate`.

## Output expectation

Produce:

- `reports/resource/nfr-gate-report.md`

## Budget Provenance

Check calibrated budget sources when numeric production budgets are claimed:

- `measured`
- `calibrated_from_target_baseline`
- `inferred_from_operating_envelope`
- `user_mandated`
- `standard_or_platform_guidance`
- `placeholder_unknown`

Treat `placeholder_unknown` as `no-submit` or `experimental-only`.

## Gotchas

- **Common pitfall:** approving because functional tests pass.
  **Instead:** block when physical budgets or required evidence are missing.
- **Common pitfall:** treating unknown as pass.
  **Instead:** choose `no-submit` or `experimental-only`.
- **Common pitfall:** leaving marketing or README claims broader than measurements.
  **Instead:** remove the claim or restrict it to the measured target/profile.
