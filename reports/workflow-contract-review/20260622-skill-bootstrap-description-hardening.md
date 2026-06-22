# Workflow Contract Review

## Scope

- PR / branch: `codex/skill-bootstrap-description-hardening`
- Workflow surfaces:
  - `AGENTS.md` bootstrap rules for Agent Index inspection, explicit skill loading, `dev-workflow`, `quality-gate`, and subagent briefs.
  - `.agents/bootstrap/using-playbook.md` helper guidance.
  - `.agents/skills/*/SKILL.md` frontmatter descriptions adjusted toward trigger-only wording.
  - `scripts/validate_skills.py` description-style warnings.
  - `scripts/report_skill_inventory.py` description trigger-only flags in inventory output.
- Generated artifacts:
  - No generated Agent Index or generated custom agents are changed in this PR.
  - Inventory output remains generated on demand by `scripts/report_skill_inventory.py`.

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| Bootstrap rules | `AGENTS.md` | Repository maintainers | Codex, Copilot CLI / agent mode, reviewers | Rules that must always apply remain in root instructions. |
| Bootstrap rationale | `.agents/bootstrap/using-playbook.md` | Repository maintainers | Agents and humans needing examples/rationale | Explicitly not a special auto-load location. |
| Skill trigger metadata | `.agents/skills/*/SKILL.md` frontmatter `description` | Skill authors | Agent skill selectors, validation scripts | Descriptions are trigger-only summaries; procedures remain in bodies/references/templates. |
| Metadata validation | `python3 scripts/validate_skills.py` | Validation script | `make lint`, `make verify`, maintainers | Description style is warning-only in this PR. |
| Inventory report | `python3 scripts/report_skill_inventory.py --check --format text` | Inventory script | `make analysis`, `make verify`, maintainers | Adds `description_trigger_only_flags` without changing error semantics. |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| skill validation | controller repo root | `python3 scripts/validate_skills.py` | Python 3 | stdout validation result and optional warning list | stop on metadata/layout errors; continue on description warnings |
| skill inventory | controller repo root | `python3 scripts/report_skill_inventory.py --check --format text` | Python 3 | stdout inventory table and warning list | stop on inventory errors; continue on warning-only flags |
| agent index check | controller repo root | `python3 scripts/generate_agent_index.py --check` | Python 3 | no output when current | stop on generated index drift |
| canonical verification | controller repo root | `make verify` | Make, Python 3, git | full validation chain output | stop on any nonzero command |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| `AGENTS.md` | root bootstrap rules | agents following repository instructions | Agent Index path and skill invocation names match repository layout | pass |
| `SKILL.md` frontmatter | `description` field | `validate_skills.py`, `report_skill_inventory.py`, agent skill selectors | field name remains `description`; warnings do not alter skill names or metadata short descriptions | pass |
| `validate_skills.py` | warning labels | maintainers and CI logs | warning labels correspond to description-only style checks, not blocking errors | pass |
| `report_skill_inventory.py` | `description_trigger_only_flags` | inventory text/JSON consumers | flags derive from the same frontmatter descriptions as `description_length` | pass |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | repository working tree on `codex/skill-bootstrap-description-hardening` | canonical verification commands | pass |
| workflow id | skill bootstrap description hardening | ExecPlan, validation commands, PR scope | pass |
| target id / class | repository-local Agent Skills | bootstrap docs and validation scripts | pass |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| validation commands | controller repo root | controller repo root | pass |
| target-local commands | not applicable | none generated | pass |
| subagent execution | not applicable in this PR | bootstrap requires future task briefs before delegation | pass |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| local validation scripts | repository `scripts/` | `python3 scripts/*.py` via `make` | Python 3 on PATH | `make verify` | pass |
| generated custom agents | not in scope | not in scope | none | not applicable | pass |

## Forbidden fallback checks

- filename-order artifact selection: pass; no latest/newest artifact discovery is introduced.
- mtime/latest/newest artifact inference: pass; no mtime-based selection is introduced.
- stale prompt fallback: pass; bootstrap says always-applicable rules live in `AGENTS.md`, not hidden fallback prompts.
- raw co-presence as causal evidence: pass; validation consumes explicit paths and commands.

## Claim boundaries

- Workflow authority artifacts: `AGENTS.md`, `.agents/bootstrap/using-playbook.md`, `.agents/skills/*/SKILL.md`.
- Validation artifacts: `validate_skills.py` output, `report_skill_inventory.py` output, `make verify`.
- Measurement artifacts: none; this PR makes no model quality, token efficiency, runtime performance, or production-readiness claims.
- Blocked claims: model routing, run ledger, behavior evals, generated custom agents, and review/branch completion are not implemented by this PR.

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
| none | none | No contract findings. | none |

## Decision

submit
