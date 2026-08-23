# Workflow Contract Review

## Scope

- PR / branch: `feature/variant-exploration`
- Workflow surfaces:
  - research routing for executable variant comparison
  - single-PoC anti-overlap boundary
  - evidence and synthesis handoffs
  - blocker-only exploration review
  - rebuild-from-contract promotion
  - reviewer task/model routing
- Generated artifacts:
  - `AGENTS.md` Agent Index
  - `README.md` Skill Catalog
  - `.agents/model-routing/route-lockfile.json`
  - `.claude/skills/variant-exploration`

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| mode routing | explicit mode or `.agents/project-policy.yml` | requester/project policy | `research-workflow`, `variant-exploration` | no research receipt means no relaxed profile |
| cycle contract | Exploration Cycle Record | `variant-exploration` | evaluator, reviewer, `research-synthesis` | carries controlled substrate, identities, observations, claim IDs |
| citable evidence | experiment/claim ledger records | `experiment-loop` runner | `research-synthesis`, Productization Brief | informal observation is not promoted as a claim |
| convergence | Productization Brief | `variant-exploration` + `research-synthesis` | delivery implementation | runtime prototype source is explicitly non-authoritative |
| delivery crossing | promotion acknowledgment + delivery run evidence | delivery workflow | research boundary gate | exact paths and evidence remain governed by existing promotion contract |
| reviewer route | task class → capability profile → route lockfile | model-routing generator | agent harness | bounded fallback is recorded; escalation is explicit |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| research boundary receipt | repository root | `python3 scripts/check_research_evidence.py --working-tree --policy .agents/project-policy.yml --mode research` | Python 3, Git worktree | gate output in cycle/report | stop on safety finding or unresolved mode boundary |
| evidence registration | repository root | `python3 scripts/research_run.py register ...` then `execute --experiment-id E-XXXX` | exact command/metric inputs | experiment and claim ledger records | continue only from registered outcome |
| synthesis claim check | repository root | `python3 scripts/check_research_evidence.py --check-ledger` | canonical ledger | verified claim set | stop promotion on invalid claims |
| route generation | repository root | `python3 scripts/generate_route_lockfile.py --write` | model-routing files and catalog | route lockfile | stop on resolver error |
| full validation | repository root / CI | `make verify` | repository toolchain | canonical validation result | stop submission on failure |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| Variant Brief | variant build/run | evaluation protocol | variant ID, base revision, controlled substrate | pass: required by Skill/reference/template |
| evaluation run | observation/artifact | blocker-only reviewer | source/build/target/protocol identity | pass: mismatch is a blocking finding |
| experiment runner | claim ID | research synthesis | experiment ID, command, metric, outcome | pass: existing ledger contract retained |
| variant exploration | Productization Brief | delivery workflow | selected contracts, evidence limits, code disposition | pass: required on promotion candidate |
| task class | capability profile | route resolver | exact profile and fallback chain | pass: generated lockfile records fallback |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | explicit experiment IDs / evaluation scenario set | synthesis and Productization Brief references | pass; no latest/newest inference |
| workflow id | cycle ID plus protocol revision | reviewer and synthesis handoff | pass; template requires both |
| target id / class | target/device/OS/build fields | evaluation artifacts and reviewer | pass; missing/mismatched identity blocks evaluation |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| repository validators | controller/repository root | explicit repository-root commands | pass |
| mobile/device variant execution | declared target/device harness | Variant Brief and evaluation protocol | pass; no controller/target command is hard-coded by the Skill |
| experiment measurement | command-declared location | owned by `experiment-loop` registration | pass; variant workflow does not rewrite argv |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| none introduced | not applicable | not applicable | none | not applicable | pass |
| external device/harness selected by a target project | project-owned | recorded in Variant Brief/evaluation protocol | project-owned and must be explicit | source/build/target identity check | pass within this repo-neutral contract |

## Forbidden fallback checks

- filename-order artifact selection: absent; identities and explicit artifact paths are required.
- mtime/latest/newest artifact inference: absent; cycle, variant, experiment, claim, build, and target identities are explicit.
- stale prompt fallback: absent; Skill/reference/template and generated Agent Index are the authoritative instruction surfaces.
- raw co-presence as causal evidence: prohibited; observation, registered evidence, and production claims are separated.

## Claim boundaries

- Workflow authority artifacts: Skill, reference, Exploration Cycle Record,
  Variant Briefs, blocker-only review, and Productization Brief.
- Validation artifacts: research boundary-gate output, trigger/behavior/model
  routing validators, workflow-contract report, and canonical repository checks.
- Measurement artifacts: only registered experiment/claim records can support
  empirical claims; informal human/device observations are labelled with limits.
- Blocked claims:
  - production-ready or maintainable based on exploration review
  - quantitative superiority from an unregistered observation
  - causal attribution from a multi-axis bundle comparison
  - delivery readiness from a selected prototype
  - prototype source as authoritative production implementation

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
| none | — | No contract inconsistency identified in the designed chain. | — |

## Decision

submit
