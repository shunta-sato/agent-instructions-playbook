# Workflow Contract Review

## Scope

- PR / branch: current branch security fix for PR comment approval spoofing.
- Workflow surfaces:
  - `.agents/skills/receiving-code-review/SKILL.md`
  - `.agents/skills/branch-completion/SKILL.md`
  - `evals/skill-triggers/review-branch-completion.json`
- Generated artifacts: skill trigger eval case `pr-comment-approve-no-merge-handoff`.

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| Review feedback intake | PR comments and review submissions from repository source of truth | GitHub / review system | `receiving-code-review` | PR comments are feedback only; formal review state and actor identity are required for approval authority. |
| Approval handoff | Authorized approval signal | `receiving-code-review` | `branch-completion` | Handoff exists only for formal approved review by an authorized reviewer or explicit merge authorization by a user with merge authority. |
| Merge decision | Completion Record review/approval authority source | `branch-completion` | Agent/operator final report | Merge path records authority source instead of accepting free-form text. |
| Regression eval | `pr-comment-approve-no-merge-handoff` | This change | `validate_skill_trigger_evals.py` and downstream trigger evaluators | Spoofed contributor comment must not trigger branch completion. |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| Validate skill trigger evals | repository root | `python3 scripts/validate_skill_trigger_evals.py` | Python 3 | validation success for updated eval JSON | stop on schema/name failure |
| Full repo verification | repository root | `make verify` | Python 3, Make | validation output and `git diff --check` success | stop on any command failure |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| `receiving-code-review` | approval handoff | `branch-completion` | formal approved review + authorized reviewer OR explicit merge authorization + authorized actor | pass |
| PR comment source | feedback item | `receiving-code-review` | disposition only; no approval authority inferred from comment body | pass |
| Trigger eval | `pr-comment-approve-no-merge-handoff` | trigger evaluator | `branch-completion` listed in `should_not_trigger` | pass |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | not applicable | not applicable | pass |
| workflow id | review lifecycle / branch completion | review lifecycle / branch completion | pass |
| target id / class | not applicable | not applicable | pass |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| Skill/eval validation | repository root | repository root | pass |
| Review/merge workflow | repository source-of-truth APIs/UI | repository source-of-truth APIs/UI | pass |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| Local validation | not applicable | `make verify` | Python/Make available in repo environment | `make verify` run | pass |

## Forbidden fallback checks

- filename-order artifact selection: pass; no latest/newest artifact selection introduced.
- mtime/latest/newest artifact inference: pass; no mtime inference introduced.
- stale prompt fallback: pass; authorization must come from repository source of truth.
- raw co-presence as causal evidence: pass; PR comment text is explicitly insufficient for approval authority.

## Claim boundaries

- Workflow authority artifacts: formal approved review from authorized reviewer or explicit merge authorization from authorized actor.
- Validation artifacts: `make verify` validates syntax/schema and trigger eval coverage; it is not an external GitHub permission proof.
- Measurement artifacts: none.
- Blocked claims: a free-form PR/issue/branch comment cannot claim merge approval authority.

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
|  |  |  |  |

## Decision

submit
