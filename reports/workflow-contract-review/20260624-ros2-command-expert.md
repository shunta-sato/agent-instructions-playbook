# Workflow Contract Review

## Scope

- PR / branch: branch `ros2-command-expert`
- Workflow surfaces:
  - `.agents/skills/ros2-command-expert/SKILL.md`
  - `.agents/skills/ros2-command-expert/references/*.md`
  - `evals/skill-triggers/ros2-command-expert.json`
  - generated `AGENTS.md` Agent Index
  - generated `README.md` skill catalog
- Generated artifacts:
  - `AGENTS.md`
  - `README.md`

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| Source archive | `ros2-command-expert.zip` | user-provided archive | extraction step | Archive is the input artifact; not committed as the repo source of truth. |
| Skill source | `.agents/skills/ros2-command-expert/SKILL.md` and references | extraction plus metadata normalization | agents, validators, generated catalog | Skill folder is committed as the repo source of truth. |
| Trigger eval seed | `evals/skill-triggers/ros2-command-expert.json` | branch change | `validate_skill_trigger_evals.py` | References exact skill names. |
| Catalog generation | `python3 scripts/generate_agent_index.py --write` | generator | `AGENTS.md`, `README.md` | Generated from `.agents/skills/*/SKILL.md`. |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| Extract archive | repo root | `unzip -q ros2-command-expert.zip -d .agents/skills` | zip/unzip | `.agents/skills/ros2-command-expert/` | Stop on failure. |
| Validate skills | repo root | `python3 scripts/validate_skills.py` | Python 3 | validation output | Stop on failure. |
| Validate trigger evals | repo root | `python3 scripts/validate_skill_trigger_evals.py` | Python 3 | validation output | Stop on failure. |
| Generate catalog | repo root | `python3 scripts/generate_agent_index.py --write` | Python 3 | `AGENTS.md`, `README.md` | Continue to check mode. |
| Canonical verification | repo root | `make verify` | Make, Python 3 | verification output | Stop on failure. |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| Skill frontmatter | `name: ros2-command-expert` | trigger eval validator | `should_trigger` / `should_not_trigger` uses exact skill name | OK; `python3 scripts/validate_skill_trigger_evals.py` passed. |
| Skill frontmatter | `metadata.short-description` | generated catalog | `AGENTS.md` and `README.md` include the skill path and short description | OK; `python3 scripts/generate_agent_index.py --check` passed. |
| Trigger eval seed | `ros2-command-expert.json` | trigger eval validator | unique case ids and known skills | OK; `python3 scripts/validate_skill_trigger_evals.py` passed. |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | not applicable | not applicable | No run ledger artifact in scope. |
| workflow id | `ros2-command-expert` skill workflow | skill catalog and eval seed | Exact skill name is the workflow identity. |
| target id / class | ROS 2 Humble CLI guidance | skill body/references | The skill limits exact source evidence to Humble unless installed help is verified. |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| Repo extraction and validation | controller repo root | controller repo root | OK. |
| Skill runtime guidance | target ROS shell when a user applies the skill | instructed by skill preflight | OK; no command execution is performed by this branch. |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| repo validation scripts | repository `scripts/` | `python3 scripts/<name>.py` | Python 3 available per `COMMANDS.md` | `make verify` | OK; canonical verification passed. |
| ROS 2 CLI at skill use time | user target environment | `ros2` | skill instructs `command -v ros2` and environment checks | cached preflight in skill | OK as guidance; not executed by this branch. |

## Forbidden fallback checks

- filename-order artifact selection: not introduced.
- mtime/latest/newest artifact inference: not introduced.
- stale prompt fallback: not introduced.
- raw co-presence as causal evidence: not introduced.

## Claim boundaries

- Workflow authority artifacts: committed skill body, references, trigger eval, and generated catalogs.
- Validation artifacts: repo validators prove metadata/catalog/eval consistency only.
- Measurement artifacts: none.
- Blocked claims: the skill explicitly blocks real-time, zero-copy, transport, and production behavior claims from CLI source alone.

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
|  |  |  |  |

## Decision

submit
