# Quality Gate Run Evidence — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Add PR 5 of the Superpowers improvement sequence: `quality-gate` must not accept delegated/subagent work without fresh run evidence.
- Convert the PR #63 run ledger into a final-gate exit criterion while keeping token telemetry optional.

## Scope

### In scope

- Update `.agents/skills/quality-gate/SKILL.md`.
- Update `.agents/skills/quality-gate/references/quality-gate.md`.
- Add `evals/skill-behavior/quality-gate.json` as behavior seed data for later validation.
- Add workflow-contract evidence for the quality-gate delegated-run evidence chain.

### Out of scope / non-goals

- Do not add `scripts/validate_skill_behavior_evals.py`; that is PR 6.
- Do not modify `scripts/agent_run.py`, `scripts/judge_agent_run.py`, or the ledger schema.
- Do not make token counts required.
- Do not add review-receiving or branch-completion skills in this PR.

## Constraints / Quality targets

- Keep `quality-gate/SKILL.md` concise; detailed delegated-run checks live in the reference checklist.
- Require explicit run identity (`run_id` or equivalent cited record), not latest/newest ledger selection.
- Missing validation is blocking; missing token telemetry alone is not blocking.
- Existing `make verify` must remain green.

## Context & Orientation

- Key paths:
  - `.agents/skills/quality-gate/SKILL.md`
  - `.agents/skills/quality-gate/references/quality-gate.md`
  - `.agents/runs/agent-runs.jsonl`
  - `scripts/judge_agent_run.py`
  - `evals/skill-behavior/quality-gate.json`
- Existing behavior:
  - `quality-gate` verifies branch artifacts and canonical commands, but does not yet mention delegated run ledger evidence.
  - PR #63 added `agent_run.py`, `judge_agent_run.py`, and `summarize_agent_runs.py`.
- Conventions to follow:
  - Final gate stays concise and does not duplicate deep workflow-contract review.
  - Agent-facing workflow changes need a workflow-contract review report with decision `submit`.
- Unknowns:
  - Behavior eval validation format will be finalized in PR 6; this PR seeds the cases only.

## Design

### Boundary sketch

- Components involved:
  - `quality-gate/SKILL.md`: short mandatory gate entrypoint.
  - `references/quality-gate.md`: detailed exit checklist.
  - `evals/skill-behavior/quality-gate.json`: future behavior eval seed cases.
- Boundary crossings:
  - Gate consumes `.agents/runs/agent-runs.jsonl` through an explicitly cited run ID.
  - Gate may run `python3 scripts/judge_agent_run.py --run-id <run_id> --require-accepted`.
- DTOs / interfaces:
  - PR #63 `agent_run` JSONL record and `judge_agent_run.py` judgment output.
- Error handling strategy:
  - Missing ledger, missing run record, missing validation, validation failure, or scope violation is `no-submit`.
  - `telemetry.status: not_collected` is acceptable when validation and scope evidence are present.

### Observability

- Logs: no runtime logs; the run ledger is evidence input.
- Metrics: none.
- Traces: none; this PR keeps OpenTelemetry out of scope.

### Testing strategy

- Structural validation:
  - `python3 scripts/validate_skills.py`
  - `python3 scripts/validate_skill_trigger_evals.py`
  - `python3 -m json.tool evals/skill-behavior/quality-gate.json`
- Ledger command smoke:
  - Use temp ledger records to show `judge_agent_run.py --require-accepted` passes when tokens are not collected but validation/scope pass.
  - Use temp ledger records to show missing validation fails.
- Full canonical chain:
  - `make verify`

## Milestones (high-level plan)

1. Record route, scope, acceptance, and complexity budget in this ExecPlan.
2. Update quality-gate entrypoint and reference checklist with delegated-run evidence rules.
3. Add behavior seed cases for accepted, missing-validation, missing-ledger, scope-violation, and token-not-collected scenarios.
4. Add workflow-contract report for the gate consuming ledger evidence.
5. Run targeted JSON/ledger checks and canonical verification, publish PR, and request review.

## Progress (WBS)

- [x] (P0) Merge PR #63 and sync `main` — deliverable: local `main` at `0133082` — verify: `git pull --ff-only origin main`.
- [x] (P1) Create branch and ExecPlan — deliverable: `codex/quality-gate-run-evidence`, this plan — verify: branch exists and plan path created.
- [x] (P2) Update quality-gate contract — deliverable: SKILL and reference changes — verify: `python3 scripts/validate_skills.py`.
- [x] (P3) Add behavior seed cases — deliverable: `evals/skill-behavior/quality-gate.json` — verify: `python3 -m json.tool`.
- [x] (P4) Add workflow-contract evidence — deliverable: `reports/workflow-contract-review/20260623-quality-gate-run-evidence.md` — verify: decision `submit`.
- [x] (P5) Verification and publication — deliverable: commit, push, draft PR — verify: https://github.com/shunta-sato/agent-instructions-playbook/pull/64 and green local verification.

## Route / Required Branches

- ExecPlan required: yes.
- Risk level: normal for an Agent-facing final gate workflow change.
- Default lane: required.
- Required branches:
  - `execution-plans`: multi-step PR and handoff-ready plan.
  - `skill-creator`: updating an existing skill.
  - `implementation-economy`: normal-risk workflow change.
  - `agent-workflow-contract-review`: quality-gate consumes run ledger evidence.
  - `quality-gate`: mandatory final submit gate.
- Non-triggered branches:
  - `design-balance`: no new module/class responsibility layout.
  - `function-boundary-governor`: no function/helper/API boundary change.
  - `architecture-decision-analysis`: PR sequence already chose run ledger as the evidence source.
  - `observability`: no runtime signals added.
  - embedded/concurrency/UI/legacy/staged-lowering branches: not applicable.

## Requirements / Acceptance

- EARS-1: When delegated/subagent/worker execution changed files, `quality-gate` shall require an explicit run ledger record for that delegated run.
- EARS-2: When a delegated run record is missing or cannot be selected by explicit identity, `quality-gate` shall decide `no-submit`.
- EARS-3: When delegated validation was not run, failed, or has no reproducible blocker, `quality-gate` shall decide `no-submit`.
- EARS-4: When token telemetry is missing but validation and scope evidence pass, `quality-gate` shall not decide `no-submit` for telemetry absence alone.
- EARS-5: When changed files exceed allowed files, `quality-gate` shall decide `no-submit`.

## Implementation Economy

- Changed files target: 5 tracked files or fewer.
- New classes/modules target: 0.
- New helpers/wrappers/adapters target: 0.
- New indirection layers target: 0.
- Rough line budget: under 250 net lines across skill/reference/eval/report/plan.
- Worth-its-weight decision: add a behavior seed file now because PR 5 needs reviewable pressure cases, but defer validation runner to PR 6 to keep scope small.

## Surprises & Discoveries

Record unexpected constraints, gotchas, and newly learned facts (with evidence when possible).

- 2026-06-23: The repository has no `evals/skill-behavior/` directory yet; PR 5 will seed the target file without adding a validator.

## Decision log

Record decisions and trade-offs (and why).

- 2026-06-23: Require explicit delegated run identity instead of latest-ledger selection.
  - Options considered: latest run in `.agents/runs/agent-runs.jsonl`; explicit `run_id`; no ledger command.
  - Chosen: explicit `run_id` or equivalent cited record.
  - Consequences: prevents stale or unrelated run records from satisfying final gate.
- 2026-06-23: Defer behavior eval validator to PR 6.
  - Options considered: add validator now; seed cases only.
  - Chosen: seed cases only.
  - Consequences: `make verify` remains unchanged while PR 6 can add schema validation.

## Handoff (update at every stop)

- Current branch / commit: `codex/quality-gate-run-evidence`, draft PR #64 open at https://github.com/shunta-sato/agent-instructions-playbook/pull/64.
- What is done: PR #63 merged; local `main` synced; branch and ExecPlan created; quality-gate skill/reference edits, behavior seed, workflow-contract report, targeted ledger checks, `make verify`, commit, push, and PR creation are complete.
- What is not done: review request, GitHub review response, PR ready-for-review transition, merge, PR 6.
- How to run: `make verify`.
- How to test: `python3 -m json.tool evals/skill-behavior/quality-gate.json`; targeted `judge_agent_run.py` ledger checks; `make verify`.
- Known risks / open questions: PR 6 must add behavior eval validation, so the behavior seed file is intentionally not part of current `make verify`.
- Next 1-3 steps: request review through ATLAS/ChatGPT, address review feedback if any, mark ready and merge on Approve.
- Pointers: `.agents/skills/quality-gate/`, `.agents/runs/agent-runs.jsonl`, `scripts/judge_agent_run.py`.

## Validation & Acceptance

- AC1: Delegated run without explicit ledger evidence is blocked.
  - Verification: behavior seed case and checklist text.
- AC2: Delegated run with missing validation is blocked.
  - Verification: behavior seed case and targeted ledger smoke.
- AC3: Missing token telemetry alone is allowed.
  - Verification: behavior seed case and targeted ledger smoke.
- AC4: Scope violation is blocked.
  - Verification: behavior seed case and `judge_agent_run.py` policy.
- AC5: Canonical verification stays green.
  - Verification: `make verify`.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: draft PR opened at https://github.com/shunta-sato/agent-instructions-playbook/pull/64.
- What went well: quality-gate now has a concise delegated-run evidence rule, while detailed pass/fail cases live in the reference and behavior seed.
- What went wrong: none.
- Follow-ups / tech debt tickets: PR 6 should add behavior eval validation for `evals/skill-behavior/quality-gate.json`.
