# Workflow Contract Review

## Scope

- PR / branch: `codex/preflight-engineering-review-followup`
- Workflow surfaces: `preflight-engineering` cache-readiness guidance, development commander handoff prompt template, and trigger eval boundaries.
- Generated artifacts: none. `AGENTS.md` and README generated catalogs are not expected to change because Skill metadata is unchanged.

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| PR #74 review feedback | GitHub PR comments and prior ChatGPT thread review | reviewers | follow-up branch | Explicit PR #74 comments, not latest/newest discovery |
| Cache guidance update | `.agents/skills/preflight-engineering/SKILL.md` and `references/cache-readiness-checklist.md` | this PR | future agents using preflight | Distinguishes repo-stable from task-stable shared prefix |
| Handoff template update | `references/handoff-prompt-template.md` | this PR | development commander handoff prompts | Separates shared task context from worker-specific suffix |
| Trigger eval update | `evals/skill-triggers/preflight-engineering.json` | this PR | eval validators and reviewers | Adds two near-miss negative cases |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| Validate skills | local repo | `python3 scripts/validate_skills.py` | Python 3 | validation output | stop on failure |
| Validate trigger evals | local repo | `python3 scripts/validate_skill_trigger_evals.py` | Python 3 | validation output | stop on failure |
| Check generated index | local repo | `python3 scripts/generate_agent_index.py --check` | Python 3 | zero-diff check | stop on failure |
| Canonical verify | local repo | `make verify` | repo toolchain | full verification output | stop on failure |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| Review feedback | PR #74 comments | follow-up changes | accepted items reflected in changed files | pass |
| Skill guidance | cache and handoff templates | future preflight output | repo-stable vs task-stable terms stay consistent | pass |
| Trigger evals | preflight eval JSON | eval validator | skill name exists and cases encode trigger boundaries | pass |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | `codex/preflight-engineering-review-followup` | validation, PR, review request | pass for local validation; PR pending |
| workflow id | `preflight-engineering-review-followup` | report, PR body, review request | pass |
| target id / class | repository-local Agent Skill | `preflight-engineering` skill consumers | pass |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| Skill/eval validation | local repository | local repository | pass |
| PR/review lifecycle | GitHub and prior ChatGPT thread | external workflow after local verification | pending |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| Repository validators | repo scripts | `python3 scripts/...` | Python 3 available | `COMMANDS.md`, Makefile | pass |
| Canonical verify | Makefile | `make verify` | make and repo deps available | `COMMANDS.md` | pass |
| GitHub PR | connector / git remote | push branch and create PR | GitHub connector available | remote checked by previous loop | pending |
| ChatGPT review | Chrome session | prior thread URL | user-approved review loop | explicit thread URL from prior loop | pending |

## Forbidden fallback checks

- filename-order artifact selection: pass; explicit PR number and file paths are used.
- mtime/latest/newest artifact inference: pass.
- stale prompt fallback: pass; review request will cite current branch/PR and changed files.
- raw co-presence as causal evidence: pass; producer and consumer artifacts are explicit.

## Claim boundaries

- Workflow authority artifacts: Skill guidance, templates, eval seeds, workflow contract report.
- Validation artifacts: command output after execution.
- Measurement artifacts: not applicable.
- Blocked claims: no runtime, production, security, or measured token-savings claims.

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
|  |  |  |  |

## Decision

submit
