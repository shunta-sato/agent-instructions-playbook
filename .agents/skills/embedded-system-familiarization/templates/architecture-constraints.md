# Architecture Constraints: <target>/<feature>

Purpose: turn familiarization findings into design constraints.

## Hard Constraints

- No default polling below:
- No continuous flash write:
- Max steady CPU:
- Max RSS:
- Battery mode behavior:
- Thermal mode behavior:
- Observer mode behavior:

## Design Implications

| Source finding | Constraint | Affected component | Verification |
| --- | --- | --- | --- |
|  |  |  |  |

## Allowed Patterns

- event-driven
- piggyback existing cadence
- bounded burst
- memory ring
- coalesced writes
- off-target analysis
- explicit experimental mode

## Forbidden / Requires Approval

- always-on high-frequency polling
- recursive scan in hot path
- per-sample JSON serialization
- unbounded queues
- continuous target-local upload
- observer-enabled-by-default without observer-off comparison

## Handoff to Architecture Decision

- Candidate options:
- Quality drivers:
- NFR constraints:
- Verification tasks:
