# Mobile evidence boundaries

A successful Flutter, React Native/Expo or native host test proves its exercised
logic, not a deployed device journey. Web previews do not establish native bridge,
permission, background lifecycle, push, storage or hardware behavior. Inspect the
actual framework/toolchain versions and supported deployment mode before testing.

Agent-operated harnesses need independent oracles: tool acceptance or a successful
tap command is not proof the intended state changed. Record app/build identity,
platform, execution environment, scenario, actions, observed state and limits.
Screenshots prove only visible state; backend/persistence claims need matching
state evidence. Preserve source and runtime identity across delegated work.

For parity, inspect the same user capability and error/recovery semantics on both
platforms. A shared implementation can still have platform-specific failures.
Release signing, store submission and production rollout require their own
authorization and evidence; runtime testing grants none of those permissions.
