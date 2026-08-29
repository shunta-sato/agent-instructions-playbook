# Workflow Contract Review

## Scope

- PR / branch: `feat/user-value-delivery-governor`.
- Workflow surfaces: AGENTS bootstrap, feature governor, dev routing, quality
  gate, structure checker, Claude worker/reviewer, Copilot instructions.
- Generated artifacts: AGENTS machine index and README skill catalog, both from
  the canonical skill frontmatter.

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| capability framing | `user-value-delivery` Delivery Control | root agent | dev route, worker, reviewer, gate | single writable owner |
| route | `dev-workflow` Route Summary | root agent | workers and final gate | locked after implementation starts |
| implementation evidence | explicit `agent_run` identity | worker | orchestrator/reviewer/gate | focused validation only |
| candidate decision | `quality-gate` record | assigned gate owner | branch completion | candidate identity required |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| focused structure | worktree | `python scripts/check_structure.py --working-tree --mode feature` | Git worktree and base revision | advisory/new-or-worsened-hard result | stop on blocking hard finding |
| final repository gate | worktree/CI | canonical commands from `COMMANDS.md` | project environment | check results | stop on required failure |
| delegated evidence | worktree | `python3 scripts/agent_run.py record --harness <active> ...` | active harness | explicit run_id | continue when accepted |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| root | Delivery Control | worker/reviewer | user journey, DoD, non-goals, route | pass |
| worker | agent_run | reviewer/gate | run_id, candidate, allowed/changed files, validation | pass |
| CI/target | verification result | gate | candidate/build/target/environment | pass |
| gate owner | gate decision | branch completion | candidate and blocking count | pass |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | explicit run_id list | cited run_id list | pass |
| workflow id | feature Delivery Control | same active campaign | pass |
| target id / class | required only for target claims | same evidence record | pass |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| repository checks | controller/worktree or CI | explicit command source | pass |
| target proof | declared target only when DoD requires it | unchanged specialist route | pass |
| Delivery Control mutation | root/orchestrator | root only | pass |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| repository scripts | repository `scripts/` | canonical Python command | project Python | `COMMANDS.md` | pass |
| Claude skills | `.claude/skills` symlink | `/user-value-delivery` | repository checkout | sync validator | pass |

## Forbidden fallback checks

- filename-order artifact selection: prohibited; explicit candidate/run identity.
- mtime/latest/newest artifact inference: prohibited.
- stale prompt fallback: AGENTS and canonical skill path remain authoritative.
- raw co-presence as causal evidence: not accepted as validation.

## Claim boundaries

- Workflow authority artifacts: Delivery Control and locked Route Summary.
- Validation artifacts: exact commands/results tied to candidate identity.
- Measurement artifacts: required only for explicit NFR/operational claims.
- Blocked claims: optional review, advisory structure, or workflow success cannot
  imply production readiness or target evidence.

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
| none | — | No identity, execution-location, fallback, or claim-boundary defect in the proposed contract. | — |

## Decision

submit
