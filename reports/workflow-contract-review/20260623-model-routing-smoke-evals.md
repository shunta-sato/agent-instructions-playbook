# Workflow Contract Review

## Scope

- PR / branch: `codex/model-routing-smoke-evals`
- Workflow surfaces:
  - `evals/model-routing/core.json`
  - `scripts/validate_model_routing_evals.py`
  - `Makefile`
  - `.github/workflows/agent-index.yml`
- Generated artifacts: none.

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| routing config | `.agents/model-routing/*.yml` | repository maintainers | resolver and eval validator | Explicit paths; no generated catalog or lockfile required. |
| model-routing evals | `evals/model-routing/core.json` | repository maintainers | `scripts/validate_model_routing_evals.py` | Explicit directory; no latest/newest inference. |
| resolver behavior | `scripts/resolve_model_route.py` | repository script | eval validator | Eval validator calls resolver directly with fixture catalogs. |
| local verification | `make lint`, `make test-integration`, `make verify` | Makefile | agents and maintainers | Validator is called by explicit target lines. |
| CI verification | `.github/workflows/agent-index.yml` | GitHub Actions | PR checks | Validator is a named CI step. |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| validate model-routing evals | controller repo root | `python3 scripts/validate_model_routing_evals.py` | Python 3 stdlib | stdout success count or error bullets | stop on non-zero exit |
| lint chain | controller repo root | `make lint` | Python 3, make | all lint validators pass | stop on non-zero exit |
| integration chain | controller repo root | `make test-integration` | Python 3, make, git | validator/report/index checks pass | stop on non-zero exit |
| verify chain | controller repo root | `make verify` | Python 3, make, git | canonical verification passes | stop on non-zero exit |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| routing config | task classes and profiles | model-routing eval validator | eval `task_class` and `expected_capability_profile` match config | pass |
| eval catalog fixtures | candidate statuses/profiles/smoke_eval | resolver | profile names and status vocabulary match resolver policy | pass |
| resolver | result dict | model-routing eval validator | expected selected flag, selected model, selection profile, and fallback reasons match | pass |
| validator | process exit status | Makefile and CI | zero means schema and resolver expectations pass | pass |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | not applicable | not applicable | pass |
| workflow id | `model-routing` eval directory | validator default `evals/model-routing` | pass |
| target id / class | eval `task_class` | resolver task class | pass |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| model-routing eval validation | controller repo root | Makefile/CI repo checkout | pass |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| Python script | repository `scripts/` | `python3 scripts/validate_model_routing_evals.py` | Python 3 stdlib and local imports | `python3 -m py_compile scripts/*.py` | pass |

## Forbidden fallback checks

- filename-order artifact selection: not used.
- mtime/latest/newest artifact inference: not used.
- stale prompt fallback: not used.
- raw co-presence as causal evidence: not used; evals assert resolver outputs from explicit catalog fixtures.

## Claim boundaries

- Workflow authority artifacts: eval schema and resolver expectation checks only.
- Validation artifacts: validator, Makefile, and CI command results.
- Measurement artifacts: none.
- Blocked claims: no real model quality, cost, latency, generated catalog freshness, generated-agent correctness, or production model-routing readiness is claimed.

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
| none | none | No blocking findings. | none |

## Decision

submit
