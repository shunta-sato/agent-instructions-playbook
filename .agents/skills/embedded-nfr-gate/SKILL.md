---
name: embedded-nfr-gate
description: "Use before final submit readiness when embedded NFR design or harness work was triggered, to decide submit/no-submit from physical budgets, measurements, unknowns, and claims. Do not use as a generic quality gate."
metadata:
  short-description: Embedded NFR submit gate
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
- `embedded-project-constitution`

Use it also when a PR contains target-local runtime behavior plus claims such as "low overhead", "battery safe", "lightweight", "flash safe", or "production ready".

Do not use this skill for non-embedded final readiness; use `quality-gate`.

## How to use

1. Gather required artifacts:
   - NFR matrix
   - physical budget file
   - target profile or explicit missing-target reason
   - resource harness plan or explicit no-measurement reason
   - resource report when measurement is claimed
   - hot-path report when loop/polling/sampling risk exists
   - observer-effect report when instrumentation can perturb workload
2. Compare measurements against budgets.
3. Search changed docs/user-visible text for resource claims and verify evidence supports each claim.
4. Apply hard rules:
   - no-measurement-no-claim
   - battery_unknown is not AC
   - default mode over budget blocks submit
   - unbounded wakeups block submit
   - continuous default disk writes need budget and flash-wear evidence
   - high-frequency default polling needs budget, measurement, and justification
5. Decide:
   - `submit`: budgets pass and claims are measured or limited
   - `no-submit`: budget exceeded, artifact missing, or unsupported claim remains
   - `experimental-only`: production claims removed and unknowns are explicit
6. Write `reports/resource/nfr-gate-report.md` using `templates/nfr-gate-report.md`.
7. Hand off the report path to `quality-gate`.

## Outputs

Produce:

- `reports/resource/nfr-gate-report.md`

## Gotchas

- **Common pitfall:** approving because functional tests pass.
  **Instead:** block when physical budgets or required evidence are missing.
- **Common pitfall:** treating unknown as pass.
  **Instead:** choose `no-submit` or `experimental-only`.
- **Common pitfall:** leaving marketing or README claims broader than measurements.
  **Instead:** remove the claim or restrict it to the measured target/profile.
