# OAuth Refresh Token Dry Run

Use this example to check whether `preflight-engineering` produces concrete, auditable output for an auth task.

## User Request

```text
Issue AUTH-1841 should be fixed.

When an OAuth refresh token expires, the frontend should redirect to login.
It currently shows a 500 error page.

Constraints:
- Preserve public API compatibility.
- Follow auth middleware design.
- Add regression coverage.
- Keep the diff minimal.
- Use subagents for root-cause investigation, test review, and safety review.
```

## Expected Preflight Result Shape

```markdown
# Preflight result

## Summary

Full preflight is required because the task touches auth/session behavior, public API compatibility, frontend redirect behavior, regression tests, and subagent coordination.

## Repository readiness score

- AGENTS.md: needs auth quick map
- Agent context docs: needs `.agent/ctx/auth.md`, `.agent/ctx/api.md`, `.agent/ctx/test.md`
- Skill routing: needs auth, frontend redirect, API compatibility, test, and token safety routes
- Test routing: backend auth, web auth, API compatibility
- Safety invariants: secret logging and public API boundaries must be explicit
- Prompt caching readiness: keep auth maps stable; keep issue logs out of prefix
- Subagent readiness: use read-only investigation and read-only post-patch review

## Proposed file changes

| File | Action | Purpose |
| --- | --- | --- |
| `AGENTS.md` | update | Add compact auth work quick map and hard rules |
| `services/auth/AGENTS.md` | create/update | Local auth middleware invariants |
| `apps/web/AGENTS.md` | create/update | Login redirect and route guard invariants |
| `.agent/ctx/auth.md` | create | Auth entry points, invariants, and tests |
| `.agent/ctx/api.md` | create | Public API compatibility map |
| `.agent/ctx/test.md` | create | Targeted test routing |
| `.agent/maps/skills.md` | create | Skill routing map |

## Key invariants

- Expired refresh tokens map to auth-domain errors, not generic 500.
- Login redirects go through `apps/web/src/auth/redirect.ts`.
- Do not edit generated API clients directly.
- Do not log tokens, cookies, authorization headers, refresh tokens, or credentials.
- Do not change public API error shapes without explicit approval.

## Work routing map

| Task phrase | First map | First files | Skills | Targeted tests |
| --- | --- | --- | --- | --- |
| OAuth / refresh token / session expiry | `.agent/ctx/auth.md` | `services/auth/src/token-exchange.ts`, `apps/web/src/auth/redirect.ts` | `$auth-debugging`, `$frontend-auth-redirect`, `$api-compat-review` | `pnpm --filter @acme/auth test`, `pnpm --filter @acme/web test -- auth`, `pnpm api:compat` |

## Subagent plan

### Phase 1: read-only investigation

1. Backend auth explorer
   - Scope: token exchange, middleware, error mapping
   - Output: root-cause candidates and files to inspect

2. Frontend redirect explorer
   - Scope: auth redirect and route guard flow
   - Output: expected redirect path and regression test locations

3. API/security reviewer
   - Scope: public API shape and token exposure risk
   - Output: compatibility and logging risks

### Phase 2: main-thread implementation

- Main agent synthesizes reports, implements the minimal fix, and runs targeted tests.

### Phase 3: read-only post-patch review

- API/security reviewer checks response shape and secret logging.
- Test reviewer checks regression coverage.

## Cache readiness check

- Root and nested `AGENTS.md` contain stable guidance only.
- Issue logs and test output stay out of the stable prefix.
- Shared subagent context precedes worker-specific scopes.

## Development commander handoff prompt

Use root `AGENTS.md`, auth context maps, the auth skill routes, and the subagent plan above. Preserve public API compatibility, do not log credentials or tokens, keep the patch minimal, run targeted auth/web/API compatibility tests first, and report remaining risks.
```
