# Auth Session Preflight Reference

## First Docs

- Auth architecture or login-flow docs.
- API compatibility docs for auth endpoints.
- Security/logging policy docs.
- Frontend routing or route-guard docs.

## First Files

- `services/auth/**`
- `src/auth/**`
- `middleware/session*`
- `middleware/csrf*`
- `apps/web/**/auth*`
- `apps/web/**/route*guard*`
- `openapi*`, `swagger*`, or generated client ownership docs.
- `tests/**/auth*`, `tests/**/session*`, `tests/**/csrf*`

## Example Domain Invariants

- `AUTH-LOG: Never log tokens, cookies, authorization headers, or credentials.`
- `AUTH-EXPIRED-REFRESH: Expired refresh tokens must map to the documented auth error, not a generic 500.`
- `AUTH-REDIRECT: Preserve the login redirect entry point and return-to behavior unless explicitly changed.`
- `AUTH-CSRF: Identify CSRF token creation, validation, and failure response before changing session flow.`
- `API-SHAPE: Public auth error payloads require compatibility review before changing.`
- `GENERATED-CLIENT: Regenerate clients through the documented path; do not hand-edit generated files.`

## Example Output Fragments

### `.agent/ctx/auth.md` Proposal

```markdown
## Domain

- Auth/session.

## Invariants

- AUTH-LOG: Never log tokens, cookies, authorization headers, or credentials.
- AUTH-EXPIRED-REFRESH: Expired refresh tokens must use the documented auth error mapping.

## First Files

- `services/auth/` — token exchange and refresh handling.
- `apps/web/` — login redirect and route guards.

## Test Routing

- `<auth test command>` — refresh-token expiry and login redirect regression tests.
```

### Nested `AGENTS.md` Proposal

```markdown
# Auth Agent Notes

- AUTH-LOG: Never log tokens, cookies, authorization headers, or credentials.
- API-SHAPE: Public auth error payloads require explicit compatibility approval.
- GENERATED-CLIENT: Do not manually edit generated API clients.
```

### Handoff Fragment

```markdown
## Domain: auth/session

- Preserve auth logging, error-shape, generated-client, and redirect invariants.
- Start with `<auth docs>` and `<auth service/frontend files>`.
- Run `<auth targeted tests>` before final gate, or mark targeted auth tests unknown.
```
