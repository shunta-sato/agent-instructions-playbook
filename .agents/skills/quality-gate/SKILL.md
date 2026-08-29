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
Decide whether one identified candidate is ready to submit. This is an exit gate,
not a broad codebase review or a request for ideal architecture.
## When to use
Use before a delivery-mode submission. The orchestrator assigns one final-gate
owner per candidate identity. Research probes use their research evidence gate.
## How to use
0) Open `references/quality-gate.md` and complete one blocker-focused sweep.
1) Verify the commands and evidence required by the locked route and DoD. Reuse
unchanged evidence from workers, CI, and target runs after checking its identity.
2) Apply the structural exit check. Advisory structure findings are reported but
do not block; hard-guardrail findings do.
3) Validate only evidence required by acceptance, a real operating boundary, a
machine-consumed contract, or a material claim. Skill invocation does not
automatically require a standalone artifact.
   - Open `references/mobile-test-evidence-matrix.md` for any mobile completion
     claim.
   - Open `references/flutter-mobile-test-matrix.md` when the changed mobile
     surface is Flutter.
   - Open `references/react-native-expo-test-adapter.md` when the changed mobile
     surface is React Native or Expo.
   - Open `references/maestro-agentic-verification-policy.md` when Maestro,
     agent-device, Argent, `.ad`, or another device-driving harness contributed
     evidence.
4) Assign each finding `blocking` or `optional` using the concrete standard in
the reference. Reviewer severity labels do not decide this classification.
5) Output `submit` when blocking findings are zero and required checks pass;
otherwise output `no-submit` with the smallest required fixes.

## Output expectation
Start with `Gate decision: submit` or `Gate decision: no-submit`. Include candidate
identity, required checks, blocking findings, optional findings and dispositions,
structure advisories, reused evidence, and remaining claim limits. State
`0 blocking findings`, not `0 findings`, when optional notes remain.
