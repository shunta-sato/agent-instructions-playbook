# Workflow Contract Review

## Scope

- PR / branch: `codex/model-routing-foundation`
- Workflow surfaces:
  - `.agents/model-routing/task-classes.yml` task class to capability profile routing.
  - `.agents/model-routing/capability-profiles.yml` model-agnostic capability profile and fallback chain definitions.
  - `.agents/model-routing/resolver-policy.yml` external catalog policy, selectable statuses, excluded statuses, and fallback reasons.
  - `.agents/model-routing/risk-gates.yml` route risk-gate labels and minimum verification expectations.
  - `.agents/model-routing/prompt-detail-levels.md` prompt detail contracts for delegated task briefs.
  - `scripts/resolve_model_route.py` task-class resolver CLI.
  - `scripts/validate_model_routing.py` repository validation command.
  - `Makefile` canonical validation chain.
- Generated artifacts:
  - No generated model catalog, route lockfile, custom agent, run ledger, or prompt artifact is introduced.
  - Routing files are author-maintained, JSON-compatible YAML parsed by stdlib `json`.

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| Task classes | `.agents/model-routing/task-classes.yml` | Repository maintainers | `resolve_model_route.py`, future agent generators | Stores task class, profile, prompt detail, risk gate, success criteria, and escalation profile. |
| Capability profiles | `.agents/model-routing/capability-profiles.yml` | Repository maintainers | `resolve_model_route.py`, `validate_model_routing.py` | Stores model-agnostic capability requirements and fallback profile chain. |
| Resolver policy | `.agents/model-routing/resolver-policy.yml` | Repository maintainers | `resolve_model_route.py`, `validate_model_routing.py` | Concrete model IDs are not stored in routing files; candidates come from an external catalog. |
| Risk gates | `.agents/model-routing/risk-gates.yml` | Repository maintainers | future route consumers, reviewers | Defines route risk labels and minimum verification expectations. |
| Prompt detail contract | `.agents/model-routing/prompt-detail-levels.md` | Repository maintainers | humans and future generator code | Defines compact, normal, and strict prompt brief detail levels. |
| Route resolution | `python3 scripts/resolve_model_route.py <task_class>` | Resolver script | agents, maintainers, future generated workflows | Emits selected status, selected model only from an external catalog, selected profile, and fallback reasons. |
| Routing validation | `python3 scripts/validate_model_routing.py` | Validation script | `make lint`, `make verify`, CI | Validates references, forbidden model fields, prompt detail sections, and resolver smoke behavior. |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| compile scripts | controller repo root | `python3 -m py_compile scripts/*.py` | Python 3 | bytecode compile success | stop on syntax/import error |
| model routing validation | controller repo root | `python3 scripts/validate_model_routing.py` | Python 3 | validation summary with task/profile counts | stop on config or resolver invariant error |
| no-catalog resolver smoke | controller repo root | `python3 scripts/resolve_model_route.py unit_test_single_case --format text` | Python 3 | `selected: false` and `catalog_not_provided` | stop on nonzero command |
| external-catalog resolver smoke | controller repo root | `python3 scripts/resolve_model_route.py unit_test_single_case --catalog <temp> --format text` | Python 3, temp JSON catalog | selectable candidate chosen, excluded candidate reason recorded | stop on nonzero command |
| canonical verification | controller repo root | `make verify` | Make, Python 3, git | full verification chain output | stop on nonzero command |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| `task-classes.yml` | task class names and references | resolver and validator | every profile, risk gate, prompt detail, and escalation reference exists | pass |
| `capability-profiles.yml` | fallback profile names | resolver and validator | fallback chain references defined profiles and avoids cycles by visited set | pass |
| `resolver-policy.yml` | selectable/excluded status policy | resolver and validator | selectable and excluded status sets do not overlap | pass |
| external catalog | `models[]` candidate list | resolver only | concrete candidate IDs enter only through explicit `--catalog` input | pass |
| `validate_model_routing.py` | validation result | `make lint`, `make test-integration`, `make verify` | canonical commands now include model routing validation | pass |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | repository working tree on `codex/model-routing-foundation` | targeted smoke and `make verify` | pass |
| workflow id | model routing foundation | ExecPlan, workflow-contract report, PR scope | pass |
| target id / class | repository-local agent routing artifacts | resolver and validator scripts | pass |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| validation commands | controller repo root | controller repo root | pass |
| target-local commands | not applicable | none generated | pass |
| generated delegated agent execution | not in scope | none generated | pass |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| routing config | repository `.agents/model-routing/` | loaded from repo root by resolver/validator | files are JSON-compatible YAML | `python3 scripts/validate_model_routing.py` | pass |
| local validation scripts | repository `scripts/` | `python3 scripts/*.py` via `make` | Python 3 stdlib only | `python3 -m py_compile scripts/*.py` | pass |
| external model catalog | caller-supplied JSON file | `--catalog <path>` | explicit path from caller, no latest/newest discovery | targeted resolver smoke with temp catalog | pass |

## Forbidden fallback checks

- filename-order artifact selection: pass; resolver accepts only explicit task class and optional explicit catalog path.
- mtime/latest/newest artifact inference: pass; no directory scan chooses a catalog by timestamp.
- stale prompt fallback: pass; prompt detail levels are named contracts, not hidden fallback prompts.
- raw co-presence as causal evidence: pass; route selection requires explicit profile match, candidate status, and smoke eval.
- rumored/unavailable model selection: pass; validator smoke verifies unavailable and rumored candidates are excluded.

## Claim boundaries

- Workflow authority artifacts: `.agents/model-routing/*`, `scripts/resolve_model_route.py`, `scripts/validate_model_routing.py`, `Makefile`.
- Validation artifacts: targeted resolver smoke, `validate_model_routing.py`, `make verify`.
- Measurement artifacts: none; this PR does not claim model quality, token savings, latency, cost, or production readiness.
- Blocked claims: generated model catalog, route lockfile, generated custom agents, behavior evals, run ledger, and delegated-run quality-gate evidence are not implemented by this PR.
- Concrete model IDs: prohibited in routing definitions; placeholder IDs appear only inside resolver smoke catalogs and caller-supplied temp catalogs.

## Implementation Economy Evidence

Complexity Budget:

- Changed files target: 10 tracked files or fewer.
- New classes/modules target: 0 classes, 2 scripts, 1 config directory.
- New helpers/wrappers/adapters target: small local helpers only.
- New indirection layers target: 0.
- Rough production/test line budget: initially under 500 net lines; actual staged implementation/config is larger because the PR includes schema validation, resolver smoke coverage, and static routing definitions.
- Complexity decision: accept the larger line count because the implementation remains stdlib-only, class-free, and tied into one canonical verification path.

Post-Implementation Economy Audit:

| New abstraction | Justification | Decision | Evidence |
| --- | --- | --- | --- |
| `.agents/model-routing/` | Gives later generated catalogs, lockfiles, and agents a stable model-agnostic contract. | keep | Validator loads and cross-checks every artifact. |
| `resolve_model_route.py` | Separates route resolution from repository validation so future callers can use the CLI directly. | keep | Targeted smoke covers no-catalog, direct catalog selection, and fallback profile selection. |
| `validate_model_routing.py` | Keeps schema/reference checks in canonical verification without coupling them to resolver output rendering. | keep | `make verify` runs the validator through lint and integration targets. |

## Function Boundary Evidence

| Function / module | Semantic neighbors | Decision | Rationale |
| --- | --- | --- | --- |
| `load_json_compatible_yaml` | Python stdlib `json`, routing file reads | keep local to resolver module | All current routing files share the same dependency-free parsing contract. |
| `select_candidate` | `candidate_exclusion_reason`, `profile_fallback_chain` | keep focused on one profile attempt | Avoids mixing candidate filtering with fallback traversal. |
| `profile_fallback_chain` | capability profile definitions | keep separate helper | Fallback traversal is a distinct contract from candidate status/smoke validation. |
| `resolve_route` | CLI `main`, validator smoke | keep as importable boundary | Single source for task class resolution and optional external-catalog selection. |
| `validate_model_routing` | Makefile, CLI `main` | keep as validation boundary | Returns structured error list for CLI presentation and future tests. |

Ledger update: not required; this PR adds new focused artifacts and scripts without replacing an existing abstraction or staging compatibility adapters.

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
| none | none | No contract findings. | none |

## Decision

submit
