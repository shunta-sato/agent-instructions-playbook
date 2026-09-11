---
name: quality-gate
description: "Use before a delivery-mode submission to decide whether the identified candidate passed required checks and has zero blocking findings. Non-blocking findings may remain with explicit dispositions."
metadata:
  short-description: Blocking-finding quality gate
  requires:
    - references/quality-gate.md
  resources:
    - references/mobile-test-evidence-matrix.md
    - references/flutter-mobile-test-matrix.md
    - references/react-native-expo-test-adapter.md
    - references/maestro-agentic-verification-policy.md
---
## Purpose
Decide whether one identified candidate is ready for the stated delivery/use,
not whether its code is ideal. Functional and required quality criteria both apply.
## When to use
Use before delivery-mode submission. One orchestrator-assigned owner assembles
final evidence; research probes use their research evidence gate.
## How to use
0) Open `references/quality-gate.md` and sweep applicable blockers once.
1) Read the inherited DoD, Quality Targets, and material context changes. Reuse
valid evidence; required conditions with missing agreed proof remain blocking.
A `provisional` or `not-measured` label does not waive a required NFR.
2) Apply the structural exit check: advisory findings do not block; hard findings do.
3) Validate evidence for acceptance, actual boundaries, machine contracts, and
claims. Skill invocation alone does not require a standalone artifact.
   - Open `references/mobile-test-evidence-matrix.md` for mobile completion claims.
   - Open `references/flutter-mobile-test-matrix.md` for changed Flutter surfaces.
   - Open `references/react-native-expo-test-adapter.md` for React Native or Expo.
   - Open `references/maestro-agentic-verification-policy.md` when a device-driving
     harness such as Maestro, agent-device, Argent, or `.ad` contributed evidence.
4) Classify findings against the inherited contract, not reviewer labels. A missed
optional target can remain; a newly discovered necessary NFR revises affected scope.
5) Output `submit` only when required conditions/checks pass and blockers are zero;
otherwise `no-submit` with the smallest required fix or missing evidence.

## Output expectation
Start with `Gate decision: submit` or `Gate decision: no-submit`. Include candidate
and intended use, required checks/Quality Targets, blocking and optional findings,
structure advisories, reused evidence, and limits. State `0 blocking findings`,
not `0 findings`, when optional notes remain. Do not relabel a release as a probe.
