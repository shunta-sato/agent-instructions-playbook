# Flutter project detection and first-file routing

Use this reference only when `preflight-mobile-app` has evidence that Flutter may be in scope or the implementation model is still unknown.

## Detection signals

Treat these as evidence, not as a framework decision by themselves:

- `pubspec.yaml` with Flutter SDK dependency
- `.metadata` created by Flutter tooling
- `lib/main.dart` or configured Dart entry points
- `android/`, `ios/`, `web/`, `macos/`, `windows/`, or `linux/` host directories
- `flutter` invocations in CI, Makefile, Taskfile, scripts, or documentation
- FVM, mise, asdf, or other version-manager configuration

Record the Flutter/Dart version only from repository pins or executable output. Do not infer a current version from model knowledge.

## First files and commands

Inspect, when present:

- `pubspec.yaml`
- `pubspec.lock`
- `analysis_options.yaml`
- `.metadata`
- version-manager files such as `.fvmrc`, `.fvm/fvm_config.json`, `.tool-versions`, or `mise.toml`
- root `README*`, `AGENTS.md`, `COMMANDS.md`, and CI configuration
- `android/settings.gradle*`, `android/build.gradle*`, app/module Gradle files, and `AndroidManifest.xml`
- `ios/Podfile`, `.xcodeproj`, `.xcworkspace`, entitlements, plist/configuration files, and Xcode scheme evidence
- `test/` and `integration_test/`

Prefer repository-defined commands. When no canonical wrapper exists, candidate discovery commands include:

```sh
flutter --version
dart --version
flutter doctor -v
flutter devices
flutter analyze
flutter test
```

Do not declare these canonical until the repository's command system accepts them.

## Project-policy facts

Extract but do not choose these during reusable preflight:

- state-management approach
- dependency injection approach
- router/navigation library
- HTTP client and generated-client ownership
- serialization/code-generation convention
- directory/module organization
- generated-file editing policy
- supported target platforms

Durable choices belong in project `AGENTS.md`, `.agent/ctx/mobile.md`, or equivalent project constitution/context files.

## Native boundary signals

Record existing evidence for:

- custom plugins or federated plugins
- MethodChannel/EventChannel/Pigeon usage
- Dart FFI or Native Assets
- Android Kotlin/Java code
- iOS Swift/Objective-C code
- vendor mobile SDKs
- camera/audio/video/native buffer handling

Their presence does not imply a problem. It means implementation planning must preserve the native boundary and its tests.

## Cross-platform rule

A Flutter codebase may share most implementation while still requiring platform-specific behavior. Treat the following as legitimate platform deviations unless product requirements say otherwise:

- navigation/back conventions
- permission prompts and settings flows
- accessibility semantics
- lifecycle/background execution
- secure storage implementation
- deep/universal/app links
- store packaging/signing/review
- platform-specific SDK integration

The parity contract should align product capability and observable business semantics, not force pixel or implementation identity.
