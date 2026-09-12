---
name: auth-session
description: "Change or investigate authentication, authorization, session lifetime, refresh, or credential boundaries."
---

# Authentication and session boundaries

Establish actors, trust boundaries, supported flows and the concrete failure impact.
Authentication is not authorization. Trace token/session creation, storage, use,
rotation, expiry, revocation and logout only for affected paths.

Check concurrent refresh, replay, confused identity, cross-tenant access, redirect
validation, and retry/idempotency when those paths exist. Use the current provider
contract and configured SDK, not remembered defaults. Never collect or disclose real
secret/token/cookie values; use synthetic fixtures and approved test accounts.

Test supported denial and recovery paths as well as success. A short-lived tool or
entertainment product does not waive privacy/authorization. Keep required security
proof separate from unrelated hardening. No production login, credential rotation,
or privilege expansion is authorized by this skill.
