# Preflight Engineering Operationalization — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Extend `preflight-engineering` from a manual orchestration skill into an operational preflight toolkit.
- Keep `preflight-engineering` as the orchestrator while adding read-only repository inspection helpers, a domain preflight skill scaffold, and the first high-risk domain preflight skills.

## Scope

### In scope

- PR 1: Add read-only repo inspection helper scripts, a repo-inspection output template, and helper usage guidance in `preflight-engineering`.
- PR 2: Add `preflight-domain-template` with common domain output/reference templates and add domain routing guidance to `preflight-engineering`.
- PR 3: Add `preflight-auth-session`, `preflight-api-compat`, and `preflight-db-migration` with references/examples and trigger eval coverage.
- Add or update trigger evals and generated skill indexes as required by each PR.
- Produce workflow-contract review evidence for each Agent-facing workflow change.

### Out of scope / non-goals

- Product implementation in a downstream repository.
- Migration or deployment execution.
- Reading secret values.
- Adding runtime dependencies.
- Editing generated clients.
- Building a full static analyzer or claiming measured token savings.
- Implementing every possible domain preflight skill in this GOAL.

## Constraints / Quality targets

- Latency / throughput / resource budgets: helper scripts must stay lightweight and use only the Python standard library.
- Safety/security/privacy: helper scripts must be read-only and never open secret-like files; secret-like paths may be listed as paths only.
- Compatibility / rollout constraints: new skills must pass existing skill metadata/index/eval validators.
- Operability: outputs must separate `confirmed`, `inferred`, and `unknown` facts so human review can audit decisions.

## Context & Orientation

- Key paths / entry points:
  - `.agents/skills/preflight-engineering/SKILL.md`
  - `.agents/skills/preflight-engineering/references/`
  - `evals/skill-triggers/preflight-engineering.json`
  - `scripts/validate_skills.py`
  - `scripts/validate_skill_trigger_evals.py`
  - `scripts/generate_agent_index.py`
- Existing behavior: `preflight-engineering` already inventories stable repo surfaces, classifies risk, extracts invariants, builds routing, checks cache readiness, and emits a commander handoff prompt.
- Conventions to follow: root `AGENTS.md` stays compact; detailed guidance lives in `.agents/skills/<name>/SKILL.md`; generated indexes are updated by `python3 scripts/generate_agent_index.py --write`.
- Unknowns: external reviewer feedback may require a second pass before each PR can merge.

## Design

### Boundary sketch

- `preflight-engineering` remains the single orchestrator and decides when to run helpers or domain skills.
- Repo inspection scripts are collectors only. They output path and command candidates; the skill and human operator decide what to do.
- Domain preflight skills produce domain invariants, first docs/files, context-map proposals, test routing, approval/reviewer needs, and handoff fragments.
- Trigger evals protect against over-triggering domain preflight for ordinary implementation when AGENTS/context are already current.

### Dev-workflow route

- Selected risk route: normal.
- Why this level: this is Agent-facing workflow and skill-template work across multiple files and PRs, but it does not alter runtime product behavior.
- Escalation trigger: high risk if scripts begin executing tests/migrations/deploys, reading secrets, changing git state, or making authoritative implementation decisions.
- Default lane: required.
- Required branches:
  - `execution-plans`: required because the GOAL spans multiple PRs and review loops.
  - `implementation-economy`: required by normal route and new helpers/templates.
  - `agent-workflow-contract-review`: required because skills, scripts, templates, and evals are Agent-facing workflow surfaces.
  - `playbook-template-authoring`: required for reusable scaffold/templates.
  - `skill-creator`: required when creating new skills in PR2/PR3.
  - `requesting-code-review`, `receiving-code-review`, and `branch-completion`: required for each PR loop.
  - `quality-gate`: required before each submission.
- Non-triggered branches: product bug/RCA, architecture decision, performance, concurrency, embedded, UI, staged-lowering, and legacy workflows are not triggered by this repo playbook change.

### Implementation economy budget

- Changed files target: PR1 <= 8 files, PR2 <= 8 files, PR3 <= 14 files.
- New classes/modules target: no new classes; script modules are standalone CLI collectors.
- New helpers/wrappers/adapters target: PR1 may add small local functions for safe path walking and reporting; PR2/PR3 should prefer templates over reusable code.
- New indirection layers target: none.
- Rough production/test line budget: PR1 target <= 550 lines, accepted ceiling <= 850 lines if needed for secret-safe walking plus JSON/Markdown output in the requested script files; PR2 <= 350 lines, PR3 <= 650 lines.

### Observability

- Not applicable to runtime product behavior. Helper scripts expose explicit warnings and `human_decisions_required` entries instead of logs/metrics.

### Testing strategy

- Unit tests: direct script smoke commands for PR1 helper outputs.
- Integration tests: `make verify` for each PR.
- Manual verification: inspect generated JSON/Markdown snippets for secret-safety and confirmed/inferred/unknown separation.

## Milestones

1. Add repo inspection helpers and update `preflight-engineering` to invoke them as read-only collectors.
2. Add domain preflight scaffold and routing table while keeping unimplemented domains clearly marked as candidates.
3. Add auth/API/DB domain skills with references, examples, trigger evals, and regenerated skill indexes.
4. Complete review loops and merge each PR into `main`.

## Progress (WBS)

- [x] (P1) Repo inspection helpers — deliverable: scripts, template, skill update, eval update, workflow report — verify: helper smoke commands and `make verify` passed.
- [x] (P1R) PR1 review loop — deliverable: PR, review request, review disposition, merge — verify: PR #76 approved in the requested ChatGPT thread and squash-merged to `main` at `2c903aa`.
- [x] (P2) Domain scaffold — deliverable: template skill, references, domain routing table, workflow report — verify: `make verify` passed.
- [x] (P2R) PR2 review loop — deliverable: PR, review request, review disposition, merge — verify: PR #77 approved in the requested ChatGPT thread and squash-merged to `main` at `af9733f`.
- [x] (P3) First domain skills — deliverable: three domain skills, references/examples, trigger evals, regenerated index, workflow report — verify: `make verify` passed.
- [ ] (P3R) PR3 review loop — deliverable: PR, review request, review disposition, merge — verify: approval/merge state.

## Surprises & Discoveries

- 2026-06-27: Working tree started with unrelated untracked function-design artifacts and `.DS_Store` files; they are out of scope and must not be staged.
- 2026-06-27: `estimate_context_size.py --root .` correctly warned that root `AGENTS.md` is slightly over 8 KiB; this is evidence that the warning path works, not a PR1 blocker.
- 2026-06-27: `report_skill_inventory.py --check` warns that `preflight-domain-template` has no trigger eval coverage. This is accepted for PR2 because the template skill is an authoring scaffold; executable domain skill eval coverage is PR3 scope.

## Decision log

- 2026-06-27: Split into three PRs as requested because scripts, domain scaffold, and domain skills have distinct review surfaces.
  - Options considered: one large PR; requested three-PR sequence.
  - Chosen: three PRs.
  - Consequences: each PR must update this plan and include its own workflow-contract review and quality gate evidence.
- 2026-06-27: Keep repo inspection scripts dependency-free because the repository validators and intended skill use should work in unfamiliar repos without installing packages.
  - Options considered: rich scanner dependencies; standard library collectors.
  - Chosen: standard library collectors.
  - Consequences: outputs are conservative candidates, not authoritative static analysis.

## Post-Implementation Economy Audit

| New abstraction | Justification | Decision | Evidence |
| --- | --- | --- | --- |
| `inspect_repo.py` collector module | Keeps repo fact collection repeatable while preserving human decision ownership. | keep | Smoke output separates confirmed/inferred/unknown and lists secret-like paths without opening them. |
| `estimate_context_size.py` collector module | Provides a lightweight preflight size warning without adding tokenizer dependencies. | keep | Smoke output warns on root `AGENTS.md` over 8 KiB. |
| `check_agent_docs.py` collector module | Encodes repeatable AGENTS/context structural checks as warnings, not decisions. | keep | Smoke output reports pass/warning/human-decision sections. |
| `preflight-domain-template` skill | Standardizes future domain skill outputs without making the orchestrator skill larger. | keep | `validate_skills.py` passes and the template links four explicit reference artifacts. |
| `preflight-auth-session` skill | Keeps auth/session invariants out of the generic orchestrator while making token logging, redirect, error mapping, and generated-client boundaries explicit. | keep | `validate_skills.py` and auth trigger eval validation pass. |
| `preflight-api-compat` skill | Gives API compatibility and generated-client work a focused preflight without expanding generic preflight text. | keep | `validate_skills.py` and API trigger eval validation pass. |
| `preflight-db-migration` skill | Separates migration/backfill execution boundaries and rollback/compatibility invariants from generic preflight. | keep | `validate_skills.py` and DB trigger eval validation pass. |

Budget note: PR1 exceeded the initial 550-line target because each requested CLI needs standalone secret-like path filtering, hidden-path handling, structured output, and Markdown rendering. I kept the code in the requested three scripts rather than adding a fourth shared module, so review scope remains aligned with the GOAL file list. Final script line count is 810, under the accepted 850-line ceiling.

## Handoff (update at every stop)

- Current branch / commit: `codex/preflight-critical-domain-skills` from `main` at `af9733f`.
- What is done: PR1 merged as #76; PR2 merged as #77; PR3 domain skills, references/examples, trigger evals, generated indexes, workflow contract report, and `make verify` completed.
- What is not done: PR3 review and merge.
- How to run: `make verify`; helper smoke commands:
  - `python3 -m py_compile .agents/skills/preflight-engineering/scripts/inspect_repo.py .agents/skills/preflight-engineering/scripts/estimate_context_size.py .agents/skills/preflight-engineering/scripts/check_agent_docs.py`
  - `python3 .agents/skills/preflight-engineering/scripts/inspect_repo.py --root . --markdown --max-depth 3`
  - `python3 .agents/skills/preflight-engineering/scripts/estimate_context_size.py --root .`
  - `python3 .agents/skills/preflight-engineering/scripts/check_agent_docs.py --root .`
- How to test: run helper scripts against `--root .`, then run `make verify`.
- Known risks / open questions: external review can request additional safeguards or template changes.
- Next 1-3 steps: publish PR3 and request review.
- Pointers: start with `.agents/skills/preflight-engineering/SKILL.md` and this plan.

## Validation & Acceptance

- AC1: PR1 helper scripts are read-only collectors and do not open secret-like files.
  - Verification: script design review, smoke commands, workflow contract report, `make verify`.
- AC2: PR1 outputs distinguish `confirmed`, `inferred`, and `unknown`.
  - Verification: sample JSON/Markdown output from `inspect_repo.py`.
- AC3: PR2 domain scaffold defines the common domain preflight result contract and non-implementation rules.
  - Verification: skill validator and template review.
- AC4: PR3 domain skills exist with valid metadata, references/examples, and balanced positive/negative trigger evals.
  - Verification: generated index check and eval validator.
- AC5: Each PR completes the requested review loop and merges to `main`.
  - Verification: PR approval/review result and merge state.

## Outcomes & Retrospective (fill when done)

- What shipped / merged:
- What went well:
- What went wrong:
- Follow-ups / tech debt tickets:
