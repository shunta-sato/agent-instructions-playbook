# Resource Harness Plan: <feature>

## Inputs

- NFR matrix:
- Physical budget file:
- Target profile:
- Feature entry point:
- Build artifact:

## Scenarios

| Scenario | Purpose | Duration | Command | Report path | Pass rule |
| --- | --- | ---: | --- | --- | --- |
| idle_baseline | capture target idle resource use |  |  |  |  |
| default_steady_state | prove default production footprint |  |  |  |  |
| bounded_burst | prove burst remains bounded |  |  |  |  |
| degraded_battery_low | prove battery_low behavior |  |  |  |  |
| degraded_storage_pressure | prove writes stop or rotate safely |  |  |  |  |
| observer_off | compare without target-local observer |  |  |  |  |
| observer_on | compare observer overhead |  |  |  |  |

## Commands

- Target smoke:
  ```sh
  <target command>
  ```
- Host fallback:
  ```sh
  <host command>
  ```
- Baseline capture:
  ```sh
  <baseline command>
  ```

## Evidence Limits

- Target evidence missing:
- Host fallback cannot prove:
- Hardware counters unavailable:
- Manual measurement required:

## Report Paths

- Baseline:
- Scenario reports:
- Gate report:
