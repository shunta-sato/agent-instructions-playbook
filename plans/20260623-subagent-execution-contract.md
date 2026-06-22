# Subagent Execution Contract — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Add PR 3 of the Superpowers improvement sequence: make `execution-plans` define model-routed subagent execution as a controlled execution mode.
- Prevent vague delegation by requiring a task brief, allowed files, allowed commands, validation, stop conditions, and report format before invoking a subagent.

## Scope

### In scope

- Update `.agents/skills/execution-plans/SKILL.md` to point to model-routed subagent execution guidance.
- Add `.agents/skills/execution-plans/references/model-routing.md`.
- Add `.agents/skills/execution-plans/references/subagent-execution.md`.
- Add `.agents/skills/execution-plans/templates/subagent-task-brief.md`.
- Add `.agents/skills/execution-plans/templates/subagent-report.md`.
- Add `.agents/skills/execution-plans/templates/supervisor-review-request.md`.
- Add workflow-contract evidence for the new Agent-facing delegation contract.

### Out of scope / non-goals

- Do not add run ledger scripts or `.agents/runs/` in this PR.
- Do not generate model catalogs, route lockfiles, or Copilot custom agents.
- Do not add behavior eval schemas.
- Do not create a new standalone subagent skill.
- Do not add concrete production model IDs.

## Constraints / Quality targets

- Keep `execution-plans/SKILL.md` concise; detailed rules live in references/templates.
- Use task class and capability profile before any concrete model discussion.
- Strict briefs must explicitly name editable files, validation commands, and stop conditions.
- Subagents must stop instead of widening design scope or changing unapproved files.
- Existing `make verify` must remain green.

## Context & Orientation

- Key paths:
  - `.agents/skills/execution-plans/SKILL.md`
  - `.agents/skills/execution-plans/references/`
  - `.agents/skills/execution-plans/templates/`
  - `.agents/model-routing/`
  - `reports/workflow-contract-review/`
- Existing behavior:
  - `execution-plans` currently covers ExecPlan creation and maintenance only.
  - PR #61 added model-routing artifacts and validation, but no subagent task brief contract.
- Unknowns:
  - Future run ledger schema may require extra task brief metadata; this PR keeps only fields needed to supervise execution safely.

## Design

### Boundary sketch

- `SKILL.md` remains the short entrypoint and links to references when delegation or model routing is needed.
- `references/model-routing.md` explains how to classify a task, resolve route metadata, avoid concrete model IDs in static instructions, and avoid `auto` outer model when Copilot custom-agent model fields must be respected.
- `references/subagent-execution.md` defines the delegation lifecycle: classify, write brief, invoke, receive report, supervise, escalate, and preserve evidence.
- Templates are copyable contracts:
  - `subagent-task-brief.md`: pre-invocation task boundary.
  - `subagent-report.md`: worker return format.
  - `supervisor-review-request.md`: supervisor review package for subagent output.
- Error handling:
  - Missing route, missing allowed files, missing validation command, or unclear expected behavior means stop and clarify before delegation.
  - Worker report that changes files outside scope, skips validation without reason, or expands design scope is not accepted as complete.
- Observability:
  - This PR does not add a run ledger, but templates reserve fields that later ledger scripts can consume.

### Testing strategy

- Structural validation:
  - `python3 scripts/validate_skills.py`
  - `python3 scripts/report_skill_inventory.py --check --format text`
- Full canonical chain:
  - `make verify`
- Manual contract review:
  - Check references/templates avoid latest/newest fallback, concrete model IDs, and hidden operator handoff.

## Milestones (high-level plan)

1. Add the ExecPlan and route evidence.
2. Add references and templates for model-routed subagent execution.
3. Update `execution-plans/SKILL.md` with concise reference routing.
4. Add workflow-contract report.
5. Run verification, publish PR, request review, and update automation to the new PR.

## Progress (WBS)

- [x] (P0) Sync after PR #61 merge and create branch — deliverable: `codex/subagent-execution-contract` — verify: branch exists from local `main`.
- [x] (P1) Add references/templates — deliverable: execution-plans reference and template files — verify: files exist and are linked.
- [x] (P2) Update skill entrypoint — deliverable: concise `SKILL.md` routing guidance — verify: `validate_skills.py`.
- [x] (P3) Workflow-contract evidence — deliverable: report under `reports/workflow-contract-review/` — verify: decision `submit`.
- [x] (P4) Verification and publication — deliverable: commit, push, draft PR, review request — verify: https://github.com/shunta-sato/agent-instructions-playbook/pull/62.

## Route / Required Branches

- ExecPlan required: yes.
- Risk level: normal for Agent-facing workflow contract changes.
- Default lane: required; this changes a reusable workflow surface.
- Required branches:
  - `skill-creator`: updating an existing skill with references/templates.
  - `implementation-economy`: normal-risk default lane and new reusable artifacts.
  - `agent-workflow-contract-review`: new Agent-facing subagent workflow and templates.
  - `quality-gate`: mandatory final submit gate.
- Non-triggered branches:
  - `function-boundary-governor`: no code function/helper/API boundary changes.
  - `design-balance`: no new class/module responsibility layout.
  - `architecture-decision-analysis`: PR plan already chose execution-plans mode over a new skill; no new cross-boundary option comparison needed.
  - `observability`: no runtime behavior or signal implementation.
  - embedded/concurrency/UI/legacy/staged-lowering branches: not applicable.

## Implementation Economy

- Changed files target: 8 tracked files or fewer.
- New classes/modules target: 0.
- New helpers/wrappers/adapters target: 0.
- New indirection layers target: 0.
- Rough line budget: initially under 500 net lines; actual staged docs/templates are about 625 inserted lines because the PR includes three copyable contract templates plus the ExecPlan and workflow-contract report.
- Budget decision: accept the overrun because it does not add code, classes, helpers, or runtime indirection, and trimming the templates would remove required task identity, validation, and escalation fields.
- Worth-its-weight decision: use two references and three templates because `SKILL.md` should stay concise and task briefs/reports need copyable structure.

## Surprises & Discoveries

- 2026-06-23: `execution-plans` had no `templates/` directory before this PR; adding it keeps copyable delegation artifacts out of `SKILL.md`.
- 2026-06-23: The line budget exceeded the initial estimate because the PR adds complete brief/report/review templates; accepted as documentation-only contract surface.

## Decision log

- 2026-06-23: Implement subagent execution as `execution-plans` references/templates, not a new skill.
  - Options considered: new standalone subagent skill; add only prose to `execution-plans/SKILL.md`; references/templates under `execution-plans`.
  - Chosen: references/templates under `execution-plans`.
  - Consequences: keeps trigger surface stable and makes delegation a plan execution mode.

## Handoff

- Current branch / commit: `codex/subagent-execution-contract`, draft PR #62 open.
- What is done: PR #61 merged; local `main` synced; branch created; plan started; references/templates, `SKILL.md` entrypoint update, workflow-contract report, local verification, commit, push, and PR creation are complete.
- What is not done: review request, GitHub review response, PR ready-for-review transition, merge, next PR.
- How to run: `make verify`.
- How to test: `python3 scripts/validate_skills.py`; `python3 scripts/report_skill_inventory.py --check --format text`; `make verify`.
- Known risks / open questions: future run ledger PR may extend template fields.
- Next 1-3 steps: request review, address feedback if any, mark ready and merge on Approve.
- Pointers: `.agents/skills/execution-plans/`, `.agents/model-routing/`, `reports/workflow-contract-review/`.

## Validation & Acceptance

- AC1: Subagent execution before invocation requires a task brief.
  - Verification: `references/subagent-execution.md` and `templates/subagent-task-brief.md`.
- AC2: Strict brief requires editable files, validation command, and stop conditions.
  - Verification: `templates/subagent-task-brief.md`.
- AC3: Subagent cannot silently broaden design scope.
  - Verification: stop/escalation rules in reference and report template.
- AC4: Model routing happens through task class and capability profile, not hard-coded model IDs.
  - Verification: `references/model-routing.md`.
- AC5: Canonical verification stays green.
  - Verification: `make verify`.

## Outcomes & Retrospective

- What shipped / merged: draft PR opened at https://github.com/shunta-sato/agent-instructions-playbook/pull/62.
- What went well: details stayed in references/templates while `SKILL.md` only gained concise routing guidance.
- What went wrong: none so far.
- Follow-ups / tech debt tickets: run ledger, quality-gate delegated-run evidence, behavior/model smoke evals, and review/branch-completion skills remain later PRs.
