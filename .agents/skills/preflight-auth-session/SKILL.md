---
name: preflight-auth-session
description: "Preflight auth, OAuth, refresh token, session, JWT, cookie, CSRF, login redirect, token logging. Use before auth/session/security-sensitive implementation or multi-agent investigation."
metadata:
  short-description: Auth/session preflight
  requires:
    - references/auth-session-reference.md
---

# Preflight Auth Session

## Purpose

Prepare auth/session work before implementation starts. Extract auth invariants,
first docs/files, targeted tests, approvals, reviewers, and a handoff fragment
for `preflight-engineering` to merge into its final output.

This skill does not implement product fixes, read secret values, edit generated
clients, run auth flows against production, or change runtime configuration.

## How to use

1. Confirm the trigger reason.
   - Use for OAuth, refresh token, JWT, cookie, CSRF, session middleware,
     login redirect, token logging, route guard, or auth error-shape preflight.
   - Skip when AGENTS/context/test routing are already current and the request is
     ordinary implementation.

2. Inspect auth surfaces without reading secrets.
   - Auth service directories.
   - Session middleware.
   - Token exchange and refresh-token expiry paths.
   - Error mapping and public auth error shape.
   - Frontend auth redirect and route guards.
   - Auth tests.
   - API compatibility docs.
   - Logging and audit paths.

3. Extract auth invariants.
   - `AUTH-LOG: Never log tokens, cookies, authorization headers, or credentials.`
   - `AUTH-EXPIRED-REFRESH: Expired refresh tokens must not become generic 500s.`
   - `AUTH-REDIRECT: Identify login redirect entry points before changing flow.`
   - `AUTH-ERROR-MAP: Confirm auth-domain error mapping before implementation.`
   - `API-SHAPE: Do not change public auth error shapes without explicit approval.`
   - `GENERATED-CLIENT: Do not manually edit generated API clients.`

4. Return the common output contract from `preflight-domain-template`.
   - Include confirmed facts, inferred facts, and unknowns separately.
   - Propose `.agent/ctx/auth.md`, `services/auth/AGENTS.md`, or
     `apps/web/AGENTS.md` auth fragments only when the repository shape supports them.
   - Keep root `AGENTS.md` changes compact.

## Reference routing

- Use `references/auth-session-reference.md` for inspection checklist, output
  examples, and handoff fragment wording.

## Self-review

- No token, cookie, credential, or authorization header value was read or copied.
- Login redirect and route-guard entry points are identified or marked unknown.
- Auth public error-shape compatibility is preserved or marked for approval.
- Targeted auth test commands are confirmed or explicitly unknown.

## Output expectation

- Return the common output contract from `preflight-domain-template`, filled for the auth/session domain.
- Include the six auth invariants (`AUTH-LOG`, `AUTH-EXPIRED-REFRESH`, `AUTH-REDIRECT`, `AUTH-ERROR-MAP`, `API-SHAPE`, `GENERATED-CLIENT`) verbatim when applicable, or state why one does not apply.
- Separate confirmed facts, inferred facts, and unknowns.
- Propose `.agent/ctx/auth.md` or nested `AGENTS.md` auth fragments only when the repository shape supports them.
