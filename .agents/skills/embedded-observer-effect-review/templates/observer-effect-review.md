# Embedded Observer-Effect Review: <feature>

## Observer

- Component:
- Cadence:
- Data captured:
- Storage path:
- Transmission path:
- Default/debug/experimental mode:

## Perturbation Review

| Vector | Risk | Evidence | Mitigation | Status |
| --- | --- | --- | --- | --- |
| Scheduler / wakeups |  |  |  | unknown |
| CPU / allocation |  |  |  | unknown |
| Storage writes / flash wear |  |  |  | unknown |
| Network/radio use |  |  |  | unknown |
| Thermal behavior |  |  |  | unknown |
| Lock contention / queue pressure |  |  |  | unknown |
| Timing / jitter |  |  |  | unknown |

## Observer-On vs Observer-Off

- Observer-off scenario:
- Observer-on scenario:
- Difference:
- What remains unmeasured:

## Default-Enable Decision

- Decision: enabled-by-default|debug-only|experimental-only|disabled
- Rationale:
- Required evidence before enabling by default:

## Findings

- [EOE-001] <location> - <risk> - <required fix>

## Handoff

- Harness scenario needed:
- NFR gate blocker:
