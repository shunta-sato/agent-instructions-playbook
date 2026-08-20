# Flutter mobile verification matrix

Use this reference with `quality-gate` when a Flutter/mobile change claims iOS/Android capability, platform-boundary behavior, or mobile quality targets.

This reference adds platform evidence requirements; it does not replace repository canonical commands or the normal quality gate.

## Evidence layers

Select the smallest set that proves the changed behavior.

| Layer | Typical evidence | What it can prove |
|---|---|---|
| Dart unit | repository/domain/service tests | platform-independent logic and failure contracts |
| Flutter widget | widget tests | shared widget/state interaction without real platform services |
| Golden/visual | deterministic screenshot/snapshot workflow | intended visual rendering for the scoped configuration |
| Integration | `integration_test` or repository equivalent | application flows against real Flutter runtime/services |
| Android target | emulator or physical device | Android lifecycle, permission, plugin/native, deep link, background behavior |
| iOS target | simulator or physical device on macOS/Xcode path | iOS lifecycle, permission, plugin/native, deep link, background behavior |
| Backend/contract | consumer/contract/integration tests | API/error/schema/auth compatibility |

Web preview is useful for fast UI iteration but is not evidence for Android/iOS platform boundaries.

## Platform-boundary triggers

Require target-specific evidence when the change touches or depends on:

- camera, microphone, photos, location, Bluetooth, NFC, USB, sensors
- permission grant/deny/revoke flows
- deep links, Universal Links, Android App Links
- secure storage / Keychain / Keystore
- notifications and push registration/handling
- background execution, suspend/resume, process death/restart
- platform channels, Pigeon, custom/federated plugins, FFI/Native Assets
- vendor mobile SDKs
- file sharing/pickers or OS-provided UI
- platform accessibility behavior
- signing/package/store metadata when part of the delivery claim

A shared unit/widget test is insufficient for these surfaces unless the target-specific behavior is explicitly out of scope.

## Failure/recovery scenarios

Add only those relevant to the requirement:

- network unavailable before action
- disconnect during mutation/upload/download
- timeout and retry
- duplicate/repeated action and idempotency
- cancellation
- app backgrounded/suspended during work
- process killed and relaunched
- permission denied/revoked
- stale/offline cache and reconnect
- incompatible backend/client version

For a cross-platform capability, align scenario IDs with `mobile-feature-parity` so each required scenario has iOS and Android evidence or an approved platform deviation.

## Dart/Flutter MCP use

MCP-driven widget inspection, screenshots, tap/text/scroll, and hot reload can accelerate investigation and exploratory validation. Treat them as durable completion evidence only when the project explicitly accepts that evidence or the interaction has been converted into a reproducible test/manual procedure.

- Do not let MCP screenshots/logs expose production customer data or credentials.
- Prefer test/staging accounts and endpoints.
- Record the target device/simulator and build mode.
- MCP roots do not prove filesystem isolation.

## Matrix

For a mobile cross-platform change, attach or summarize a matrix like:

| Requirement/scenario | Shared test | Android evidence | iOS evidence | Result / deviation |
|---|---|---|---|---|
| `<ID>` | `<test/none>` | `<command/device/artifact>` | `<command/device/artifact>` | `pass/fail/unknown/deviation` |

Rules:

- `unknown` on a required platform blocks submit when the change claims that platform is complete.
- An unavailable local iOS host does not waive iOS evidence; route to a macOS CI/worker or report the claim as blocked.
- A failed or skipped target-specific check cannot be replaced by a web/desktop pass.
- Platform deviation must preserve shared semantics and be recorded through `mobile-feature-parity` when that skill is triggered.

## Gate handoff

Before `submit`, confirm:

- canonical verification is green at the required risk depth
- every triggered platform boundary has the required target evidence
- declared mobile quality targets are measured or explicitly block the gate
- parity-required changes have `parity-pass`, not `parity-blocked`
- sensitive screenshots/logs/test data were handled under project policy
- untested platform claims are absent from the final response
