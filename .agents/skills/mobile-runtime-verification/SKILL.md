---
name: mobile-runtime-verification
description: "Target-bound mobile runtime evidence for exploratory, reproduction, verification, or profiling work involving a running app. Excludes unit/component-only proof and simple execution of an existing E2E suite."
metadata:
  short-description: Mobile runtime verification
  resources:
    - references/maestro-agent-device-policy.md
  templates:
    - templates/runtime-verification-record.yaml
---

# Mobile Runtime Verification

## Purpose

Use a running Android or iOS target as evidence, not as an informal demo. Select an explicit verification mode, bind the result to a source/build/device/environment identity, define the oracle before claiming pass, retain reviewable artifacts, and promote durable behavior to the smallest appropriate regression-test layer.

This skill is tool-neutral. `agent-device`, Argent, Maestro, platform tools, or another approved harness may execute the run. The skill does not install tools, add packages, operate production accounts, publish builds, or treat exploratory observation as deterministic proof.

## When to use

Use this skill when an agent must:

- operate an emulator, simulator, or physical device to verify a changed mobile behavior
- reproduce a device-only, lifecycle, permission, deep-link, native-module, network, or visual failure
- inspect screenshots, logs, network activity, component/runtime state, or performance data while exercising a running app
- convert a successful exploratory path into a durable Jest, component, Maestro, or project-specific regression test

Do not use it when:

- a pure function or state transition is completely proven by focused unit tests
- a React component contract is completely proven by component tests without a native/runtime boundary
- the task is only to run an already-defined E2E command and report its existing result
- no running mobile target is involved
- store publication, signing changes, EAS submission, or production-side effects are the requested operation

## Workflow

1. Select one mode.
   - `explore`: discover behavior or a plausible path; absence of a finding is not a pass.
   - `reproduce`: demonstrate a known failure from a recorded initial state.
   - `verify`: evaluate a declared expected behavior with explicit oracles.
   - `profile`: measure a fixed workload with target, build mode, metric, and threshold recorded.

2. Bind the run to evidence.
   - Record source revision, build identity, platform, device/simulator identity, OS version, build mode, backend/environment, account class, tool name/version, and initial state.
   - If any required identity is unavailable, mark it `unknown` and limit the claim accordingly.

3. Check the runtime-tool boundary.
   - Reuse the approved project preflight for accounts, endpoints, filesystem/network access, screenshot/log retention, redaction, and allowed side effects.
   - Use test/staging data by default. Stop before production purchase, deletion, upload, publication, or another unapproved external side effect.
   - Select one primary device driver for the run.

4. Define the oracle before pass/fail.
   - Examples: a visible/accessibility assertion, state transition, API result, focused log event, known-error absence/presence, visual baseline, or measured threshold.
   - A screenshot, tap sequence, or agent statement by itself is observation, not a pass oracle.

5. Execute the narrowest reproducible journey.
   - Reset or declare the initial app/device state.
   - Record operations, assertions, failures, retries, and artifacts.
   - Do not mask flakiness with broad retries or silently change the environment until the run passes.

6. Classify the result.
   - `pass`: every required oracle is satisfied on the recorded target.
   - `fail`: at least one required oracle is contradicted with reproducible evidence.
   - `blocked`: a required host, device, account, build, permission, or tool is unavailable.
   - `inconclusive`: execution occurred but identity, oracle, or evidence is insufficient.

7. Promote durable coverage.
   - Pure logic -> unit test.
   - React/component behavior -> component test.
   - Stable Android/iOS user journey -> Maestro or the project's canonical mobile E2E layer.
   - Web-only product journey -> the canonical web E2E layer.
   - Diagnostic/profile operation not expressible as a product contract -> retain a focused harness script when justified.
   - Do not permanently maintain equivalent `.ad` and Maestro flows as two sources of truth for the same user journey.

8. Produce the runtime verification record.
   - Open `templates/runtime-verification-record.yaml` only when writing the artifact.
   - Store records under `artifacts/mobile-runtime/<run-id>/` when the target project adopts the registered artifact layout.
   - Open `references/maestro-agent-device-policy.md` when Maestro, agent-device, `.ad` scripts, or exploratory-to-regression promotion is involved.

## Routing rules

- Missing project/toolchain/device facts -> `preflight-mobile-app`.
- Cross-platform product semantics -> `mobile-feature-parity`.
- Performance target or native/shared boundary decision -> `performance-review` and, when architectural, `architecture-decision-analysis`.
- Stable regression test design -> the project's unit/component/E2E test skills and `quality-gate`.
- Store, signing, backend compatibility, or coordinated publication -> `mobile-release-coordination`.
- Runtime logs/metrics/traces added to production code -> `observability`.

## Self-review

- The run has one explicit mode and one primary device driver.
- Source/build/target/environment identity is recorded or marked unknown.
- Every `pass` claim has at least one explicit oracle and target-bound evidence.
- Screenshots and agent observations are not treated as sufficient proof by themselves.
- Production side effects and sensitive artifacts remained inside policy.
- Regression promotion uses the smallest durable test layer and avoids duplicate `.ad`/Maestro ownership.

## Output expectation

- Produce a `Mobile Runtime Verification Record` with mode, identities, environment, tool, initial state, operations, oracles, artifacts, sensitive-data review, result, limitations, and regression-promotion decision.
- Return exactly one result: `pass`, `fail`, `blocked`, or `inconclusive`.
- A `pass` result must cite its explicit oracle and target-bound evidence; otherwise return `inconclusive`.
- State which durable regression layer was added, proposed, or deliberately not applicable.
