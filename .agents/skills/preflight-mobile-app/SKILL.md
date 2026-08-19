---
name: preflight-mobile-app
description: "Preflight iOS, Android, Flutter, or cross-platform mobile app work before new-project, unfamiliar-repo, cross-platform, signing, device, store, or cloud-connected implementation. Do not use for already-routed small mobile edits."
metadata:
  short-description: Mobile app preflight
  resources:
    - references/flutter-project-detection.md
    - references/flutter-mcp-security.md
  commands:
    - scripts/inspect_mobile_project.py
  templates:
    - templates/mobile-project-profile.yaml
---

# Mobile App Preflight

## Purpose

Prepare mobile application work before implementation starts. Detect the actual mobile stack, target platforms, host/toolchain readiness, native escape hatches, cloud boundaries, signing/release surfaces, and the specialist skills that must run next.

This skill is a domain helper for `preflight-engineering`. It does not implement features, install SDKs, read signing credentials, publish store builds, change production configuration, or assume iOS and Android must share identical UI implementations.

## When to use

Use this skill before implementation when one or more applies:

- a new iOS, Android, Flutter, Kotlin Multiplatform, React Native, or other mobile application is being started
- the repository's mobile stack, targets, build variants, signing path, simulator/emulator path, or canonical test commands are unfamiliar or unknown
- one feature must ship on both iOS and Android and the shared/platform-specific boundary is not yet explicit
- mobile code crosses API, auth, offline sync, push notification, background execution, file upload, camera/media, native SDK, or store-release boundaries
- the task requires checking whether the current host can actually build or validate each target platform

Do not use it for an already-routed, small, single-platform edit when the repository profile, commands, tests, signing boundary, and platform constraints are already documented and current.

## Workflow

1. Confirm the mobile trigger and intended targets.
   - Record `ios`, `android`, `web`, desktop targets, and any backend/cloud surface separately.
   - Separate capability parity from pixel-identical UI. Shared product behavior may still require platform-native navigation, permissions, accessibility, and lifecycle handling.

2. Detect the implementation model from repository evidence.
   - Classify as `dual-native`, `flutter`, `kmp-native-ui`, `compose-multiplatform`, `react-native`, `other`, or `unknown`.
   - For Flutter detection and first-file routing, open `references/flutter-project-detection.md`.
   - Run `python3 .agents/skills/preflight-mobile-app/scripts/inspect_mobile_project.py --root . --markdown` when the stack or target surfaces are not already confirmed.
   - Mark every result as `confirmed`, `inferred`, or `unknown`; never select a framework from the request alone when repository evidence disagrees.

3. Record platform/toolchain readiness.
   - iOS: macOS/Xcode availability, project/workspace, schemes/configurations, deployment target, simulator/device path, entitlements/capabilities, signing reference, and CI/macOS runner path.
   - Android: JDK, Gradle wrapper, Android Gradle Plugin/SDK targets, modules/variants, emulator/device path, manifest/permissions, signing reference, and CI path.
   - Flutter: Flutter/Dart SDK and version-manager evidence, enabled targets, analyzer/test commands, Android/iOS host readiness, and Dart/Flutter MCP availability when used.
   - A missing host capability is a blocker or delegated validation path, not evidence that the target passed.

4. Map cloud-connected boundaries.
   - Identify API contract/generated clients, authentication/session, network timeout/retry/idempotency, offline/cache authority, background sync, push, upload, telemetry, feature flags, minimum-client compatibility, and production-vs-staging endpoints.
   - Route to `preflight-api-compat` for public contracts/generated clients and `preflight-auth-session` for auth/session work.
   - Do not place secrets, signing keys, service-account contents, tokens, or keystore contents into the profile. Record references/paths only.

5. Check native/performance escape-hatch risk.
   - Flag camera/audio/video frame pipelines, high-rate sensors, large binary transfer, 30/60fps processing, low-latency requirements, vendor SDKs, Bluetooth/USB, C/C++ libraries, platform channels, FFI, or background execution as a native/performance decision surface.
   - Do not force pure Dart or shared-code implementation merely because the repository uses Flutter.
   - Route architecture choices with measurable quality drivers to `architecture-decision-analysis`; route missing quality targets to `requirements-engineering` first.

6. Check Dart/Flutter MCP security when applicable.
   - Open `references/flutter-mcp-security.md` when Dart/Flutter MCP will be enabled or evaluated.
   - Distinguish local MCP/tooling traffic from cloud-LLM traffic and from explicit package-network operations.
   - Prefer analytics suppression, constrained workspace mounts, staging/test accounts, and disabled package-network tools for confidential code unless policy explicitly allows them.
   - Treat MCP roots as workspace hints, not a security boundary; enforce filesystem/network isolation outside MCP when required.

7. Produce the mobile project profile.
   - Open `templates/mobile-project-profile.yaml` only when writing the artifact.
   - Fill confirmed/inferred/unknown facts, required routes, blockers, and verification commands without inventing versions or signing state.

8. Return the common domain preflight contract.
   - Return every heading required by `preflight-domain-template`.
   - Propose `.agent/ctx/mobile.md`, `.agent/maps/mobile-project.yaml`, and nested mobile `AGENTS.md` fragments only when the target repository shape supports them.
   - Keep project-specific architecture choices such as state-management library, router, HTTP client, DI framework, or directory convention in project context/AGENTS, not in this reusable skill.

## Routing rules

- Ambiguous functionality or NFR targets -> `requirements-engineering`.
- Cross-boundary architecture/framework choice -> `architecture-decision-analysis` after measurable quality drivers exist.
- Public API/schema/generated client -> `preflight-api-compat`.
- OAuth/session/token/login -> `preflight-auth-session`.
- Android background/concurrency behavior -> `concurrency-core` + `concurrency-android` during implementation.
- UI/UX work -> `uiux-core` with matching platform adapter.
- Runtime behavior change -> `observability` during implementation.
- Package/dependency changes -> use repository dependency policy and canonical commands; do not silently add packages during preflight.

## Self-review

- Framework and targets came from repository evidence or are marked unknown.
- iOS validation is not claimed from a non-macOS host without a macOS runner/device path.
- Capability parity is separated from platform-native UI/lifecycle behavior.
- Secret/signing values were not read or copied.
- Cloud/API/auth/native/performance/store boundaries are routed rather than buried in generic mobile guidance.
- Flutter MCP roots are not treated as filesystem isolation.
- Project-specific framework choices were not hard-coded into the reusable skill.

## Output expectation

- Return the common output contract from `preflight-domain-template`, filled for the mobile-app domain.
- Produce or propose `.agent/maps/mobile-project.yaml` using `templates/mobile-project-profile.yaml` when a durable project profile is useful.
- State implementation model, target platforms, host/toolchain readiness, cloud boundaries, native/performance risk, required routes, blockers, and unknowns.
- For Flutter MCP use, state whether analytics, package-network tools, workspace isolation, test/staging accounts, and cloud-LLM data flow have been reviewed.
