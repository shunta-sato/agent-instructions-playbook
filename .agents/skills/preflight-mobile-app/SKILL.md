---
name: preflight-mobile-app
description: "Preflight iOS, Android, Flutter, React Native, Expo, or cross-platform mobile app work before new-project, unfamiliar-repo, cross-platform, signing, device, store, runtime-tool, or cloud-connected implementation. Do not use for already-routed small mobile edits."
metadata:
  short-description: Mobile app preflight
  resources:
    - references/flutter-project-detection.md
    - references/flutter-mcp-security.md
    - references/react-native-expo-project-detection.md
    - references/mobile-runtime-tool-security.md
  commands:
    - scripts/inspect_mobile_project.py
  templates:
    - templates/mobile-project-profile.yaml
---

# Mobile App Preflight

## Purpose

Prepare mobile application work before implementation starts. Detect the actual stack, target platforms, host/toolchain readiness, test/runtime harness, native escape hatches, cloud boundaries, signing/release surfaces, and specialist skills that must run next.

This skill is a domain helper for `preflight-engineering`. It does not implement features, install SDKs/packages, execute dynamic app config, read credentials, operate production accounts, publish builds, or assume iOS and Android require identical UI implementations.

## When to use

Use this skill before implementation when one or more applies:

- a new iOS, Android, Flutter, React Native, Expo, Kotlin Multiplatform, or other mobile application is being started
- the repository's stack, targets, package manager, build variants, signing path, simulator/emulator path, test layers, runtime harness, or canonical commands are unfamiliar or unknown
- one feature must ship on both iOS and Android and the shared/platform-specific boundary is not explicit
- mobile code crosses API, auth, offline sync, push, background execution, upload/media, native SDK, device automation, or store-release boundaries
- the current host's ability to build and validate each claimed platform is unknown

Do not use it for an already-routed, small, single-platform edit when repository profile, commands, tests, signing boundary, and platform constraints are documented and current.

## Workflow

1. Confirm trigger and intended targets.
   - Record `ios`, `android`, `web`, desktop targets, and backend/cloud surfaces separately.
   - Separate capability parity from pixel identity and platform-native behavior.

2. Detect the implementation model from repository evidence.
   - Classify as `dual-native`, `flutter`, `react-native-expo`, `react-native-bare-or-brownfield`, `kmp-native-ui`, `compose-multiplatform`, `other`, or `unknown`.
   - Run `python3 .agents/skills/preflight-mobile-app/scripts/inspect_mobile_project.py --root . --markdown` when facts are not already confirmed.
   - Open `references/flutter-project-detection.md` for Flutter or `references/react-native-expo-project-detection.md` for React Native/Expo.
   - Mark results `confirmed`, `inferred`, or `unknown`; do not select a framework from request text when repository evidence differs.

3. Record platform and framework readiness.
   - iOS: macOS/Xcode, project/workspace or generated-project model, schemes/configurations, deployment target, simulator/device, entitlements, signing reference, and macOS CI path.
   - Android: JDK, package/Gradle wrapper, SDK targets, modules/variants, emulator/device, manifest/permissions, signing reference, and CI path.
   - Flutter: SDK/version manager, analyzer/test commands, targets, and MCP when used.
   - React Native/Expo: Node/package manager and lockfile, RN/Expo versions, Expo config/CNG/native-project ownership, Expo Go versus development/release build, EAS surfaces, Jest/RNTL, Maestro, Playwright, and runtime-harness readiness.
   - A missing host/device capability is a blocker or delegated path, not evidence that the target passed.

4. Map cloud-connected boundaries.
   - Identify API contract/generated clients, auth/session, timeout/retry/idempotency, offline/cache authority, background sync, push, upload, telemetry, feature flags, minimum-client compatibility, and staging/production endpoints.
   - Route public contracts to `preflight-api-compat` and auth/session work to `preflight-auth-session`.
   - Record secret/signing/account references only; never copy their values.

5. Check native/performance escape-hatch risk.
   - Flag high-rate camera/audio/video, large binary transfer, frame-rate/latency targets, vendor SDKs, Bluetooth/USB, C/C++, JSI/TurboModule/FFI/platform modules, or background execution.
   - Do not force work into Dart or JavaScript merely because a cross-platform framework is present.
   - Route measurable architecture choices to `architecture-decision-analysis`; route missing targets to `requirements-engineering` first.

6. Check agent/runtime tool security when applicable.
   - Open `references/flutter-mcp-security.md` for Dart/Flutter MCP.
   - Open `references/mobile-runtime-tool-security.md` for agent-device, Argent, Expo MCP, or another device/account-backed runtime tool.
   - Separate local device control, filesystem/network access, app traffic, package traffic, account-backed services, remote data paths, and retained artifacts.
   - Prefer staging/test accounts, explicit side-effect policy, constrained mounts/network, and artifact redaction.

7. Produce the mobile project profile.
   - Open `templates/mobile-project-profile.yaml` only when writing the artifact.
   - Fill facts, required routes, blockers, and verification paths without inventing versions, signing state, build identity, or device readiness.

8. Return the common domain preflight contract.
   - Return every heading required by `preflight-domain-template`.
   - Propose `.agent/ctx/mobile.md`, `.agent/maps/mobile-project.yaml`, and nested mobile `AGENTS.md` only when useful.
   - Keep state-management, router, HTTP client, DI, directory layout, selector policy, and dependency decisions in project context, not this reusable skill.

## Routing rules

- Ambiguous functionality or NFR targets -> `requirements-engineering`.
- One capability required on both iOS and Android -> `mobile-feature-parity`.
- Agent must operate a running app to explore, reproduce, verify, or profile -> `mobile-runtime-verification` after tool/account/device preflight.
- Coordinated store/backend release -> `mobile-release-coordination`.
- Cross-boundary architecture/framework choice -> `architecture-decision-analysis` after quality drivers exist.
- Public API/schema/generated client -> `preflight-api-compat`.
- OAuth/session/token/login -> `preflight-auth-session`.
- Android background/concurrency behavior -> `concurrency-core` + `concurrency-android` during implementation.
- UI/UX -> `uiux-core`; runtime behavior -> `observability`; package changes -> project dependency policy.

## Self-review

- Framework and targets came from repository evidence or remain unknown.
- Expo CNG without committed native directories was not misclassified as unsupported mobile platforms.
- Dynamic Expo config was not executed during read-only inspection.
- iOS was not claimed from a non-macOS host without delegated evidence.
- Capability parity is separate from platform-native UI/lifecycle behavior.
- Secret/signing/account values were not read or copied.
- Runtime tools have explicit account, side-effect, data-path, and artifact policies.
- Project-specific framework choices were not hard-coded into the reusable skill.

## Output expectation

- Return the common output contract from `preflight-domain-template`, filled for the mobile domain.
- Produce or propose `.agent/maps/mobile-project.yaml` using the template when durable context is useful.
- State implementation/native-project model, targets, package/toolchain readiness, test/runtime harness, cloud/native/performance/release boundaries, required routes, blockers, and unknowns.
- For an agent/runtime tool, state account/environment, allowed side effects, filesystem/network/data paths, artifact retention/redaction, and approval status.
