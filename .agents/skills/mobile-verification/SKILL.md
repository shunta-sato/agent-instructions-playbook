---
name: mobile-verification
description: "Reproduce or verify changed behavior on a running mobile device, emulator or simulator with target-bound evidence."
---

# Mobile runtime verification

Choose whether the current run is exploration, reproduction, verification or profiling.
Bind evidence to source/build, platform/device/OS, build mode, backend/environment,
account class, tool version and initial state. Unknown identity limits the claim.

Use an explicit expected-state, API, accessibility, log or metric oracle for a pass.
A screenshot or tap sequence alone does not establish that behavior passed. Keep
Android and iOS results separate when both platforms are claimed. Unit/component
proof remains sufficient for behavior with no affected native/runtime boundary.

`references/device-tools.md` covers exploratory-driver to durable-regression handoff
and selector/initial-state discipline. Use approved test accounts and endpoints.
Screenshots/logs can contain sensitive data; apply project retention/redaction rules.
No store upload, purchase, production deletion or signing change is implied.

Report pass, fail, blocked or inconclusive with evidence and limits, using the existing
result location. Do not mask flakiness with broad retries or silently switch the
environment until the run passes. Add the smallest durable regression layer needed,
not duplicate ownership in multiple device-driving frameworks.
