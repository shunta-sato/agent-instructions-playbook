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
| hardware control surface map | current|stale|missing|provisional|deferred |  |  |  |  |
| controlled operating points | current|stale|missing|provisional|deferred |  |  |  |  |
| experiment design matrix | current|stale|missing|provisional|deferred |  |  |  |  |
| capability cost model | current|stale|missing|provisional|deferred |  |  |  |  |
| workload map | current|stale|missing|provisional|deferred |  |  |  |  |
| bottleneck/margin map | current|stale|missing|provisional|deferred |  |  |  |  |
| architecture constraints | current|stale|missing|provisional|deferred |  |  |  |  |
| NFR gate report | current|stale|missing|provisional|deferred |  |  |  |  |

## 3. Artifact Freshness

- Target characterization current because:
- Operating envelope current because:
- Calibrated NFRs current because:
- Hardware capability map current because:
- Hardware control surface map current because:
- Controlled operating points current because:
- Experiment design matrix current because:
- Capability cost model current because:
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

| Capability | Available? | Measurement surface | Software lever | Risk | Control surface known? | Cost model known? | Architecture implication | Architecture claim boundary | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPU frequency scaling |  |  |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |  |
| thermal zones |  |  |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |  |
| battery state |  |  |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |  |
| storage write budget |  |  |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |  |
| accelerator/NPU/GPU |  |  |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |  |
| scheduler / real-time |  |  |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |  |
| hardware counters |  |  |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |  |

## 7. Operating Envelope Summary

- Normal range:
- Near-boundary indicators:
- Degradation signals:
- Telemetry/logging blackout:
- Recovery behavior:
- No-go boundary:
- Observer effect:

## 8. Controlled Conditions

| Condition | Role | Control status | Value(s) | Verification | Restore | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| CPU governor | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  |  |
| CPU frequency | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  |  |
| CPU core affinity | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  |  |
| Online CPU cores | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  |  |
| Thermal state | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  |  |
| Power mode | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  |  |
| Workload level | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  |  |

## 9. Uncontrolled Confounders

| Confounder | Affected claim / metric | Observed? | Why uncontrolled | Mitigation | Claim limitation |
| --- | --- | --- | --- | --- | --- |
|  |  | yes|no|partial |  |  |  |

## 10. Operating Point Coverage

| Factor | Coverage status | Evidence role | Values observed | Values controlled | Confidence | Evidence path | Allowed claim boundary |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CPU governor | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  | none|low|medium|high |  |  |
| CPU frequency | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  | none|low|medium|high |  |  |
| CPU core affinity | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  | none|low|medium|high |  |  |
| Online CPU cores | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  | none|low|medium|high |  |  |
| Thermal state | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  | none|low|medium|high |  |  |
| Power mode | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  | none|low|medium|high |  |  |
| Workload level | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  | none|low|medium|high |  |  |

## 11. Bottleneck and Margin Map

| Resource | Current baseline | Near-boundary | Margin | Dominant risk | Evidence |
| --- | ---: | ---: | ---: | --- | --- |
| CPU |  |  |  |  |  |
| memory |  |  |  |  |  |
| wakeups |  |  |  |  |  |
| flash writes |  |  |  |  |  |
| battery |  |  |  |  |  |
| thermal |  |  |  |  |  |
| latency/jitter |  |  |  |  |  |

## 12. NFR Calibration Inputs

- CPU budget source:
- memory budget source:
- wakeup budget source:
- battery budget source:
- flash budget source:
- thermal budget source:
- latency/jitter budget source:

## 13. Architecture Constraints

- Must:
- Must not:
- Should:
- Allowed only in burst mode:
- Experimental only:
- Deferred until measured:

## 14. Claim-To-Evidence Trace

| Claim | Claim type | Required evidence | Actual evidence | Operating point coverage | Confidence | Allowed wording | Blocked wording / status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| works at all CPU clocks | NFR|architecture|hardware | controlled frequency sweep across claimed range with governor, thermal, power, and workload conditions recorded |  | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | none|low|medium|high |  | blocked|provisional|target-specific |
| low overhead across frequency range | NFR|architecture|hardware | controlled operating points and observer-effect evidence for claimed range |  | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | none|low|medium|high |  | blocked|provisional|target-specific |
| battery-safe | NFR|architecture|hardware | controlled power/thermal/workload duration evidence and budget provenance |  | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | none|low|medium|high |  | blocked|provisional|target-specific |
| GPU offload is better | NFR|architecture|hardware | control surface, API, transfer cost, workload fit, power/thermal cost model, and benchmark evidence |  | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | none|low|medium|high |  | blocked|provisional|target-specific |

## 15. Claims Blocked By Missing Evidence

| Claim | Missing evidence | Allowed wording/status |
| --- | --- | --- |
| hardware-efficient |  | blocked|experimental-only|target-specific |
| low-overhead |  | blocked|experimental-only|target-specific |
| battery-safe |  | blocked|experimental-only|target-specific |
| flash-safe |  | blocked|experimental-only|target-specific |
| thermally-safe |  | blocked|experimental-only|target-specific |
| production-ready |  | blocked|experimental-only|target-specific |

## 16. Architecture Evidence Packet

Use this section when handing off hardware-dependent choices to `architecture-decision-analysis`.

| Packet field | Value |
| --- | --- |
| Decision question |  |
| Candidate options |  |
| Hardware/control surface status |  |
| Operating point coverage |  |
| Capability cost model status |  |
| Benchmark evidence |  |
| Power/thermal evidence |  |
| Known covariates |  |
| Uncontrolled confounders |  |
| Provisional assumptions |  |
| Blocked claims |  |
| Allowed wording |  |
| Verification tasks for ADR |  |

## 17. Handoffs

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
