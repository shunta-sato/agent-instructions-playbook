# Embedded Hot-Path Review: <feature>

## Hot Path

- Entry point:
- Cadence or trigger:
- Default mode:
- Burst mode:
- Target class:

## Per-Iteration Cost

| Cost source | Present? | Allowed budget | Evidence | Risk | Required change |
| --- | --- | --- | --- | --- | --- |
| Allocation |  | 0 per default steady-state iteration |  |  |  |
| Serialization/parsing |  | 0 per high-frequency default iteration unless measured |  |  |  |
| Filesystem / flash I/O |  | 0 continuous default writes unless budgeted |  |  |  |
| Directory scan |  | 0 per default iteration |  |  |  |
| Network/radio use |  | 0 hidden background use unless budgeted |  |  |  |
| Blocking syscall |  | 0 in sub-100ms loop unless justified |  |  |  |
| Lock/queue operation |  | bounded wait and bounded queue |  |  |  |
| O(n) data-structure operation |  | 0 per high-frequency iteration unless bounded |  |  |  |

## Cadence Decision

- Default cadence:
- Burst cadence:
- Why this cadence is needed:
- Event-driven or coalesced alternative:
- Measurement required:

## Findings

- [EHP-001] <location> - <risk> - <required fix>

## Handoff

- NFR budget impact:
- Harness scenario needed:
- Gate blocker:
