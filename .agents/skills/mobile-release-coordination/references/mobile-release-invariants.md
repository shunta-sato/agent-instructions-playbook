# Mobile release invariants

Use this reference with `mobile-release-coordination`.

## Release identity

- Every platform artifact must map to the intended source revision, configuration, and capability/release record.
- Do not treat version strings alone as provenance when build artifacts can differ.
- Generated API/client/schema inputs should identify their compatible contract revision when relevant.

## Mixed-version compatibility

Mobile distribution creates a period in which old and new clients coexist.

- Backend-first rollout requires backward compatibility for currently supported deployed clients.
- New backend behavior must not assume the new mobile binary is already available everywhere.
- Retryable mutations require stable duplicate/idempotency behavior across the mixed-version window.
- Removing old endpoints, fields, auth semantics, or error contracts requires an explicit compatibility/deprecation decision and evidence that the removal condition has been met.
- Feature flags may stage exposure but do not excuse incompatible APIs beneath the flag.

## Store timing

Distinguish controllable and observable events.

Controllable or project-governed examples:

- which reviewed artifact is selected
- when the team submits or requests publication using its approved tooling
- whether both platforms are held until their defined releasable states
- whether a feature flag is enabled after publication actions

Externally controlled or only observable examples include review completion and final end-user visibility/propagation. Do not express exact simultaneity as a guaranteed requirement unless the project has a mechanism and evidence that makes it controllable.

Prefer a release requirement such as:

- both platform artifacts must be approved/releasable before the coordinated publication window opens
- the publication actions must occur inside the defined action window
- actual store availability must be observed and recorded after the actions

## Signing and credentials

- Record signing identities, certificate/profile/keystore/service-account locations, owners, or references only as project policy permits.
- Do not copy private keys, passwords, tokens, cookies, certificate private material, provisioning secrets, or store service-account credentials into Agent context or release records.
- Signing/publishing tools should run under least privilege and project approval policy.
- A release-readiness check may verify presence/status without granting the reasoning agent unrestricted access to production publication credentials.

## Verification and parity

- `quality-gate` remains mandatory for delivery changes.
- If a capability is promised on both platforms and `mobile-feature-parity` applies, `parity-pass` is required before coordinated release readiness can be `ready`.
- Shared Dart/widget tests do not replace Android/iOS platform evidence for permissions, lifecycle, native plugins, deep links, background work, secure storage, or other platform boundaries.
- Missing iOS evidence due to lack of a local macOS host is a routing/blocker condition, not a pass.

## Rollout controls

Use only controls that the product actually owns:

- backend compatibility window
- feature flag / remote configuration
- kill switch or server-side disable path
- rate/percentage rollout when supported by the chosen distribution/tooling and project policy
- backend rollback or forward-fix
- minimum-client enforcement only under explicit policy

Feature flags and kill switches are operational safety controls, not substitutes for correctness, privacy, security, or required test evidence.

## Recovery

Binary rollback after store publication may not be immediate or equivalent to backend rollback. Define recovery in terms of mechanisms the system controls:

- disable new server-side behavior
- keep old/new API compatibility
- turn off a guarded client feature remotely when available
- forward-fix the backend/client
- pause further rollout/publication actions
- communicate a blocked/recovery state to release owners

Never state “rollback available” without naming the mechanism and what already-published clients will do.

## Observation

After publication actions, observe only signals needed by the release contract, such as:

- store availability by required platform/region where relevant
- crash/hang/ANR or equivalent health signals
- backend error/latency changes
- auth/session failures
- parity-critical functional failures
- feature flag exposure/adoption

Keep telemetry free of credentials and unnecessary sensitive payloads.
