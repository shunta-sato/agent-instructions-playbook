# NFR Calibration: <feature>

## Inputs

- Target characterization:
- Operating envelope:
- User-mandated constraints:
- Platform guidance:

## Calibrated Budgets

| NFR | Value | Source | Evidence | Confidence | Revisit when |
| --- | ---: | --- | --- | --- | --- |
| CPU |  |  |  |  |  |
| Wakeups |  |  |  |  |  |
| Memory |  |  |  |  |  |
| Disk writes |  |  |  |  |  |
| Flash wear |  |  |  |  |  |
| Network background bytes |  |  |  |  |  |
| Battery |  |  |  |  |  |
| Thermal |  |  |  |  |  |
| Latency/jitter |  |  |  |  |  |
| Observer overhead |  |  |  |  |  |
| Polling/sampling cadence |  |  |  |  |  |
| Burst duration/cadence |  |  |  |  |  |

## Claim Level

| Claim level | Required budget source |
| --- | --- |
| experimental | `placeholder_unknown` allowed only when production claims are removed |
| development | host fallback or platform guidance allowed when marked non-production |
| target-validated | `measured`, `calibrated_from_target_baseline`, or `inferred_from_operating_envelope` |
| production-ready | `measured` or `calibrated_from_target_baseline` plus relevant operating-envelope evidence |

## Unknowns

- Unknown:
- Production claim impact:

## Handoff

- embedded-nfr-design:
- embedded-nfr-harness-design:
- embedded-nfr-gate:
