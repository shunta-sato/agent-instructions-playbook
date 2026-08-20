# Flutter performance review guidance

Use this reference with `performance-review` when Flutter rendering, startup, memory, network, image/media handling, or a Dart/native boundary is on the user-visible or sustained hot path.

## Measurement rules

- Do not use debug-mode timing as release-performance evidence.
- Prefer profile or release-equivalent builds and record build mode, device, OS version, and workload.
- A web/desktop measurement does not prove Android/iOS performance when rendering, runtime, plugin, lifecycle, or native behavior is involved.
- When the requirement applies to both mobile platforms, measure both or record why one remains unmeasured; do not silently generalize one platform's result.
- Keep declared quality targets in the same `metric | target | measurement method | measured result` form used by `requirements-engineering`.

## Candidate metrics

Select only metrics that map to a requirement or risk:

- cold/warm startup and first useful frame
- user-action-to-visible-result latency
- frame build/raster duration, missed-frame/jank rate, and sustained frame rate
- CPU use during representative foreground/background work
- memory peak, steady state, growth/leak behavior, image/cache pressure
- allocation/copy/serialization cost for large payloads or per-frame work
- network request count, payload size, throughput, timeout/retry delay
- app/package size when it is a declared delivery constraint
- battery/thermal behavior for sustained media, sensor, location, or background workloads when required

Do not invent thresholds in this reference. Use project requirements or route to `requirements-engineering`.

## Flutter-specific red flags

Check when relevant:

- expensive synchronous work on the UI isolate
- unnecessary rebuild scope on a frequently changing tree
- repeated image decode/resize/copy on a frame-sensitive path
- unbounded lists/caches or retained objects across navigation/lifecycle transitions
- repeated JSON/serialization or allocation in hot callbacks
- chatty MethodChannel/EventChannel/Pigeon calls
- large binary buffers copied between Dart and native layers
- per-item/per-frame platform calls that could be batched or moved behind a coarser native operation
- serial network awaits on a latency-sensitive user action
- background or lifecycle assumptions that differ between Android and iOS

## Native boundary handoff

When the performance issue cannot be resolved without choosing among pure Dart, isolate, plugin/platform code, FFI/Native Assets, or backend processing, stop treating it as a local optimization and route to `architecture-decision-analysis` with `.agents/skills/architecture-decision-analysis/references/mobile-native-boundary.md`.

The architecture decision should state the data path, crossing frequency, copies/serialization, threading, lifecycle, and per-platform verification tasks. A plugin's existence alone is not performance evidence.

## Evidence sources

Prefer repository-defined tooling. Depending on the project, useful evidence may include:

- Flutter DevTools performance/CPU/memory/network views
- timeline or integration-test performance traces
- Android/iOS platform profilers for native/plugin work
- application metrics/traces for end-to-end latency
- controlled benchmark/test harnesses with fixed data and device state

Record exact commands or artifact paths only when confirmed by the repository/toolchain.

## Performance-review mapping

Add Flutter/mobile context to the normal Performance Review:

- Hot path: startup | render/frame | user operation | background | media/sensor | native bridge | network
- Platform scope: shared | Android | iOS | both-separately
- Build/device evidence: mode, device, OS, workload
- Boundary cost: calls, bytes, copies/serialization, thread/isolate transitions
- Decision: `improve-now | accept | accept-with-limit | needs-measurement`

A shared mobile performance claim is `needs-measurement` when required platform evidence is missing.
