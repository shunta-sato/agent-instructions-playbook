# Agent Workflow Contract Review - ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Prevent recurrence of Agent-facing workflow product bugs where generated instructions, collect plans, validation artifacts, and handoff artifacts drift from the product contract.
- Add a focused skill and gate wiring so future agents replay generated workflow semantics, verify artifact identity chains, and check controller/target runtime discovery assumptions before submit.

## Scope

### In scope
- Add `.agents/skills/agent-workflow-contract-review/SKILL.md`.
- Add `.agents/skills/agent-workflow-contract-review/templates/workflow-contract-review.md`.
- Update `quality-gate` to require a Workflow Contract Review Report for Agent-facing workflow changes.
- Update `bug-investigation-and-rca`, `embedded-system-familiarization`, and `embedded-nfr-harness-design` with the requested prevention/runtime discovery clauses.
- Add trigger eval seeds for positive and near-miss negative cases.
- Update README Skill Map plus generated README/AGENTS catalogs.
- Self-apply the new discipline with `reports/workflow-contract-review/agent-workflow-contract-review.md`.

### Out of scope / non-goals
- No adc-lab code changes.
- No broad rewrite of existing embedded/NFR skills.
- No expansion of `quality-gate` into the deep workflow contract checklist; it only checks report presence and decision.
- No new top-level orchestration framework beyond the requested skill.

## Constraints / Quality targets

- Latency / throughput / resource budgets: not applicable; docs/skill metadata only.
- Safety/security/privacy: no real target hostnames, credentials, private artifacts, or production data in templates.
- Compatibility / rollout constraints: keep `.agents/skills` as the single skill source; generated indexes must pass `--check`.
- Operability: final PR must include exact validation commands and results.
- Quantitative targets: none declared; acceptance is artifact and command based.

## Context & Orientation

- Key paths:
  - `.agents/skills/*/SKILL.md`
  - `.agents/skills/*/templates/`
  - `evals/skill-triggers/*.json`
  - `README.md`
  - `AGENTS.md`
  - `reports/workflow-contract-review/`
- Existing behavior:
  - `quality-gate` checks triggered-branch evidence but has no Agent-facing workflow contract artifact.
  - Embedded skills cover target evidence and physical NFR proof but not generated argv replay or installer/runtime discovery compatibility.
  - `generate_agent_index.py --write` updates both AGENTS generated index and README generated catalog.
- Conventions:
  - New skill frontmatter must include `name`, `description`, and `metadata.short-description`.
  - Trigger eval cases are JSON under `evals/skill-triggers`.
  - Keep heavy checklist detail in the dedicated skill/template, not `quality-gate`.
- Unknowns:
  - Whether `report_skill_inventory.py --check` will flag broad wording in the new skill. Mitigation: use narrow trigger wording and eval coverage.

## Design

### Boundary sketch

- `agent-workflow-contract-review`: owns deep review procedure and required report shape for Agent-facing workflow product contracts.
- `quality-gate`: owns final submit/no-submit evidence check only; it verifies the report exists, says `submit`, and resolved/accepted findings are bounded.
- `bug-investigation-and-rca`: owns prevention clauses when RCA root cause is a missed workflow/product contract.
- `embedded-system-familiarization`: owns cross-host deployment/runtime discovery fields at target-learning/control-surface time.
- `embedded-nfr-harness-design`: owns controller-target harness contract fields for measurement harnesses.
- `README.md` human Skill Map and generated catalogs: expose the new skill without making always-on rules heavier.
- `evals/skill-triggers/agent-workflow-contract-review.json`: protects trigger boundaries.
- `reports/workflow-contract-review/agent-workflow-contract-review.md`: self-applied review evidence for this PR.

### Design-to-WBS coverage check

| Design deliverable | WBS item |
| --- | --- |
| New skill + template | P1 |
| Quality-gate wiring | P2 |
| RCA/embedded skill updates | P2 |
| Trigger eval seeds | P3 |
| README/AGENTS generated indexes | P3 |
| Self-applied Workflow Contract Review Report | P4 |
| Verification + PR | P5 |

No deliverables are deferred.

### Responsibility Map

| Unit | Name | Responsibility sentence | Reason to change | Dependency direction |
| --- | --- | --- | --- | --- |
| Skill | `agent-workflow-contract-review` | Define when and how to review Agent-facing generated workflows as product contracts. | Workflow contract review scope or required checks change. | Read by agents; referenced by gate. |
| Template | `workflow-contract-review.md` | Provide a reusable report skeleton matching the skill output contract. | Report sections or artifact shape change. | Depends on skill output contract. |
| Gate | `quality-gate` | Check whether workflow-contract evidence exists and is submit-ready. | Submission evidence requirements change. | Depends on dedicated skill artifact. |
| RCA skill | `bug-investigation-and-rca` | Ensure missed workflow/product contracts produce durable prevention. | Bug prevention requirements change. | Independent; can point to workflow skill. |
| Embedded skills | `embedded-system-familiarization`, `embedded-nfr-harness-design` | Capture cross-host runtime discovery and harness path assumptions before target claims. | Embedded controller/target contract fields change. | Independent; feeds target/NFR gates. |
| Eval seeds | `agent-workflow-contract-review.json` | Prove positive and near-miss trigger boundaries. | Trigger scope changes. | Depends on skill name and descriptions. |

Layout decision: keep-layout with one new focused skill plus template. Rejected alternatives: absorb everything into `quality-gate` (too much deep checklist in final gate), or spread the full checklist across embedded skills (misses non-embedded Agent workflows).

### Complexity Budget

- Changed files target: 11-14 files, including generated indexes and one plan/report artifact.
- New classes/modules target: 1 new skill directory.
- New helpers/wrappers/adapters target: 0.
- New indirection layers target: 0.
- Rough production/test line budget: 250-450 documentation/eval lines, no runtime code unless generated index updates.
- Quantitative plan target reconciliation: no numeric outcome target declared; budget is review scope only.

### Testing strategy

- Skill schema: `python3 scripts/validate_skills.py`.
- Trigger eval schema/name coverage: `python3 scripts/validate_skill_trigger_evals.py`.
- Inventory and trigger-risk report: `python3 scripts/report_skill_inventory.py --check --format text`.
- Generated index/catalog freshness: `python3 scripts/generate_agent_index.py --check`.
- Canonical chain: `make verify`.

## Milestones (high-level plan)

1. Define the workflow-contract skill and report template with narrow triggers and explicit anti-triggers.
2. Wire existing skills and quality-gate to route/check the new report without duplicating deep taxonomy.
3. Add trigger evals and update generated README/AGENTS catalogs.
4. Self-apply the new report to this PR and run the full verification chain.
5. Commit, push, and open a draft PR.

## Progress (WBS)

- [x] (P0) Explore requested GOAL and repo conventions - deliverable: this ExecPlan route and context - verify: relevant skills/scripts/files read.
- [x] (P1) Add new skill and template - deliverable: `agent-workflow-contract-review` skill folder - verify: `validate_skills.py`.
- [x] (P2) Wire existing skills/gate - deliverable: updated `quality-gate`, RCA, embedded familiarization, and harness skills - verify: diff review and skill validation.
- [x] (P3) Add trigger evals and generated catalogs - deliverable: eval JSON plus generated README/AGENTS updates - verify: trigger eval validation and generated index check.
- [x] (P4) Self-apply workflow contract review - deliverable: `reports/workflow-contract-review/agent-workflow-contract-review.md` - verify: report decision is `submit`.
- [x] (P5) Verify and prepare publish - deliverable: verified branch ready for commit, push, draft PR - verify: `make verify` passed.

## Surprises & Discoveries

- 2026-06-15: `origin/main` had advanced by 2 commits; local `main` was fast-forwarded before creating `codex/agent-workflow-contract-review`.
- 2026-06-15: `generate_agent_index.py --write` updates both AGENTS and README generated catalog, so README generated rows should not be hand-edited.
- 2026-06-15: First `make verify` failed only on trailing whitespace in `quality-gate/SKILL.md`; after removing it, `make verify` passed.
- 2026-06-15: Review found stale Handoff state and a local Codex attachment path in the self-review report; both were fixed before moving the PR out of draft.

## Decision log

- 2026-06-15: Create a new focused skill because the requested behavior changes route-to-skill and submit/no-submit decisions for Agent-facing workflow product contracts.
  - Options considered: absorb into `quality-gate`, distribute across embedded skills, add a dedicated skill.
  - Chosen: dedicated `agent-workflow-contract-review` plus concise `quality-gate` existence/decision check.
  - Consequences: one new skill surface, protected by positive and near-miss trigger evals.
- 2026-06-15: Do not add an `init_artifact.py` kind in this PR.
  - Options considered: add script bootstrap for the new report, or keep only a skill template.
  - Chosen: keep only a template because acceptance requires the template/report, not a script API change.
  - Consequences: smaller blast radius; future PR can add bootstrap support if repeated use shows value.

## Handoff (update at every stop)

- Current branch / commit: `codex/agent-workflow-contract-review` / PR #57 head after review-fix commit.
- What is done: implementation committed and pushed, PR #57 opened and marked Ready for review, review feedback fixes applied, local `make verify` passed, and GitHub Actions checks passed for the latest pushed head when last checked.
- What is not done: merge.
- How to run: `make verify`.
- How to test: `make verify`.
- Known risks / open questions: re-check GitHub Actions if another commit is pushed. Inventory still reports 7 existing broad-trigger warnings; the new skill reports no broad-trigger warning.
- Next 1-3 steps:
  1. Merge after approval.
- Pointers:
  - `.agents/skills/quality-gate/SKILL.md`
  - `.agents/skills/bug-investigation-and-rca/SKILL.md`
  - `.agents/skills/embedded-system-familiarization/SKILL.md`
  - `.agents/skills/embedded-nfr-harness-design/SKILL.md`
  - `evals/skill-triggers/`

## Validation & Acceptance

- AC1: New `agent-workflow-contract-review` skill exists under `.agents/skills/` with requested trigger, anti-trigger, procedure, and output artifact.
  - Verification: `python3 scripts/validate_skills.py` and file review.
- AC2: README Skill Map, README generated catalog, and AGENTS generated index include the new skill.
  - Verification: `python3 scripts/generate_agent_index.py --check`.
- AC3: Positive and near-miss negative trigger eval seeds cover the requested cases.
  - Verification: `python3 scripts/validate_skill_trigger_evals.py`.
- AC4: `quality-gate` requires a Workflow Contract Review Report for Agent-facing workflow changes and does not duplicate the deep checklist.
  - Verification: file review plus `make verify`.
- AC5: RCA and embedded skills include the requested prevention/runtime discovery clauses.
  - Verification: file review plus `make verify`.
- AC6: The PR self-applies the new discipline with a Workflow Contract Review Report.
  - Verification: report exists and decision is `submit`.
- AC7: Canonical validation passes.
  - Verification: `make verify`.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: branch ready for PR with new `agent-workflow-contract-review` skill, gate wiring, trigger evals, generated indexes, and self-review report.
- What went well: new skill stayed below broad-trigger warning threshold; generated indexes and eval schemas passed.
- What went wrong: first `make verify` caught a trailing whitespace line; fixed before final validation.
- Follow-ups / tech debt tickets: none.
