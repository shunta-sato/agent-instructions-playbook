# Mobile platform deviation policy

Use this reference with `mobile-feature-parity` when iOS and Android implementations differ.

## Core rule

Parity means equivalent product capability and externally observable business semantics. It does not require identical source code, widget hierarchy, navigation chrome, lifecycle APIs, or pixel output.

A deviation is acceptable when it is caused by a platform convention, capability, policy, accessibility requirement, lifecycle model, native SDK constraint, or measured quality tradeoff and the shared requirement remains satisfied.

## Usually acceptable deviations

Record only when relevant:

- iOS navigation/back affordances vs Android system/back navigation
- platform permission prompts and settings redirection
- VoiceOver vs TalkBack semantics/announcements
- Dynamic Type vs Android font-scaling behavior
- Keychain vs Android Keystore implementation
- Universal Links vs Android App Links plumbing
- BackgroundTasks/background URLSession vs WorkManager/foreground-service choices
- native share/camera/media picker surfaces
- store review/signing/package metadata
- platform-specific error wording required by OS or store policy when error meaning remains equivalent

## Requires explicit product decision

Do not silently accept:

- a missing success path on one platform
- a materially different data model or server-side side effect
- different retry/idempotency semantics that can duplicate mutations
- different auth/session expiry behavior
- different privacy/data-retention behavior
- missing offline/recovery behavior where the shared requirement includes it
- materially different performance or reliability target without an approved quality-target change
- an accessibility gap that makes the capability unusable on one platform
- one platform shipping against an incompatible API/schema version

## Evidence format

For each deviation record:

- requirement/capability ID
- platform
- observed difference
- reason/category
- shared semantics preserved: yes | no | unknown
- verification method
- approval needed: yes | no
- revisit condition

If shared semantics are `no` or `unknown`, parity cannot be declared passed.
