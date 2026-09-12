---
name: mobile-release
description: "Use when coordinating an iOS/Android release, store submission or cross-platform rollout decision."
---

# Mobile release coordination

Establish the authorized release scope, app/build IDs, signing/configuration,
platform versions, compatible services, feature flags and required runtime proof.
A code merge, simulator pass or one platform's success is not the other platform's
release evidence.

Check intentional parity differences, rollout order, store/review constraints and
rollback or forward-repair limits from the actual release process. Preserve
required checks and branch protection. Publication and deployment must be explicitly
within authority; a skill invocation cannot approve them.

Assemble existing evidence once for the identified candidates. Reverify only
invalidated proof. Report each platform's readiness, blockers, authorized next
operation and material limits; do not create a parallel release ledger without a
consumer or claim publication until the actual operation succeeds.
