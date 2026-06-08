# Capability Cost Model: <target>/<capability>

Purpose: prevent architecture decisions from treating hardware presence as capability proof. Record the control surface, API, workload fit, transfer/setup cost, power/thermal cost, and evidence needed before claiming a hardware path is better.

## 1. Capability Summary

- Capability:
- Candidate architecture decision:
- Workloads considered:
- Control surface map:
- Controlled operating points:
- Experiment design matrix:
- Benchmark / report paths:
- Current decision status: blocked|provisional|target-specific|ready-for-architecture-decision

## 2. Control Surface And API

| Item | Status | Evidence | Architecture implication |
| --- | --- | --- | --- |
| Hardware present | yes|no|unknown |  |  |
| Driver/runtime/API available | yes|no|unknown |  |  |
| Control surface known? | yes|no|unknown|provisional |  |  |
| Cost model known? | yes|no|unknown|provisional |  |  |
| Safe enable/disable method | yes|no|unknown|not_supported |  |  |
| Workload can be routed to capability | yes|no|unknown|provisional |  |  |
| Fallback path exists | yes|no|unknown |  |  |

## 3. Cost Model

| Cost component | Unit | Measurement method | Value / range | Evidence path | Confidence | Claim impact |
| --- | --- | --- | --- | --- | --- | --- |
| Setup / initialization |  |  |  |  | none|low|medium|high |  |
| Data transfer in |  |  |  |  | none|low|medium|high |  |
| Data transfer out |  |  |  |  | none|low|medium|high |  |
| Scheduling / queueing |  |  |  |  | none|low|medium|high |  |
| Synchronization / copy overhead |  |  |  |  | none|low|medium|high |  |
| CPU load displaced |  |  |  |  | none|low|medium|high |  |
| Power cost |  |  |  |  | none|low|medium|high |  |
| Thermal cost |  |  |  |  | none|low|medium|high |  |
| Memory pressure |  |  |  |  | none|low|medium|high |  |
| Contention with other workloads |  |  |  |  | none|low|medium|high |  |

## 4. Workload Fit / Break-Even

| Workload | Input size / rate | Latency budget | CPU-only baseline | Capability path result | Break-even point | Power/thermal effect | Evidence path | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  |  | blocked|provisional|target-specific|preferred|rejected |

## 5. Claim-To-Evidence Trace

| Claim | Required evidence | Actual evidence | Missing cost/control evidence | Confidence | Allowed wording | Blocked wording / status |
| --- | --- | --- | --- | --- | --- | --- |
| GPU offload is better | API/control surface, transfer cost, workload fit, power/thermal cost, controlled benchmark |  |  | none|low|medium|high |  | blocked|provisional|target-specific |
| reduces CPU load safely | CPU displacement, scheduling overhead, power/thermal impact, fallback behavior |  |  | none|low|medium|high |  | blocked|provisional|target-specific |
| lower battery impact | power measurement under controlled operating points and workload levels |  |  | none|low|medium|high |  | blocked|provisional|target-specific |

## 6. Architecture Evidence Packet

Use this summary when handing off to `architecture-decision-analysis`.

| Packet field | Value |
| --- | --- |
| Decision question |  |
| Candidate options |  |
| Hardware/control surface status |  |
| Operating point coverage |  |
| Cost model status |  |
| Benchmark evidence |  |
| Power/thermal evidence |  |
| Workload fit / break-even |  |
| Known confounders |  |
| Provisional assumptions |  |
| Blocked claims |  |
| Allowed wording |  |
| Verification tasks for ADR |  |
