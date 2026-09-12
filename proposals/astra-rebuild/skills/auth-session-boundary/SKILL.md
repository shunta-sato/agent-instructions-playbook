---
name: auth-session-boundary
description: "Use when authentication, session lifetime, token storage or refresh behavior changes; not for unrelated endpoint edits."
---

# Authentication and session boundaries

Identify actual actors, trusted components, token audiences, storage locations and
session/refresh ownership. Inspect expiry, revocation, concurrent refresh, replay,
logout, retry behavior and cross-account isolation where changed.

Use non-production fixtures and redact credentials in logs and evidence. Do not
read or copy real secret values for an inventory. A refreshed token must not turn
an authorization failure into a silent success, and a transient outage must not
silently grant access. Preserve server-side authority and supported session rules.

Verify realistic failure paths and recovery. Resolve scope and identity decisions
from the actual product, not an invented universal token lifetime. Report the
verified boundary and residual uncertainty without a mandatory security workbook.
