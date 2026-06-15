# Workflow Contract Review

## Scope

- PR / branch: `codex/agent-workflow-contract-review`
- Workflow surfaces:
  - `.agents/skills/agent-workflow-contract-review/SKILL.md`
  - `.agents/skills/agent-workflow-contract-review/templates/workflow-contract-review.md`
  - `.agents/skills/quality-gate/SKILL.md`
  - `.agents/skills/quality-gate/references/quality-gate.md`
  - `.agents/skills/bug-investigation-and-rca/SKILL.md`
  - `.agents/skills/embedded-system-familiarization/SKILL.md`
  - `.agents/skills/embedded-nfr-harness-design/SKILL.md`
  - `evals/skill-triggers/agent-workflow-contract-review.json`
  - `AGENTS.md`
  - `README.md`
- Generated artifacts:
  - AGENTS generated skill index
  - README generated skill catalog

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| Requirements | `/Users/satoshun/.codex/attachments/62fb761b-95b4-4952-9ba0-d213f13920df/pasted-text.txt` | User GOAL | ExecPlan and implementation | Defines required skill, gate wiring, trigger evals, and acceptance criteria. |
| Plan | `plans/agent-workflow-contract-review.md` | This PR | Implementation and quality-gate | Maps requested deliverables to WBS; no deferred design deliverables. |
| Skill source | `.agents/skills/agent-workflow-contract-review/SKILL.md` | This PR | Agents, generated catalogs, trigger eval names | Defines trigger, anti-trigger, procedure, output report. |
| Report template | `.agents/skills/agent-workflow-contract-review/templates/workflow-contract-review.md` | This PR | Future workflow-contract reports | Matches required output sections. |
| Gate wiring | `.agents/skills/quality-gate/SKILL.md` and reference | This PR | Final submit gate | Checks report existence, submit decision, and findings status only. |
| Trigger evals | `evals/skill-triggers/agent-workflow-contract-review.json` | This PR | `validate_skill_trigger_evals.py` and inventory | Covers 4 positive and 4 near-miss negative cases. |
| Generated catalogs | `python3 scripts/generate_agent_index.py --write` | Repo script | `AGENTS.md`, README generated catalog | Uses SKILL frontmatter as source; no hand-edited generated rows. |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| Generate indexes | controller repo root | `python3 scripts/generate_agent_index.py --write` | Python 3, local working tree | Updated `AGENTS.md` and README generated catalog | Stop on failure. |
| Validate skills | controller repo root | `python3 scripts/validate_skills.py` | Python 3 | Skill validation pass | Stop on failure. |
| Validate trigger evals | controller repo root | `python3 scripts/validate_skill_trigger_evals.py` | Python 3 | Trigger eval validation pass | Stop on failure. |
| Inventory check | controller repo root | `python3 scripts/report_skill_inventory.py --check --format text` | Python 3 | Inventory check pass; warnings reviewed | Stop on errors. |
| Generated index check | controller repo root | `python3 scripts/generate_agent_index.py --check` | Python 3 | No generated drift | Stop on failure. |
| Canonical verify | controller repo root | `make verify` | Repo Makefile and Python 3 | Full canonical verification pass | Stop on failure. |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| New skill frontmatter | `name: agent-workflow-contract-review` | Trigger eval JSON | Skill name matches known catalog | Pass; eval references the exact skill name. |
| New skill frontmatter | short description | AGENTS/README generated catalog | Generated rows derive from SKILL frontmatter | Pass after `generate_agent_index.py --write`. |
| New skill output contract | report path and required sections | `quality-gate` checks | Gate checks `reports/workflow-contract-review/<slug>.md` and `submit` decision | Pass; gate does not duplicate deep checklist. |
| User GOAL trigger seeds | 4 positive + 4 negative prompts | Eval JSON | Prompts and near-misses match requested cases | Pass; all requested cases represented. |
| Embedded runtime discovery requirement | field list in GOAL | Embedded familiarization and harness skill/template updates | Installer path, runtime path, SSH PATH, runner path, env/PATH, helper, version, diagnostics | Pass; fields are present in skill guidance and templates. |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | Not applicable to this repo skill PR | Not applicable | Pass; no validation run-set artifact is produced here. |
| workflow id | `agent-workflow-contract-review` | Eval cases, generated catalogs, quality-gate references | Pass; consistent skill name. |
| target id / class | Not applicable to this repo skill PR | Not applicable | Pass; no target-specific claim is made. |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| Repo validation commands | controller repo root | controller repo root | Pass. |
| Cross-host runtime discovery guidance | target workflows in future repos | documented in embedded skills/templates, no runtime command generated by this PR | Pass; this PR adds fields only. |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| This PR validation | Not applicable | Local repo commands | Local shell PATH for `python3` and `make` | `make verify` | Pass; canonical verification completed. |
| Future controller-target harnesses | Template fields require explicit value | Template fields require explicit value | Template fields require explicit value | Template fields require explicit value | Pass; the template no longer leaves this implicit. |

## Forbidden fallback checks

- filename-order artifact selection: pass; new skill rejects `find ... PLAN-*.json | sort | tail -n 1`.
- mtime/latest/newest artifact inference: pass; new skill rejects latest/newest and mtime-based artifact selection.
- stale prompt fallback: pass; new skill rejects stale prompt fallback when workflow surfaces exist.
- raw co-presence as causal evidence: pass; new skill rejects raw primitive artifact co-presence as causal evidence.

## Claim boundaries

- Workflow authority artifacts: skill/report/gate artifacts only define workflow review authority.
- Validation artifacts: validation command success proves repo skill/index/eval consistency, not target evidence.
- Measurement artifacts: none produced by this PR.
- Blocked claims: no production readiness, target performance, or target selection claim is made.

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
| none | none | No workflow contract findings. | None. |

## Decision

submit
