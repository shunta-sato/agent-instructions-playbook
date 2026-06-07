# Resource Discipline

## Required Feature Artifacts

Embedded-facing features provide:

- NFR matrix
- physical budget file
- target profile
- resource harness plan
- gate report before final submit readiness

## Review Routes

- Feature physical budget: `embedded-nfr-design`
- Measurement harness: `embedded-nfr-harness-design`
- Hot path loop/polling/sampling review: `embedded-hot-path-review`
- Observer effect review: `embedded-observer-effect-review`
- Final embedded NFR decision: `embedded-nfr-gate`

## Default Blockers

- Unsupported low-overhead, battery-safe, or production-ready claim
- Missing sampling/polling cadence budget for target-local default behavior
- Default mode over CPU, wakeup, memory, write, or thermal budget
- Measurement unknown treated as pass
- Host fallback treated as target proof
- Continuous default storage write with no flash-wear estimate
- Battery unknown treated as AC power
- Missing degraded-mode behavior for relevant pressure states
