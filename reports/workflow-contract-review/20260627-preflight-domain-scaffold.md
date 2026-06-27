# Workflow Contract Review: Preflight Domain Scaffold

## Decision

submit

## Workflow surfaces reviewed

- `.agents/skills/preflight-domain-template/SKILL.md`
- `.agents/skills/preflight-domain-template/references/domain-agents-template.md`
- `.agents/skills/preflight-domain-template/references/domain-ctx-template.md`
- `.agents/skills/preflight-domain-template/references/domain-handoff-fragment-template.md`
- `.agents/skills/preflight-domain-template/references/domain-trigger-eval-template.md`
- `.agents/skills/preflight-engineering/SKILL.md`
- `AGENTS.md`
- `README.md`
- `plans/20260627-preflight-operationalization.md`

## Source-of-truth chain

| Stage | Upstream artifact | Downstream consumer | Identity / authority |
| --- | --- | --- | --- |
| Domain authoring | `preflight-domain-template/SKILL.md` | Agent creating `preflight-*` domain skills | Explicit skill path and common output contract |
| Nested AGENTS proposal | `references/domain-agents-template.md` | Domain preflight output | Explicit template path; no generated latest/newest selection |
| Agent context proposal | `references/domain-ctx-template.md` | `.agent/ctx/<domain>.md` proposal | Explicit template path |
| Handoff fragment | `references/domain-handoff-fragment-template.md` | `preflight-engineering` final handoff prompt | Explicit template path |
| Trigger eval seed | `references/domain-trigger-eval-template.md` | Domain skill eval files in PR3 | Explicit template path |
| Routing table | `preflight-engineering/SKILL.md` | Orchestrator domain skill selection | Candidate status is written in the table |

## Generated argv replay

| step_id | execution_location | command_argv | required environment | expected artifact kind | expected artifact path | continue_on / stop_on | claim gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| validate-skills | repo root | `python3 scripts/validate_skills.py` | Python 3 stdlib | validation output | stdout | stop on non-zero exit | Skill metadata/layout only |
| validate-index | repo root | `python3 scripts/generate_agent_index.py --check` | Python 3 stdlib | index check output | stdout | stop on non-zero exit | Generated index is current |
| inventory-check | repo root | `python3 scripts/report_skill_inventory.py --check --format text` | Python 3 stdlib | inventory output | stdout | stop on non-zero exit | Inventory consistency only |

## Artifact producer/consumer consistency

| Producer step | Produced artifact | Consumer step | Consumer argv | Identity fields that must match |
| --- | --- | --- | --- | --- |
| Domain template skill | common output contract | Future domain skills | explicit skill/reference paths | output headings, no-implementation rules, secret/deploy/migration boundaries |
| `generate_agent_index.py --write` | `AGENTS.md`, `README.md` indexes | validators and future agents | `python3 scripts/generate_agent_index.py --check` | skill name/path/short description |
| Domain routing table | candidate domain routing rows | `preflight-engineering` users | direct table in `SKILL.md` | risk surface, candidate skill, use-when condition |

## Run-set / target / workflow identity consistency

- Workflow identity: `preflight-domain-template` authoring and orchestrator routing.
- Target identity: repository-local skill catalog under `.agents/skills`.
- Run-set identity: explicit validator commands, not newest report files.
- Consistency status: pass.

## Controller / target-local execution-location table

| Step | Controller location | Target-local location | Status |
| --- | --- | --- | --- |
| Skill/template authoring | Repository root | Not applicable | pass |
| Product implementation | Not emitted | Not applicable | pass |
| Migration/deploy execution | Not emitted | Not applicable | pass |

## Deployment/runtime discovery assumptions

- No external service or deployment runtime is required.
- Domain templates are Markdown instruction artifacts only.
- The generated skill index is updated by the repository-local script and checked by `make verify`.

## Forbidden fallback checks

- No latest/newest artifact discovery.
- No mtime-based selection.
- No stale prompt fallback.
- No implicit authority from co-present template files; `SKILL.md` links each reference explicitly.

## Claim boundary checks

- `preflight-domain-template` helps author domain preflight skills; it is not itself domain risk evidence.
- Candidate domain rows do not claim the domain skills exist yet.
- Domain preflight outputs are proposals for `preflight-engineering` to merge, not product implementation instructions.
- Trigger eval template is a seed; real domain eval files are deferred to PR3.

## Findings

0 findings.
