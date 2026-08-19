# Mobile native boundary decision guidance

Use this reference with `architecture-decision-analysis` when a Flutter or other cross-platform mobile feature may need a native/plugin/FFI boundary. It is not a standalone skill and does not force native code merely because a platform API is involved.

## Trigger signals

Open this reference when two or more viable implementation boundaries exist and the choice affects measurable quality drivers. Typical signals include:

- camera/audio/video frame pipelines or other sustained media processing
- high-rate sensors or event streams
- large image/binary buffers crossing a language/runtime boundary
- explicit 30/60fps, frame-budget, or low-latency requirements
- Bluetooth, USB, NFC, special sensors, hardware codecs, or platform services
- vendor Android/iOS SDKs
- C/C++ libraries, Dart FFI, or Native Assets
- MethodChannel/EventChannel/Pigeon or custom/federated Flutter plugins
- background execution with materially different iOS/Android constraints
- repeated serialization/copying across a platform boundary

A package/plugin existing on pub.dev is evidence that an option exists, not proof that it meets the quality, maintenance, licensing, or platform requirements.

## Candidate boundaries

Compare only viable options. Common candidates are:

1. Pure Dart/shared implementation.
2. Dart isolate/shared worker for CPU isolation.
3. Existing maintained Flutter plugin.
4. Custom Flutter plugin or federated plugin with Kotlin/Swift implementation.
5. Pigeon/MethodChannel/EventChannel boundary.
6. Dart FFI / Native Assets to a native library.
7. Backend/off-device processing when latency, privacy, connectivity, and cost allow it.

Do not compare every option by default. Remove obviously invalid candidates before the architecture record.

## Quality drivers

Make the decision against measurable project requirements such as:

- end-to-end latency and jitter
- sustained throughput / frames per second
- number and size of boundary crossings
- copies and serialization bytes per operation/frame
- CPU and memory use on representative devices
- battery/thermal behavior for sustained work
- cancellation, lifecycle, background, and process-restart behavior
- Android/iOS feature parity and SDK capability
- testability and deterministic failure injection
- maintenance burden, upstream plugin health, licensing, and upgrade surface

If a performance target lacks metric, target, or measurement method, return to `requirements-engineering` before deciding.

## Boundary evidence

For each candidate, capture:

| Concern | Evidence |
|---|---|
| Data path | types, buffer sizes, crossing frequency |
| Copy/serialization | zero-copy, copied, encoded/decoded, unknown |
| Threading | UI/main thread, isolate, platform thread/executor, native threads |
| Lifecycle | foreground/background/suspend/process death behavior |
| Android | supported API/SDK path and constraints |
| iOS | supported API/SDK path and constraints |
| Failure contract | cancellation, timeout, disconnect, native exception mapping |
| Verification | benchmark/profile/device/integration test path |
| Maintenance | dependency/plugin/native API ownership and update burden |

## Decision rules

- Prefer the simplest boundary that satisfies measured requirements and platform behavior.
- Do not move code native solely for anticipated performance; require a target or measurement gap.
- Do not keep high-rate per-frame/per-sample traffic on a serialization-heavy boundary when measurement shows it consumes the budget.
- Prefer coarse-grained native operations over chatty platform calls when the native boundary is required.
- Keep the product capability contract above the implementation boundary so iOS and Android can legitimately use different native mechanisms.
- Keep a fallback/reversibility plan when adopting a third-party plugin or vendor SDK that becomes a critical boundary.
- If upstream Flutter/Dart FFI or Native Assets skills are enabled, use them after this decision to implement the chosen boundary; they do not replace the architecture decision.

## Verification tasks

At least one verification task should exercise the real boundary on representative target environments when the quality driver is platform-dependent. Web/desktop measurements do not prove Android/iOS native-boundary performance.

Useful evidence may include profile/release-mode traces, frame timelines, native profiler results, memory/copy measurements, integration tests, lifecycle/background tests, and fault injection around disconnection/cancellation.

Feed the chosen boundary, rejected options, assumptions, and verification tasks into the normal Architecture Decision Analysis Record.
