# Embedded NFR Matrix: <feature>

## Target-Class Assumptions

- Target class:
- Power state:
- Deployment mode:
- Default mode:
- Burst mode:
- Degraded modes:
- Measurement surfaces available:
- Measurement surfaces unavailable:

## NFR Matrix

| NFR | Default budget | Burst budget | Measurement | Merge rule | Status |
| --- | ---: | ---: | --- | --- | --- |
| Polling / sampling cadence | >=1000ms or <=1Hz | bounded by trigger/duration | <tool/report> | sub-100ms default cadence blocks submit unless explicitly allowed, measured, and justified | unknown |
| CPU | <target> | <target for duration> | <tool/report> | default over budget blocks submit | unknown |
| Wakeups | <target> | <target for duration> | <tool/report> | unbounded wakeups block submit | unknown |
| RSS / heap | <target> | <target> | <tool/report> | unbounded growth blocks submit | unknown |
| Hot-path allocation | <target> | <target> | <tool/report> | per-sample allocation needs justification | unknown |
| Storage writes | <target> | <target> | <tool/report> | continuous writes need budget and wear estimate | unknown |
| Flash wear | <target> | <target> | <estimate/report> | missing wear estimate blocks production-ready claim | unknown |
| Battery | <target> | <target> | <tool/report> | battery_unknown is not AC | unknown |
| Network/radio | <target> | <target> | <tool/report> | hidden background radio use blocks battery-safe claim | unknown |
| Thermal | <target> | <target> | <tool/report> | feature-caused thermal rise needs degraded mode | unknown |
| Latency / jitter | <target> | <target> | <tool/report> | missed timing budget blocks submit | unknown |
| Observer overhead | <target> | <target> | <tool/report> | unmeasured observer overhead limits claims | unknown |

## Runtime Mode Classification

| Behavior | Mode | Cadence | Duration bound | Enabled by default? | Required evidence |
| --- | --- | ---: | ---: | --- | --- |
| target-local background behavior | default/burst/experimental-only/debug-only |  |  |  |  |

## Steady-State vs Burst Classification

- Steady-state behavior:
- Burst behavior:
- Burst trigger:
- Burst duration bound:
- Default-mode safeguards:

## Degraded-Mode Policy

| Condition | Required behavior | Evidence |
| --- | --- | --- |
| battery_low |  |  |
| memory_pressure |  |  |
| thermal_pressure |  |  |
| storage_pressure |  |  |
| measurement_unavailable |  |  |

## Measurement Plan

- Target smoke command:
- Host fallback:
- Baseline:
- Report path:
- Missing evidence:

## No-Measurement-No-Claim List

Claims not allowed until measured:

-
