# Workflow Contract Review

## Scope

- PR / branch: `codex/skill-behavior-eval-validator`
- Workflow surfaces:
  - `scripts/validate_skill_behavior_evals.py`
  - `Makefile`
  - `.github/workflows/agent-index.yml`
  - `evals/skill-behavior/quality-gate.json`
- Generated artifacts: none.

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| behavior seed | `evals/skill-behavior/quality-gate.json` | repository maintainers | validator | Explicit path; no latest/newest inference. |
| local skill names | `.agents/skills/*/SKILL.md` | repository skills | validator | Skill field must reference an existing skill name. |
| local verification | `make lint`, `make test-integration`, `make verify` | Makefile | agents and maintainers | Behavior validator is called directly by target name. |
| CI verification | `.github/workflows/agent-index.yml` | GitHub Actions | PR checks | Behavior validator is a named step. |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| validate behavior evals | controller repo root | `python3 scripts/validate_skill_behavior_evals.py` | Python 3 stdlib | stdout success count or error bullets | stop on non-zero exit |
| lint chain | controller repo root | `make lint` | Python 3, make | all lint validators pass | stop on non-zero exit |
| integration chain | controller repo root | `make test-integration` | Python 3, make, git | validator/report/index checks pass | stop on non-zero exit |
| verify chain | controller repo root | `make verify` | Python 3, make, git | canonical verification passes | stop on non-zero exit |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| repository maintainers | behavior eval JSON | `validate_skill_behavior_evals.py` | file under explicit `evals/skill-behavior` directory | pass |
| repository skills | skill frontmatter names | `validate_skill_behavior_evals.py` | top-level `skill` field matches an existing skill name | pass |
| validator | process exit status | Makefile and CI | zero means schema-valid; non-zero blocks verification | pass |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | not applicable | not applicable | pass |
| workflow id | `skill-behavior` eval directory | validator default `evals/skill-behavior` | pass |
| target id / class | not applicable | not applicable | pass |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| behavior eval validation | controller repo root | Makefile/CI repo checkout | pass |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| Python script | repository `scripts/` | `python3 scripts/validate_skill_behavior_evals.py` | Python 3 stdlib available like existing validators | `python3 -m py_compile scripts/*.py` | pass |

## Forbidden fallback checks

- filename-order artifact selection: not used.
- mtime/latest/newest artifact inference: not used.
- stale prompt fallback: not used.
- raw co-presence as causal evidence: not used; schema references explicit skill names and case fields.

## Claim boundaries

- Workflow authority artifacts: validator proves JSON schema and local skill-name references only.
- Validation artifacts: command success/failure from validator, Makefile, and CI.
- Measurement artifacts: none.
- Blocked claims: no model behavior correctness, model routing quality, generated-agent correctness, or prompt-grading accuracy is claimed.

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
| none | none | No blocking findings. | none |

## Decision

submit
