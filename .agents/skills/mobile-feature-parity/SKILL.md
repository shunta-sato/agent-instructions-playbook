---
name: mobile-feature-parity
description: "Use when one product capability must be implemented or verified across iOS and Android with shared semantics, API/error behavior, allowed platform deviations, and traceable tests. Do not use for single-platform changes or pixel-identical UI enforcement."
metadata:
  short-description: Cross-platform mobile capability parity
  resources:
    - references/platform-deviation-policy.md
  templates:
    - templates/mobile-capability-contract.yaml
---

# Mobile Feature Parity

## Purpose

Keep one product capability aligned across iOS and Android without forcing identical source code or identical platform UI. Produce a capability contract that captures shared behavior, state transitions, cloud/API semantics, platform-specific deviations, verification, and observability.

This skill coordinates implementation evidence. It does not choose the cross-platform framework, redesign the product, publish store builds, or override platform accessibility/navigation/lifecycle conventions.

## When to use

Use when:

- the same feature or changed behavior must ship on both iOS and Android
- a shared Flutter/KMP/React Native implementation still has platform-specific behavior that must be reviewed explicitly
- backend/API changes must remain compatible with both mobile clients
- one platform already implements a capability and the other must reach equivalent product semantics
- release readiness depends on proving both clients implement the same requirement IDs

Do not use for:

- a single-platform feature with no cross-platform contract
- snapshot-only or copy-only changes that do not alter shared capability semantics
- demands for pixel identity; use UI/visual skills and record only product-relevant deviations here
- choosing Flutter vs native vs KMP; use `architecture-decision-analysis`

## Workflow

1. Establish shared requirement IDs.
   - Use existing requirement IDs when present.
   - If functionality, failure behavior, or quality targets are ambiguous, route to `requirements-engineering` first.
   - Separate functional behavior, quality/NFR targets, and delivery/platform constraints.

2. Define shared product semantics.
   - Inputs and preconditions.
   - Success result and externally observable state transitions.
   - User-visible errors and recovery behavior.
   - Cancellation, retry, duplicate-request, and offline/reconnect behavior when relevant.
   - Data ownership/cache authority when the capability persists or syncs data.

3. Define the cloud/API contract when applicable.
   - Operation/schema/version or generated-client ownership.
   - Compatibility window for currently deployed mobile versions.
   - Idempotency/duplicate handling for retried mutations.
   - Auth/session assumptions without copying credentials.
   - Correlation/observability fields needed to compare client behavior.
   - Route public contract work to `preflight-api-compat` and auth/session work to `preflight-auth-session` when their preflight conditions apply.

4. Define platform realizations.
   - Record iOS and Android entry points, lifecycle/background behavior, permissions, secure storage, deep-link/navigation behavior, and native integration only where relevant.
   - Open `references/platform-deviation-policy.md` when deciding whether a difference is acceptable.
   - Shared behavior is mandatory unless an allowed deviation is recorded with rationale and verification.

5. Build the parity verification matrix.
   - For every shared requirement, name iOS evidence, Android evidence, and any shared/core evidence.
   - Prefer tests at the lowest layer that proves the contract, then add platform/integration/device evidence where lifecycle, permission, plugin, native, rendering, or store behavior requires it.
   - Web preview does not substitute for Android/iOS verification.
   - A shared Flutter unit/widget test does not substitute for platform verification when the requirement crosses a platform boundary.

6. Check observability parity.
   - Use the same logical success/failure/correlation concepts across clients even if SDK implementations differ.
   - Do not log tokens, credentials, sensitive payloads, or customer data merely to make parity easier to inspect.
   - Runtime behavior changes still route to `observability`.

7. Produce the capability contract.
   - Open `templates/mobile-capability-contract.yaml` only when writing the artifact.
   - Record unknowns explicitly; do not mark a platform complete without evidence.

8. Gate completion.
   - `parity-pass`: every required shared behavior has acceptable iOS and Android evidence, with intentional deviations documented.
   - `parity-blocked`: one platform, API compatibility surface, required quality target, or verification path is missing/failed.
   - `not-applicable`: the task is truly single-platform and no shared capability contract is required.

## Handoffs

- Ambiguous shared behavior/NFRs -> `requirements-engineering`.
- Cross-boundary framework/architecture choice -> `architecture-decision-analysis`.
- UI/interaction review -> `uiux-core` and `visual-regression-testing`.
- Android concurrency/background work -> `concurrency-core` + `concurrency-android`.
- Runtime/API/retry/fallback behavior -> `error-handling` and `observability` as triggered.
- Release synchronization -> `mobile-release-coordination` when available/triggered.

## Self-review

- Product capability parity is separated from code-sharing percentage and pixel identity.
- Shared requirement IDs map to both platform implementations and tests.
- Allowed deviations have platform rationale rather than convenience-only justification.
- API/auth compatibility is not hidden inside UI implementation details.
- Web-only verification is never treated as mobile parity evidence.
- Unknown or untested platform behavior blocks a parity-pass claim.

## Output expectation

Return a Mobile Capability Parity Record containing:

- capability/requirement IDs and shared semantics
- cloud/API/auth compatibility notes when applicable
- iOS realization and verification evidence
- Android realization and verification evidence
- allowed platform deviations with rationale
- observability/correlation expectations
- parity verification matrix
- decision: `parity-pass` | `parity-blocked` | `not-applicable`

Use `templates/mobile-capability-contract.yaml` for a durable machine-readable artifact when the repository benefits from one.
