# Workflow Contract Review: Preflight Inspection Helpers

## Decision

submit

## Workflow surfaces reviewed

- `.agents/skills/preflight-engineering/SKILL.md`
- `.agents/skills/preflight-engineering/scripts/inspect_repo.py`
- `.agents/skills/preflight-engineering/scripts/estimate_context_size.py`
- `.agents/skills/preflight-engineering/scripts/check_agent_docs.py`
- `.agents/skills/preflight-engineering/references/repo-inspection-output-template.md`
- `evals/skill-triggers/preflight-engineering.json`
- `plans/20260627-preflight-operationalization.md`

## Source-of-truth chain

| Stage | Upstream artifact | Downstream consumer | Identity / authority |
| --- | --- | --- | --- |
| Helper invocation | Explicit script path in `preflight-engineering/SKILL.md` | Agent running preflight | Path and argv are written directly; no latest/newest discovery |
| Helper output | JSON/Markdown stdout from explicit command | Human/agent preflight summary | Output labels facts as confirmed, inferred, or unknown |
| Summary template | `references/repo-inspection-output-template.md` | `preflight-engineering` proposals | Template states collectors are not decision makers |
| Trigger eval | `evals/skill-triggers/preflight-engineering.json` | Eval validator | Skill names validated against local skill catalog |

## Generated argv replay

| step_id | execution_location | command_argv | required environment | expected artifact kind | expected artifact path | continue_on / stop_on | claim gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inspect-repo | repo root | `python3 .agents/skills/preflight-engineering/scripts/inspect_repo.py --root . --markdown` | Python 3 stdlib | Markdown collector output | stdout | stop on non-zero exit | Candidate repo facts only |
| estimate-context-size | repo root | `python3 .agents/skills/preflight-engineering/scripts/estimate_context_size.py --root .` | Python 3 stdlib | Markdown size estimate | stdout | stop on non-zero exit | Rough byte/line/token estimate only |
| check-agent-docs | repo root | `python3 .agents/skills/preflight-engineering/scripts/check_agent_docs.py --root .` | Python 3 stdlib | Markdown doc check | stdout | stop on non-zero exit | Agent-doc readiness warnings only |

## Artifact producer/consumer consistency

| Producer step | Produced artifact | Consumer step | Consumer argv | Identity fields that must match |
| --- | --- | --- | --- | --- |
| inspect-repo | stdout JSON/Markdown | preflight summary | explicit helper command from skill | `root`, path buckets, `commands.confirmed/inferred/unknown`, `risk_surfaces` |
| estimate-context-size | stdout Markdown/JSON | cache readiness review | explicit helper command from skill | file path, bytes, lines, rough token estimate |
| check-agent-docs | stdout Markdown/JSON | AGENTS/context proposal review | explicit helper command from skill | pass, warnings, human decisions |

## Run-set / target / workflow identity consistency

- Workflow identity: `preflight-engineering` helper collector workflow.
- Target identity: the repository root passed by `--root`.
- Run-set identity: explicit helper invocations, not files selected by mtime or newest path.
- Consistency status: pass.

## Controller / target-local execution-location table

| Step | Controller location | Target-local location | Status |
| --- | --- | --- | --- |
| Helper collectors | Repository root where preflight is running | Not applicable | pass |
| Migrations/deploy/tests | Not emitted by helpers | Not applicable | pass |

## Deployment/runtime discovery assumptions

- Python 3 standard library is available to run local helper scripts.
- No external services, credentials, package installs, or generated clients are required.
- Helpers print to stdout and do not write files.

## Forbidden fallback checks

- No latest/newest artifact discovery.
- No mtime-based plan or approval selection.
- No stale prompt fallback.
- No raw co-presence claim that helper output alone proves readiness.

## Claim boundary checks

- Helper success means only that candidate facts were collected.
- Helper output does not imply that AGENTS.md should be changed.
- Context-size estimates are rough byte/line/token estimates, not tokenizer-compatible measurements.
- Secret-like paths are path-only candidates and do not authorize reading secret values.

## Findings

0 findings.
