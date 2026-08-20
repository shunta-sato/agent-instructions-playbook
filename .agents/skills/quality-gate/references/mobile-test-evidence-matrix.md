# Mobile test evidence matrix

Open this reference when a submission claims mobile behavior, cross-platform completion, native/runtime correctness, or device-bound quality.

## Evidence selection

| Change surface | Minimum durable evidence |
| --- | --- |
| Pure language/domain logic | focused unit tests |
| React/widget/component behavior without native boundary | component/widget tests |
| Stable Android/iOS user journey | canonical mobile E2E flow, such as Maestro |
| Permission, deep link, lifecycle, native module/SDK, background behavior | target-specific Android and/or iOS runtime evidence plus durable regression where feasible |
| Visual behavior | visual-regression evidence and target identity |
| Performance | representative target, build mode, workload, metric, threshold, and result |
| Web product surface | canonical web E2E; never substitute it for a mobile target claim |
| Shared iOS/Android capability | shared evidence plus separate Android and iOS evidence required by the parity record |

## Evidence classes

- **Regression evidence**: repeatable project-owned test with explicit assertions.
- **Runtime verification evidence**: target-bound run with explicit oracle and retained artifacts.
- **Observation**: screenshot, manual/agent statement, log excerpt, or exploratory path without a complete oracle.

Observation can motivate a test or finding but cannot independently satisfy a submit-blocking mobile claim.

## Gate rules

- Record Android and iOS separately; `unknown` or unavailable remains blocked when both are claimed complete.
- A simulator/emulator pass does not prove a physical-device-only behavior.
- A web/shared-test pass does not prove permission, native-module, signing, lifecycle, or store behavior.
- Require source/build/target/environment identity for runtime evidence.
- Require an explicit oracle for every runtime `pass`.
- Use the framework adapter for project-specific test commands and boundaries.
