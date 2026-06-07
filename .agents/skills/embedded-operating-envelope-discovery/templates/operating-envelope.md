# Operating Envelope: <target>/<feature>

## Purpose

Identify normal, near-boundary, degraded, recovery, and blackout behavior.

## Preconditions

- Target characterization:
- Safe discovery boundary:
- Abort conditions:
- Do-not-probe:

## Scenarios

| Scenario | Workload | Duration | Expected behavior | Safety limit | Report |
| --- | --- | ---: | --- | --- | --- |
| idle |  |  |  |  |  |
| nominal |  |  |  |  |  |
| peak |  |  |  |  |  |
| near_boundary |  |  |  |  |  |
| degraded |  |  |  |  |  |
| observer_off |  |  |  |  |  |
| observer_on |  |  |  |  |  |
| recovery |  |  |  |  |  |
| blackout_or_telemetry_loss |  |  |  |  |  |

## Findings

- Normal range:
- Near-boundary indicators:
- Degradation signals:
- Boundary findings:
  - Signal:
  - Boundary type:
  - Threshold:
  - Unit:
  - Confidence:
  - Evidence:
- Telemetry blackout:
  - Observed:
  - Signal ID:
  - Last seen time:
  - Expected cadence ms:
  - Confidence:
- Observer effect:
- No-go boundary:
- Safe experimental limits:
- Abort conditions observed:

## Budget Calibration Inputs

- CPU headroom:
- Wakeup headroom:
- Memory headroom:
- Storage write headroom:
- Thermal headroom:
- Battery evidence:

## Handoff

- nfr-calibration:
- nfr-design:
- nfr-gate:
