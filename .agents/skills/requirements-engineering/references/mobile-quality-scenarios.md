# Mobile quality scenarios

Use this reference with `requirements-engineering` when a requirement targets iOS, Android, Flutter, or another mobile client and platform constraints materially affect acceptance criteria.

Keep metrics project-specific. This reference provides dimensions and scenario structure, not universal thresholds.

## Requirement classification

Do not collapse all cross-platform statements into one NFR bucket.

- Product behavior available on both iOS and Android: functional requirement plus target-platform scope/constraint.
- Equivalent business result/state transition on both platforms: capability parity requirement.
- Both clients ready in the same release train/window: delivery/release constraint.
- Platform-native navigation, accessibility, permissions, lifecycle, and store compliance: compatibility/usability/platform-conformance quality requirements or constraints.
- Flutter/KMP/native/shared-code percentage: architecture/implementation constraint, not inherently a product requirement.
- Exact store visibility at the same instant: usually not fully controllable; express the controllable release action window and observation requirement instead.

## Quality dimensions to consider

Select only those relevant to the feature.

### Performance efficiency

- cold/warm startup or resume latency
- user-action-to-visible-result latency
- frame/build/raster time and jank under a stated workload
- upload/download throughput and timeout behavior
- memory peak and steady-state growth
- CPU use for sustained/background work
- app/package size where it affects delivery or device constraints

### Reliability and recoverability

- process termination and state restoration
- network loss, reconnect, retry, and duplicate-request handling
- offline/cache authority and stale-data behavior
- sync conflict handling
- background-task suspension/resumption
- partial upload/download recovery
- crash/hang/ANR or equivalent failure criteria

### Compatibility and platform conformance

- supported OS versions and device classes
- phone/tablet/foldable/orientation behavior when in scope
- permission-denied and permission-revoked paths
- deep/universal/app links
- platform-specific background execution limits
- backend/API compatibility window across deployed client versions
- generated-client/schema regeneration and compatibility checks

### Usability and accessibility

- text scaling / Dynamic Type / font scaling
- VoiceOver / TalkBack semantics and focus order
- touch target/gesture alternatives
- color/contrast/theme behavior
- platform-native navigation/back expectations
- localization, locale, time zone, calendar, and number/date formatting

### Security and privacy

- secure token/small-secret storage via platform facilities
- no embedded confidential client secret assumption for distributed apps
- transport security and endpoint policy
- PII/token/log redaction
- camera/microphone/location/photo permission rationale and denial behavior
- local data deletion/account deletion and cache cleanup where applicable

### Operability and supportability

- correlation IDs or equivalent cross-client/backend tracing concept
- user-visible error taxonomy aligned across platforms
- diagnostic signals that avoid sensitive payload logging
- staged/test environment behavior
- feature flag / kill switch / minimum-client-version behavior when needed

### Release quality

- both platform artifacts trace to the intended source revision and capability contract
- platform-specific signing/build/review readiness
- backend deployed with compatibility for old and new clients
- controlled release action window and post-release availability observation
- rollback/disable strategy for backend or feature behavior

## Quality scenario template

For every selected quality target record:

```text
Scenario:
Stimulus:
Environment / device / OS / network:
Observable response:
Metric:
Target:
Measurement method:
Platform scope: shared | ios | android | each-platform-separately
Verification evidence:
Measured result: <filled before gate or not-measured with reason>
```

Do not use a desktop/web measurement as proof of a mobile target unless the requirement explicitly scopes to shared non-platform code and the measured property is platform-independent.

## Parity handoff

When one capability must ship on both iOS and Android, keep the requirement IDs here and hand them to `mobile-feature-parity`. That skill owns the iOS/Android evidence matrix and allowed platform deviations; this reference owns making the requirement measurable and testable first.
