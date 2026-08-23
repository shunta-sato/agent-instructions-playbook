# Workflow Contract Review

## Scope

- PR / branch: `fix/harness-aware-model-routing`
- Workflow surfaces:
  - Task Class to Capability Profile resolution
  - concrete catalog selection
  - Route Lockfile generation
  - delegated-execution guidance
  - Claude Code and Copilot client mappings
  - model-routing validation and evals
- Generated artifacts:
  - `.agents/model-routing/route-lockfile.json`

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| task semantics | `.agents/model-routing/task-classes.yml` | playbook maintainer | resolver, task brief | harness-independent |
| capability semantics | `.agents/model-routing/capability-profiles.yml` | playbook maintainer | resolver | harness-independent |
| active execution identity | `--harness` or actual client mapping | caller/client entry | resolver | required before concrete selection |
| concrete availability | `.agents/model-routing/model-catalog.json` | evidence-backed catalog maintenance | resolver/generator | top-level `harness: claude-code` |
| concrete route | `.agents/model-routing/route-lockfile.json` | `generate_route_lockfile.py` | matching-harness delegated execution | top-level and per-route harness identity |
| delegation brief | execution-plans model-routing reference | supervisor | worker/harness | cannot cite a mismatched model as available |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| matching resolution | repository root | `python3 scripts/resolve_model_route.py codebase_exploration --catalog .agents/model-routing/model-catalog.json --harness claude-code` | Python 3, repository files | selected Claude route | continue when candidate policy passes |
| mismatch resolution | repository root | `python3 scripts/resolve_model_route.py codebase_exploration --catalog .agents/model-routing/model-catalog.json --harness codex` | Python 3, repository files | `selected: false`, mismatch reason | stop concrete delegation |
| lockfile generation | repository root | `python3 scripts/generate_route_lockfile.py --write` | catalog with non-empty harness | harness-bound lockfile | stop on identity inconsistency |
| model validation | repository root | `python3 scripts/validate_model_routing.py` | routing files and catalog | validator pass | stop submission on failure |
| routing evals | repository root | `python3 scripts/validate_model_routing_evals.py` | eval fixtures | eval validator pass | stop submission on failure |
| full verification | repository root / CI | `make verify` | repository toolchain | canonical result | stop submission on failure |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| client/caller | active harness | resolver | non-empty exact string | enforced before candidates |
| catalog | catalog harness | resolver | equals active harness | mismatch returns unresolved |
| resolver | route harness fields | lockfile generator | active = catalog = route | generator checks equality |
| lockfile generator | route lockfile | Claude Code mapping | `harness: claude-code` | explicit in artifact and docs |
| shared reference | delegation rule | Codex/Copilot/Claude supervisors | current harness only | cross-harness fallback prohibited |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| task class | caller/task brief | resolver result | exact task class retained |
| active harness | actual execution environment | resolver `harness` | explicit; never inferred from model family |
| catalog harness | catalog top level | resolver `catalog_harness` | explicit and compared |
| selected model | matching catalog candidate | matching-harness invocation only | unavailable on mismatch |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| resolver and validators | repository controller | repository-root Python commands | pass by design |
| Claude custom agents | Claude Code Agent tool | `.claude/agents/` | catalog/lockfile scoped to same harness |
| Codex delegation | Codex runtime | no matching concrete catalog in this repository | remains unresolved; no Claude invocation claim |
| Copilot delegation | Copilot runtime | client-owned model availability | current Claude artifacts explicitly non-authoritative |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| no new runtime service | not applicable | not applicable | none | not applicable | pass |
| model harness | client-owned | client-specific subagent/model invocation | active harness must be known | verify catalog/lockfile `harness` before invocation | pass by contract |

## Forbidden fallback checks

- filename-order artifact selection: not used.
- mtime/latest/newest artifact inference: not used.
- stale prompt fallback: not used.
- raw co-presence as causal evidence: not used.
- provider/model-name inference as harness identity: prohibited.
- cross-harness profile or candidate fallback: prohibited and mechanically stopped before candidate evaluation.
- use of Claude Code `selected_model` from Codex or Copilot: prohibited by schema, resolver result, tests, and client docs.

## Claim boundaries

- Shared Task Class and Capability Profile resolution does not prove a concrete
  model is invokable.
- `status: available` and `smoke_eval: passed` are meaningful only within the
  catalog's named harness.
- A matching capability profile in a mismatched catalog does not create an
  available worker.
- A Route Lockfile generated for Claude Code is not a Codex or Copilot route.
- No concrete Codex or Copilot model availability is claimed by this PR.
- `selected: false` preserves model-independent route metadata but authorizes no
  delegated invocation.

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
| none | — | The designed chain binds concrete selection to an explicit matching harness and fails closed otherwise. | — |

## Decision

submit
