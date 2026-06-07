# Embedded System Familiarization: <target>/<feature>

## 1. Goal

- System to understand:
- Software decision depending on this understanding:
- Work type: new target|new workload|new runtime|optimization|architecture decision
- Production/resource-safety claims requested:

## 2. Artifact Status

| Artifact | Status | Path | Required? | Freshness / revisit condition | Missing/provisional/deferred reason |
| --- | --- | --- | --- | --- | --- |
| target characterization | current|stale|missing|provisional|deferred |  |  |  |  |
| operating envelope | current|stale|missing|provisional|deferred |  |  |  |  |
| calibrated NFRs | current|stale|missing|provisional|deferred |  |  |  |  |
| hardware capability map | current|stale|missing|provisional|deferred |  |  |  |  |
| workload map | current|stale|missing|provisional|deferred |  |  |  |  |
| bottleneck/margin map | current|stale|missing|provisional|deferred |  |  |  |  |
| architecture constraints | current|stale|missing|provisional|deferred |  |  |  |  |
| NFR gate report | current|stale|missing|provisional|deferred |  |  |  |  |

## 3. Artifact Freshness

- Target characterization current because:
- Operating envelope current because:
- Calibrated NFRs current because:
- Hardware capability map current because:
- Workload map current because:
- Bottleneck/margin map current because:
- Architecture constraints current because:
- Revisit when target hardware changes:
- Revisit when OS/kernel/runtime changes:
- Revisit when workload profile changes:
- Revisit when power mode changes:
- Revisit when measurement method changes:

## 4. Target Identity

- Target class:
- Hardware:
- CPU / cores / governors:
- Memory:
- Storage:
- Power source:
- Thermal surfaces:
- OS/runtime:
- Kernel/driver constraints:
- Accelerator / GPU / NPU / DSP:
- I/O buses:
- Real-time constraints:

## 5. Workload Map

| Workload | Description | Normal? | Peak? | Boundary? | Risk | Report |
| --- | --- | --- | --- | --- | --- | --- |
| idle |  |  |  |  |  |  |
| nominal |  |  |  |  |  |  |
| peak |  |  |  |  |  |  |
| degraded |  |  |  |  |  |  |
| recovery |  |  |  |  |  |  |

## 6. Hardware Capability Map

| Capability | Available? | Measurement surface | Software lever | Risk | Architecture implication | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| CPU frequency scaling |  |  |  |  |  |  |
| thermal zones |  |  |  |  |  |  |
| battery state |  |  |  |  |  |  |
| storage write budget |  |  |  |  |  |  |
| accelerator/NPU/GPU |  |  |  |  |  |  |
| scheduler / real-time |  |  |  |  |  |  |
| hardware counters |  |  |  |  |  |  |

## 7. Operating Envelope Summary

- Normal range:
- Near-boundary indicators:
- Degradation signals:
- Telemetry/logging blackout:
- Recovery behavior:
- No-go boundary:
- Observer effect:

## 8. Bottleneck and Margin Map

| Resource | Current baseline | Near-boundary | Margin | Dominant risk | Evidence |
| --- | ---: | ---: | ---: | --- | --- |
| CPU |  |  |  |  |  |
| memory |  |  |  |  |  |
| wakeups |  |  |  |  |  |
| flash writes |  |  |  |  |  |
| battery |  |  |  |  |  |
| thermal |  |  |  |  |  |
| latency/jitter |  |  |  |  |  |

## 9. NFR Calibration Inputs

- CPU budget source:
- memory budget source:
- wakeup budget source:
- battery budget source:
- flash budget source:
- thermal budget source:
- latency/jitter budget source:

## 10. Architecture Constraints

- Must:
- Must not:
- Should:
- Allowed only in burst mode:
- Experimental only:
- Deferred until measured:

## 11. Claims Blocked By Missing Evidence

| Claim | Missing evidence | Allowed wording/status |
| --- | --- | --- |
| hardware-efficient |  | blocked|experimental-only|target-specific |
| low-overhead |  | blocked|experimental-only|target-specific |
| battery-safe |  | blocked|experimental-only|target-specific |
| flash-safe |  | blocked|experimental-only|target-specific |
| thermally-safe |  | blocked|experimental-only|target-specific |
| production-ready |  | blocked|experimental-only|target-specific |

## 12. Handoffs

| Handoff | Status | Required? | Evidence path | Blocker? | Notes |
| --- | --- | --- | --- | --- | --- |
| embedded-project-constitution | not_needed|required_pending|completed|deferred_with_reason|blocked | yes|no |  | yes|no |  |
| embedded-target-characterization | not_needed|required_pending|completed|deferred_with_reason|blocked | yes|no |  | yes|no |  |
| embedded-operating-envelope-discovery | not_needed|required_pending|completed|deferred_with_reason|blocked | yes|no |  | yes|no |  |
| embedded-nfr-calibration | not_needed|required_pending|completed|deferred_with_reason|blocked | yes|no |  | yes|no |  |
| embedded-nfr-design | not_needed|required_pending|completed|deferred_with_reason|blocked | yes|no |  | yes|no |  |
| architecture-decision-analysis | not_needed|required_pending|completed|deferred_with_reason|blocked | yes|no |  | yes|no |  |
| embedded-nfr-harness-design | not_needed|required_pending|completed|deferred_with_reason|blocked | yes|no |  | yes|no |  |
| embedded-hot-path-review | not_needed|required_pending|completed|deferred_with_reason|blocked | yes|no |  | yes|no |  |
| embedded-observer-effect-review | not_needed|required_pending|completed|deferred_with_reason|blocked | yes|no |  | yes|no |  |
| embedded-nfr-gate | not_needed|required_pending|completed|deferred_with_reason|blocked | yes|no |  | yes|no |  |
| quality-gate | not_needed|required_pending|completed|deferred_with_reason|blocked | yes|no |  | yes|no |  |
