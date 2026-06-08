# Hardware Capability Map: <target>

Purpose: map hardware capabilities to software levers, control surfaces, cost models, and architecture claim boundaries.

## Compute

| Capability | Available? | Software lever | Measurement | Constraints | Control surface known? | Cost model known? | Architecture implication | Architecture claim boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPU cores |  | thread placement / affinity |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |
| CPU governor |  | frequency policy |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |
| GPU |  | offload / batching |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |
| NPU/DSP |  | inference offload |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |
| SIMD |  | vectorization |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |

## Memory

| Capability | Available? | Software lever | Measurement | Constraints | Control surface known? | Cost model known? | Architecture implication | Architecture claim boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RAM headroom |  | buffer sizing |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |
| cache behavior |  | data layout |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |
| memory bandwidth |  | batching / zero-copy |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |

## I/O and Storage

| Capability | Available? | Software lever | Measurement | Constraints | Control surface known? | Cost model known? | Architecture implication | Architecture claim boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| flash/eMMC/SD |  | write coalescing |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |
| bus bandwidth |  | batching / rate limit |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |
| network/radio |  | duty-cycle / upload policy |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |

## Power and Thermal

| Capability | Available? | Software lever | Measurement | Constraints | Control surface known? | Cost model known? | Architecture implication | Architecture claim boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| battery state |  | degrade policy |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |
| thermal zones |  | duty cycle |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |
| throttling indicators |  | trigger / coverage |  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  |

## Evidence Gaps

- Missing capability:
- Missing measurement surface:
- Unknown control surface:
- Unknown cost model:
- Claim or architecture decision blocked:

## Architecture Claim Boundaries

| Claim or decision | Required capability | Control surface known? | Cost model known? | Evidence path | Allowed wording | Blocked wording / status |
| --- | --- | --- | --- | --- | --- | --- |
|  |  | yes|no|unknown|provisional | yes|no|unknown|provisional |  |  | blocked|provisional|target-specific |
