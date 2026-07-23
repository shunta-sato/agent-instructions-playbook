---
name: preflight-engineering
description: "Preflight, AGENTS.md, agent context, skill routing, test routing, subagent handoff, prompt caching readiness. Use before long-running, multi-agent, unfamiliar, high-risk, or cross-service coding tasks. Do not use for small one-file edits."
metadata:
  short-description: Preflight agent context and handoff
  resources:
    - references/agent-ctx-template.md
    - references/agents-template.md
    - references/cache-readiness-checklist.md
    - references/handoff-prompt-template.md
    - references/oauth-refresh-token-example.md
    - references/repo-inspection-output-template.md
    - references/skill-map-template.md
  commands:
    - scripts/check_agent_docs.py
    - scripts/estimate_context_size.py
    - scripts/inspect_repo.py
---

# Preflight Engineering

## Purpose

Prepare a repository for long-running agentic development before product implementation starts. Produce compact Agent-facing context, routing maps, safety invariants, test routing, subagent work plans, cache-readiness checks, and a development commander handoff prompt.

This skill prepares the work environment; it does not implement product fixes, run migrations, deploy, reveal secrets, or broaden dependencies.

## How to use

0. Decide whether preflight is needed.
   - Use lightweight preflight when one area is involved, `AGENTS.md` exists, and test routing is clear.
   - Use full preflight for multi-service work, auth/billing/security/public API/DB/infra changes, subagent work, unfamiliar repos, missing docs, missing `AGENTS.md`, or repos that agents will revisit.
   - For obvious one-file fixes, typo fixes, formatter-only changes, or already-routed small work, state why preflight is unnecessary and stop.

1. Inventory stable repository surfaces.
   - Inspect instruction files, README/CONTRIBUTING, package and lock files, CI/test config, docs, `.agent/`, `.agents/skills/`, schema files, generated-code directories, migrations, deploy config, and secret-like filename patterns.
   - Do not read secret, credential, token, cookie, or key values. Record paths and patterns only.
   - Mark facts as `confirmed`, `inferred`, or `unknown`.
   - When the repository is unfamiliar, `AGENTS.md` is missing, or docs/test routing are unknown, run the read-only helper collectors:
     - `python3 .agents/skills/preflight-engineering/scripts/inspect_repo.py --root . --markdown`
     - `python3 .agents/skills/preflight-engineering/scripts/estimate_context_size.py --root .`
     - `python3 .agents/skills/preflight-engineering/scripts/check_agent_docs.py --root .`
   - Treat helper output as candidate evidence only. The scripts collect paths, size estimates, warnings, and unknowns; they do not decide risk, rewrite `AGENTS.md`, run tests, execute migrations, deploy, or change git state.
   - Use `references/repo-inspection-output-template.md` when summarizing helper output.

2. Classify task risk.
   - Check for auth/session/token, billing/payment, public API, DB migration, security-sensitive code, production config, generated clients, multi-service work, external side effects, and dependency changes.
   - Record risk level, sensitive areas, approval needs, required reviewers, and required tests.
   - After risk classification, select applicable domain preflight skills when a risk surface needs specialist invariants or first-file routing.
   - Domain preflight skills are helpers, not replacements for this orchestrator. Merge their outputs into `AGENTS.md` proposals, `.agent/ctx` maps, skill routing, test routing, approval/reviewer notes, and the final handoff prompt.

## Domain preflight routing

| Risk surface | Domain skill | Use when |
|---|---|---|
| auth/session/token | `preflight-auth-session` | OAuth, refresh token, JWT, cookie, CSRF, login redirect |
| public API/generated client | `preflight-api-compat` | OpenAPI, GraphQL, public error shape, generated clients |
| DB/migration/persistence | `preflight-db-migration` | schema change, migration, rollback, backfill |
| security-sensitive code | `preflight-security-sensitive` (candidate) | secrets, logging, injection, SSRF, dependency risk |
| infra/deploy/runtime config | `preflight-infra-deploy` (candidate) | deploy config, IaC, env vars, production runtime |
| billing/payment | `preflight-billing-payment` (candidate) | payment flow, invoice, subscription, external money movement |

3. Extract invariants.
   - Keep safety, compatibility, generated-file, destructive-operation, approval, and test-command invariants.
   - Exclude style rules that lint or formatters already enforce.
   - Do not over-compress security, public API, secret-handling, generated-file, approval, or test-command rules.

4. Build work routing.
   - Map task phrases to first docs, first files, relevant skills, and targeted tests.
   - Prefer short, auditable paths such as `.agent/ctx/auth.md` and `.agent/maps/skills.md` before broad search.

5. Design `AGENTS.md`.
   - Keep root `AGENTS.md` as a compact, stable work contract: context entry points, hard rules, work routing, skill routing, and common commands.
   - Move area-specific rules into nested `AGENTS.md` files.
   - Do not paste long human docs, API specs, past discussions, skill bodies, issue logs, timestamps, temporary plans, or user-specific data into `AGENTS.md`.
   - Use `references/agents-template.md` when drafting or reviewing the structure.

6. Design Agent context docs.
   - Propose `.agent/ctx/*.md` and `.agent/maps/*.md` files as compact work maps, not human-facing design docs.
   - Link to long human docs from the maps instead of duplicating them.
   - Use `references/agent-ctx-template.md` for each context map.

7. Organize skill routing.
   - Inventory available skills and propose missing skills when routing gaps appear.
   - Keep `AGENTS.md` to a skill reverse index; do not paste skill bodies.
   - Use `references/skill-map-template.md` for the map.

8. Check prompt-cache readiness.
   - Separate repo-stable prefix from task-stable shared prefix.
   - Keep repo-stable instructions, schemas, output formats, and tool-order guidance before volatile run data.
   - Keep task-stable GOAL, acceptance criteria, shared constraints, and common subagent output format before worker-specific scopes.
   - Keep timestamps, request IDs, logs, grep output, test output, snippets, issue-specific notes, and worker-specific roles out of repo-stable docs and long-lived prefixes.
   - Use `references/cache-readiness-checklist.md`.

9. Plan subagent use only when it pays for itself.
   - Prefer read-only investigation first, main-thread implementation, and read-only post-patch review.
   - Avoid giving multiple subagents the same search task, the same editable files, full logs, or volatile prompt prefixes.
   - Fix shared context, constraints, and output format before invoking subagents.

10. Generate the development commander handoff prompt.
    - Include GOAL, readiness summary, relevant `AGENTS.md` files, `.agent/ctx` maps, required skills, hard constraints, subagent plan, implementation guidance, targeted test plan, post-patch review plan, and final response format.
    - Use `references/handoff-prompt-template.md`.

## Reference routing

- Use `references/agents-template.md` when drafting root or nested `AGENTS.md`.
- Use `references/agent-ctx-template.md` when drafting `.agent/ctx/*.md` or `.agent/maps/paths.md`.
- Use `references/skill-map-template.md` when mapping skill triggers and gaps.
- Use `references/cache-readiness-checklist.md` during final preflight validation.
- Use `references/repo-inspection-output-template.md` when converting helper script output into auditable preflight notes.
- Use `references/handoff-prompt-template.md` for the final commander prompt.
- Use `references/oauth-refresh-token-example.md` for a concrete dry-run pattern.

## Output expectation

```markdown
# Preflight result

## Summary

## Repository readiness score

- AGENTS.md:
- Agent context docs:
- Skill routing:
- Test routing:
- Safety invariants:
- Prompt caching readiness:
- Subagent readiness:

## Proposed file changes

| File | Action | Purpose |
| --- | --- | --- |

## Key invariants

## Work routing map

## Skill routing map

## Test routing

## Cache readiness check

## Subagent plan

## Human decisions required

## Development commander handoff prompt

## Remaining gaps
```

## Self-review

- This skill prepares the environment and does not implement product changes.
- The description can trigger implicitly for long-running or multi-agent work.
- `AGENTS.md` stays compact and stable.
- Human docs and Agent context docs stay separate.
- Skill routing is referenced, not pasted.
- A development commander handoff prompt is produced.
- Cache-readiness is checked.
- Subagents are treated as useful but token-expensive.
- Compression remains readable and auditable.
- The OAuth refresh token example remains available.
