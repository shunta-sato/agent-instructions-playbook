# Workflow Contract Review

## Scope

- PR / branch: https://github.com/shunta-sato/agent-instructions-playbook/pull/67 / `codex/review-branch-completion-skills`
- Workflow surfaces:
  - `.agents/skills/requesting-code-review/SKILL.md`
  - `.agents/skills/receiving-code-review/SKILL.md`
  - `.agents/skills/branch-completion/SKILL.md`
  - `evals/skill-triggers/review-branch-completion.json`
  - generated `AGENTS.md` Agent Index and README skill catalog
- Generated artifacts:
  - `AGENTS.md` generated Agent Index
  - `README.md` generated skill catalog

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| Skill source | `.agents/skills/*/SKILL.md` | PR author | `generate_agent_index.py`, `validate_skills.py`, agents | Source of truth for trigger metadata and body instructions. |
| Trigger eval seed | `evals/skill-triggers/review-branch-completion.json` | PR author | `validate_skill_trigger_evals.py` | References skill names by exact catalog identity. |
| Generated index/catalog | `python3 scripts/generate_agent_index.py --write` | generator | `AGENTS.md`, `README.md` readers | Generated from `.agents/skills`; no hand-edited generated entries. |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| Validate skills | repo root | `python3 scripts/validate_skills.py` | Python 3 | validation output | Stop on failure. |
| Validate trigger evals | repo root | `python3 scripts/validate_skill_trigger_evals.py` | Python 3 | validation output | Stop on failure. |
| Regenerate index/catalog | repo root | `python3 scripts/generate_agent_index.py --write` | Python 3 | `AGENTS.md`, `README.md` generated blocks | Continue to check mode. |
| Check generated index/catalog | repo root | `python3 scripts/generate_agent_index.py --check` | Python 3 | up-to-date check | Stop on failure. |
| Canonical verification | repo root | `make verify` | Make, Python 3 | verification output | Stop on failure. |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| Skill source files | skill names in frontmatter | trigger eval validator | `should_trigger` / `should_not_trigger` names match `.agents/skills/*/SKILL.md` names | OK: `validate_skill_trigger_evals.py` passed. |
| Skill source files | short descriptions and paths | Agent Index / README catalog | generated entries reflect exact source skill names and paths | OK: `generate_agent_index.py --check` passed. |
| Trigger eval seed | case ids and expected skill names | trigger eval validator | unique case ids; no unknown skill names; no trigger overlap | OK: `validate_skill_trigger_evals.py` passed. |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | not applicable | not applicable | No run ledger or target validation artifacts in scope. |
| workflow id | review lifecycle skill workflow | Agent-facing skill users and trigger eval seed | Stable by exact skill names. |
| target id / class | not applicable | not applicable | No target-local workflow in scope. |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| Skill/eval validation | controller repo root | controller repo root | OK. |
| Generated index/catalog check | controller repo root | controller repo root | OK. |
| Branch completion skill guidance | agent controller workspace | agent controller workspace | OK; no target-local commands introduced. |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| repo validation scripts | repository `scripts/` | `python3 scripts/<name>.py` | Python 3 available through canonical commands | `make verify` | OK: canonical verification passed. |

## Forbidden fallback checks

- filename-order artifact selection: not introduced.
- mtime/latest/newest artifact inference: not introduced.
- stale prompt fallback: not introduced.
- raw co-presence as causal evidence: not introduced.

## Claim boundaries

- Workflow authority artifacts: new skill bodies and trigger eval seed only define agent workflow expectations.
- Validation artifacts: validator output proves schema/catalog consistency, not review quality or merge safety in every repository.
- Measurement artifacts: none.
- Blocked claims: no claim that GitHub automation, CI policy, or destructive cleanup is universally safe.

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
|  |  |  |  |

## Decision

submit
