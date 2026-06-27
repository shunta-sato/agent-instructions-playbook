# Workflow Contract Review: Preflight Critical Domain Skills

## Decision

submit

## Workflow surfaces reviewed

- `.agents/skills/preflight-auth-session/SKILL.md`
- `.agents/skills/preflight-auth-session/references/auth-session-reference.md`
- `.agents/skills/preflight-api-compat/SKILL.md`
- `.agents/skills/preflight-api-compat/references/api-compat-reference.md`
- `.agents/skills/preflight-db-migration/SKILL.md`
- `.agents/skills/preflight-db-migration/references/db-migration-reference.md`
- `evals/skill-triggers/preflight-auth-session.json`
- `evals/skill-triggers/preflight-api-compat.json`
- `evals/skill-triggers/preflight-db-migration.json`
- `.agents/skills/preflight-engineering/SKILL.md`
- `AGENTS.md`
- `README.md`
- `plans/20260627-preflight-operationalization.md`

## Source-of-truth chain

| Stage | Upstream artifact | Downstream consumer | Identity / authority |
| --- | --- | --- | --- |
| Domain skill trigger | Each `preflight-*` domain `SKILL.md` description | Codex skill router | Explicit skill name and description |
| Domain workflow | Each domain `SKILL.md` body | Agent running domain preflight | Common output contract from `preflight-domain-template` |
| Domain examples | Each domain reference file | Domain preflight output proposals | Explicit `references/<domain>-reference.md` path |
| Trigger evals | `evals/skill-triggers/preflight-*.json` | Eval validator | Skill names validated against local catalog |
| Orchestrator routing | `preflight-engineering/SKILL.md` table | `preflight-engineering` users | Implemented first three domain rows no longer marked candidate |
| Generated index | `AGENTS.md`, `README.md` | Agents and humans | Updated by `python3 scripts/generate_agent_index.py --write` |

## Generated argv replay

| step_id | execution_location | command_argv | required environment | expected artifact kind | expected artifact path | continue_on / stop_on | claim gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| validate-skills | repo root | `python3 scripts/validate_skills.py` | Python 3 stdlib | validation output | stdout | stop on non-zero exit | Skill metadata/layout only |
| validate-trigger-evals | repo root | `python3 scripts/validate_skill_trigger_evals.py` | Python 3 stdlib | eval validation output | stdout | stop on non-zero exit | Eval schema and skill-name references only |
| validate-index | repo root | `python3 scripts/generate_agent_index.py --check` | Python 3 stdlib | index check output | stdout | stop on non-zero exit | Generated index is current |
| verify | repo root | `make verify` | Python 3 stdlib and make | canonical verification output | stdout | stop on non-zero exit | Repository validation only |

## Artifact producer/consumer consistency

| Producer step | Produced artifact | Consumer step | Consumer argv | Identity fields that must match |
| --- | --- | --- | --- | --- |
| Domain `SKILL.md` files | skill metadata and common workflow | skill router / agents | `python3 scripts/validate_skills.py` | `name`, path, description |
| Domain eval files | trigger cases | eval validator | `python3 scripts/validate_skill_trigger_evals.py` | `should_trigger`, `should_not_trigger`, case ids |
| Domain references | examples and invariant wording | domain skill users | explicit reference path in each `SKILL.md` | first docs/files, invariants, handoff fragment |
| Generated index | index rows | `generate_agent_index.py --check` | explicit index check command | skill name/path/short description |

## Run-set / target / workflow identity consistency

- Workflow identity: first critical domain preflight skill rollout.
- Target identity: repository-local skill catalog under `.agents/skills`.
- Run-set identity: explicit validator commands and PR #78 branch contents, not newest files.
- Consistency status: pass.

## Controller / target-local execution-location table

| Step | Controller location | Target-local location | Status |
| --- | --- | --- | --- |
| Domain preflight skill use | Repository under review | Not applicable | pass |
| Product implementation | Not emitted by these skills | Not applicable | pass |
| Migration/deploy/backfill execution | Explicitly forbidden by relevant skills | Not applicable | pass |

## Deployment/runtime discovery assumptions

- Domain skills are Markdown instruction artifacts only.
- No external services, package installs, database connections, deployments, or generated-client writes are required.
- Repository-local validators are sufficient for skill metadata, eval schema, and index integrity.

## Forbidden fallback checks

- No latest/newest artifact discovery.
- No mtime-based selection.
- No stale prompt fallback.
- No implicit claim that domain preflight output authorizes implementation, migration, deployment, or generated-client editing.

## Claim boundary checks

- Domain skills produce preflight proposals and handoff fragments, not product changes.
- Auth skill forbids reading/copying token, cookie, credential, or authorization header values.
- API compatibility skill forbids manual generated-client editing.
- DB migration skill forbids migration, seed, backfill, deploy, and production DB execution during preflight.
- Trigger evals intentionally include negative cases for already-current context to avoid over-triggering.

## Findings

0 findings.
