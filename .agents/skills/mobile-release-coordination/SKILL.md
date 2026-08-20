---
name: mobile-release-coordination
description: "Use when iOS and Android releases must be coordinated across builds, signing, store review/readiness, backend compatibility, feature flags, rollback, and a controlled release window. Do not use for ordinary feature implementation or single-platform build fixes."
metadata:
  short-description: Coordinated iOS and Android release gate
  resources:
    - references/mobile-release-invariants.md
  templates:
    - templates/mobile-release-readiness.yaml
---

# Mobile Release Coordination

## Purpose

Coordinate release readiness for one mobile product across iOS, Android, and any coupled backend/cloud rollout. Decide whether the release is ready to enter its controlled publication window without claiming control over store review or propagation timing that the team does not actually possess.

This skill is a release gate and coordination record. It does not upload binaries, change store metadata, sign artifacts, deploy production backend changes, flip production feature flags, publish an app, or perform destructive rollback actions. Those remain explicit tools/commands with the project's required approvals.

## When to use

Use this skill when one or more applies:

- iOS and Android are intended to ship the same capability or release train together
- publication must be coordinated within a defined release window
- a backend/API change must remain compatible while old and new mobile versions coexist
- store review/readiness state must be aligned before publication actions
- feature flags, minimum-client rules, kill switches, or rollback/fallback plans are part of the mobile rollout
- a release owner needs a single `ready` / `no-go` decision backed by both platform artifacts and verification evidence

Do not use it for:

- ordinary implementation before release planning
- a single-platform local build/signing fix with no coordinated release decision
- choosing the application framework or architecture
- replacing the normal `quality-gate`; this skill consumes its evidence and adds release-level coordination

## Workflow

1. Define release identity and scope.
   - Release/capability IDs and source revision.
   - Intended iOS and Android versions/build identifiers.
   - Backend/API/schema/feature-flag revision or compatibility state when coupled.
   - Release owner, approval surface, and intended publication action window.
   - Separate `same release train/window` from `exactly simultaneous store visibility`; the latter is not a valid guarantee unless the project has evidence that it controls it.

2. Confirm product and quality evidence.
   - Require the normal `quality-gate` result for each changed surface.
   - When `mobile-feature-parity` was triggered, require `parity-pass` for the capabilities claimed on both platforms.
   - Required mobile quality targets must be measured and met, or the release is `no-go`.
   - Unknown/untested platform claims are not release-ready.

3. Confirm artifact provenance.
   - iOS and Android artifacts trace to the intended source revision and configuration.
   - Record build/test/signing status by reference only; never copy signing keys, certificates, provisioning secrets, keystore passwords, service-account credentials, or tokens.
   - Confirm generated clients/schema digests or equivalent contract provenance when relevant.

4. Confirm backend compatibility and rollout order.
   - A backend deployed before mobile publication must support the currently deployed client population as well as the new clients for the declared compatibility window.
   - Do not remove old API behavior merely because new store submissions exist.
   - Mutating operations must preserve the declared idempotency/retry behavior during mixed-version rollout.
   - Record minimum-client enforcement, migration, or deprecation only when the project explicitly owns that policy.

5. Confirm store readiness without pretending to control review timing.
   - Record iOS and Android submission/review/readiness states as `confirmed`, `inferred`, or `unknown` from project/store tooling evidence.
   - Publication actions remain blocked until each required platform is in the project's defined releasable state.
   - Store approval, propagation, indexing, CDN, regional availability, or device-visible timing outside project control is observation, not a guaranteed exact timestamp.
   - If one platform is delayed, choose `hold-both`, `release-asymmetric-with-approval`, or `no-go`; do not silently publish the other when coordinated release was required.

6. Confirm rollout controls.
   - Feature flag / remote configuration state when used.
   - Kill switch or server-side disable path for risky new behavior when applicable.
   - Backend rollback/fallback path compatible with already-published clients.
   - Client-side rollback expectations: store distribution often makes immediate binary rollback non-equivalent to server rollback, so define the actual recovery mechanism.
   - Observability/alert signals and owner for the release window.

7. Define execution and observation steps.
   - List explicit, reviewable publication/deployment/flag actions in order, each with required actor/tool and approval.
   - Keep actions separate from this skill's decision; do not execute them while producing the readiness record.
   - Define post-action observations: store availability, crash/error/latency signals, backend compatibility, feature adoption, and parity-critical failures.

8. Decide:
   - `ready`: all required platform/product/backend/store/rollback evidence exists and publication actions may enter the approved window.
   - `no-go`: any required artifact, compatibility, platform evidence, store readiness, approval, rollback path, or quality target is missing/failed.
   - `not-applicable`: no coordinated mobile release decision is needed.

## Reference routing

Open `references/mobile-release-invariants.md` for compatibility-window, store-timing, signing/credential, and rollout/rollback invariants.

## Self-review

- Both mobile artifacts are tied to the intended source/capability revision.
- `ready` is not based on one platform's evidence generalized to the other.
- Backend compatibility covers mixed old/new client populations.
- No signing or store credential value is copied into the record.
- Store review/visibility timing outside project control is not promised as exact.
- Feature flags/kill switches are not treated as substitutes for required client correctness.
- Publication/deployment/flag actions are listed but not executed by this skill.
- Recovery behavior is explicit for backend and already-published clients.

## Output expectation

Return a Mobile Release Readiness Record containing:

- release identity, source revision, capability IDs, and intended platform versions/builds
- iOS artifact, verification, signing-reference, and store-readiness state
- Android artifact, verification, signing-reference, and store-readiness state
- backend/API compatibility and mixed-version window state
- feature flag / kill switch / minimum-client state when applicable
- publication action window, ordered actions, required approvals, and owners
- rollback/fallback and post-release observation plan
- blockers/unknowns
- decision: `ready` | `no-go` | `not-applicable`

Use `templates/mobile-release-readiness.yaml` for a durable machine-readable record when useful.
