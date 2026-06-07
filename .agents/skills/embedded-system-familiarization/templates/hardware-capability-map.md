# Hardware Capability Map: <target>

Purpose: map hardware capabilities to software levers and constraints.

## Compute

| Capability | Available? | Software lever | Measurement | Constraints |
| --- | --- | --- | --- | --- |
| CPU cores |  | thread placement / affinity |  |  |
| CPU governor |  | frequency policy |  |  |
| GPU |  | offload / batching |  |  |
| NPU/DSP |  | inference offload |  |  |
| SIMD |  | vectorization |  |  |

## Memory

| Capability | Available? | Software lever | Measurement | Constraints |
| --- | --- | --- | --- | --- |
| RAM headroom |  | buffer sizing |  |  |
| cache behavior |  | data layout |  |  |
| memory bandwidth |  | batching / zero-copy |  |  |

## I/O and Storage

| Capability | Available? | Software lever | Measurement | Constraints |
| --- | --- | --- | --- | --- |
| flash/eMMC/SD |  | write coalescing |  |  |
| bus bandwidth |  | batching / rate limit |  |  |
| network/radio |  | duty-cycle / upload policy |  |  |

## Power and Thermal

| Capability | Available? | Software lever | Measurement | Constraints |
| --- | --- | --- | --- | --- |
| battery state |  | degrade policy |  |  |
| thermal zones |  | duty cycle |  |  |
| throttling indicators |  | trigger / coverage |  |  |

## Evidence Gaps

- Missing capability:
- Missing measurement surface:
- Claim or architecture decision blocked:
