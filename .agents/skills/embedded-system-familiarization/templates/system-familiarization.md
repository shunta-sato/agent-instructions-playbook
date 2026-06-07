# Embedded System Familiarization: <target>/<feature>

## 1. Goal

- System to understand:
- Software decision depending on this understanding:
- Work type: new target|new workload|new runtime|optimization|architecture decision
- Production/resource-safety claims requested:

## 2. Artifact Status

| Artifact | Status | Path | Required? | Missing/provisional/deferred reason |
| --- | --- | --- | --- | --- |
| target characterization | current|stale|missing|provisional|deferred |  |  |  |
| operating envelope | current|stale|missing|provisional|deferred |  |  |  |
| calibrated NFRs | current|stale|missing|provisional|deferred |  |  |  |
| hardware capability map | current|stale|missing|provisional|deferred |  |  |  |
| workload map | current|stale|missing|provisional|deferred |  |  |  |
| bottleneck/margin map | current|stale|missing|provisional|deferred |  |  |  |
| architecture constraints | current|stale|missing|provisional|deferred |  |  |  |
| NFR gate report | current|stale|missing|provisional|deferred |  |  |  |

## 3. Target Identity

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

## 4. Workload Map

| Workload | Description | Normal? | Peak? | Boundary? | Risk | Report |
| --- | --- | --- | --- | --- | --- | --- |
| idle |  |  |  |  |  |  |
| nominal |  |  |  |  |  |  |
| peak |  |  |  |  |  |  |
| degraded |  |  |  |  |  |  |
| recovery |  |  |  |  |  |  |

## 5. Hardware Capability Map

| Capability | Available? | Measurement surface | Software lever | Risk | Evidence |
| --- | --- | --- | --- | --- | --- |
| CPU frequency scaling |  |  |  |  |  |
| thermal zones |  |  |  |  |  |
| battery state |  |  |  |  |  |
| storage write budget |  |  |  |  |  |
| accelerator/NPU/GPU |  |  |  |  |  |
| scheduler / real-time |  |  |  |  |  |
| hardware counters |  |  |  |  |  |

## 6. Operating Envelope Summary

- Normal range:
- Near-boundary indicators:
- Degradation signals:
- Telemetry/logging blackout:
- Recovery behavior:
- No-go boundary:
- Observer effect:

## 7. Bottleneck and Margin Map

| Resource | Current baseline | Near-boundary | Margin | Dominant risk | Evidence |
| --- | ---: | ---: | ---: | --- | --- |
| CPU |  |  |  |  |  |
| memory |  |  |  |  |  |
| wakeups |  |  |  |  |  |
| flash writes |  |  |  |  |  |
| battery |  |  |  |  |  |
| thermal |  |  |  |  |  |
| latency/jitter |  |  |  |  |  |

## 8. NFR Calibration Inputs

- CPU budget source:
- memory budget source:
- wakeup budget source:
- battery budget source:
- flash budget source:
- thermal budget source:
- latency/jitter budget source:

## 9. Architecture Constraints

- Must:
- Must not:
- Should:
- Allowed only in burst mode:
- Experimental only:
- Deferred until measured:

## 10. Claims Blocked By Missing Evidence

| Claim | Missing evidence | Allowed wording/status |
| --- | --- | --- |
| hardware-efficient |  | blocked|experimental-only|target-specific |
| low-overhead |  | blocked|experimental-only|target-specific |
| battery-safe |  | blocked|experimental-only|target-specific |
| flash-safe |  | blocked|experimental-only|target-specific |
| thermally-safe |  | blocked|experimental-only|target-specific |
| production-ready |  | blocked|experimental-only|target-specific |

## 11. Handoffs

- embedded-project-constitution:
- embedded-target-characterization:
- embedded-operating-envelope-discovery:
- embedded-nfr-calibration:
- embedded-nfr-design:
- architecture-decision-analysis:
- embedded-nfr-harness-design:
- embedded-hot-path-review:
- embedded-observer-effect-review:
- embedded-nfr-gate:
- quality-gate:
