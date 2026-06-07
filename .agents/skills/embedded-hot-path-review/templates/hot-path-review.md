# Embedded Hot-Path Review: <feature>

## Hot Path

- Entry point:
- Cadence or trigger:
- Default mode:
- Burst mode:
- Target class:

## Per-Iteration Cost

| Cost source | Present? | Evidence | Risk | Required change |
| --- | --- | --- | --- | --- |
| Allocation |  |  |  |  |
| Serialization/parsing |  |  |  |  |
| Filesystem / flash I/O |  |  |  |  |
| Directory scan |  |  |  |  |
| Network/radio use |  |  |  |  |
| Blocking syscall |  |  |  |  |
| Lock/queue operation |  |  |  |  |
| O(n) data-structure operation |  |  |  |  |

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
