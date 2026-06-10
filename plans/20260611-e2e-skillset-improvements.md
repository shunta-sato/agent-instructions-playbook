# E2E Skillset Improvements - ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Improve the software-development skillset so agents can run end to end from requirements through implemented, verified changes without drifting into too much code, excess layering, giant classes, unclear names, or missed performance costs.
- Convert the review report into reviewable PRs without waiting for more confirmation.

## Scope

### In scope
- Add `implementation-economy`, `design-balance`, and `performance-review`.
- Add a normal/high-risk default lane in `dev-workflow`.
- Wire required evidence into `quality-gate` without making the gate a deep reviewer.
- Update neighboring skills so responsibilities and trigger boundaries remain clear.
- Keep study-note migration separate. PR #48 records the hold because the destination repository does not exist yet.

### Out of scope / non-goals
- Creating the destination study-note repository.
- Removing study-note skills from this repository before the destination repository exists and validates.
- Rewriting the full embedded NFR suite.
- Changing runtime application code; this repository change is playbook and validation content only.

## Constraints / Quality targets

- Latency / throughput / resource budgets: not applicable to this documentation-only repository change.
- Safety/security/privacy: no private study-note content or external credentials.
- Compatibility / rollout constraints: each PR must pass the canonical commands in `COMMANDS.md`.
- Operability: future agents must be able to tell which skills own complexity budget, responsibility layout, and generic performance review.

## Context & Orientation

- Key paths / entry points:
  - `.agents/skills/dev-workflow/SKILL.md`
  - `.agents/skills/dev-workflow/references/dev-workflow.md`
  - `.agents/skills/quality-gate/SKILL.md`
  - `.agents/skills/quality-gate/references/quality-gate.md`
  - `evals/skill-triggers/*.json`
  - `scripts/generate_agent_index.py`
  - `COMMANDS.md`
- Existing behavior:
  - `dev-workflow` routes only trigger-based branches; ordinary implementation can have little generation-time discipline.
  - Performance review is mostly embedded-only.
  - Generated skill indexes live in `AGENTS.md` and README generated catalog blocks.
- Conventions to follow:
  - Do not edit generated index/catalog blocks by hand.
  - Run `python scripts/generate_agent_index.py --write` after adding skills.
  - Add trigger eval seeds for broad/core skills.
- Unknowns (explicit):
  - CI result after remote PR creation is not available locally unless GitHub checks are queried later.

## Design

### Boundary sketch

- Components involved:
  - `implementation-economy`: implementation-size budget and post-implementation audit.
  - `design-balance`: module/class responsibility map and naming/responsibility alignment.
  - `performance-review`: generic non-embedded cost review for request/render/data-scaling paths.
  - `dev-workflow`: routes default lane and trigger branches.
  - `quality-gate`: checks required artifacts exist and commands pass.
- Boundary crossings:
  - No runtime service boundaries.
  - Skill-boundary changes must keep function, module, architecture, and performance skills distinct.
- DTOs / interfaces:
  - Skill output contracts are markdown tables and concise records.
- Error handling strategy:
  - If a PR cannot pass validation, fix the PR before creating the next stacked PR.
  - If a destination repo is missing, keep study-note cleanup blocked.

### Observability

- Logs: not applicable.
- Metrics: not applicable.
- Traces: not applicable.

### Testing strategy

- Unit tests: `make test-unit`.
- Integration tests: `make test-integration`.
- Static validation: `python scripts/validate_skills.py`, `python scripts/validate_skill_trigger_evals.py`, `python scripts/report_skill_inventory.py --check --format text`, `python scripts/generate_agent_index.py --check`, `git diff --check`.
- Full verification: `make verify`.

## Milestones (high-level plan)

1. Phase 1: add `implementation-economy` and `design-balance`; wire the default lane, evidence checks, neighboring boundaries, evals, and generated catalogs.
2. Phase 2: add `performance-review`; wire generic performance routing and embedded-hot-path boundary.
3. Phase 3: update remaining existing-skill goals, including explicit-only UI orchestration and template-authoring scope.
4. Push all branches and open draft PRs.

## Progress (WBS)

- [x] (P0) Phase 1 PR - deliverable: default lane plus `implementation-economy` and `design-balance` - verify: `make verify` passed on `codex/e2e-default-lane`.
- [ ] (P0) Phase 2 PR - deliverable: `performance-review` plus generic performance routing - verify: `make verify`.
- [ ] (P1) Phase 3 PR - deliverable: remaining skill goal alignment and explicit-only cleanup - verify: `make verify`.
- [ ] (P1) Publish all PRs - deliverable: draft PR URLs - verify: branches pushed and PRs open.

## Surprises & Discoveries

- 2026-06-11: `gh` is not installed locally. Use local `git` for branch/commit/push and the GitHub connector for PR creation.
- 2026-06-11: PR #48 already handles the study-note migration hold and remains independent from the main skillset improvement PR stack.
- 2026-06-11: Phase 1 validation passed with 45 skills, 105 trigger eval cases, 0 inventory errors, and 7 existing broad-trigger warnings.

## Decision log

- 2026-06-11: Use stacked PRs for main improvements.
  - Options considered:
    - One large PR with all report changes.
    - Fully independent PRs from `main`.
    - Stacked PRs by theme.
  - Chosen: stacked PRs by theme.
  - Consequences: each PR stays reviewable, while later PRs can depend on newly added skill names and generated catalogs without conflict.

## Handoff (update at every stop)

- Current branch / commit: `codex/e2e-default-lane`; uncommitted Phase 1 changes ready to commit.
- What is done: Phase 1 implementation and verification are complete.
- What is not done: Phase 1 push/PR creation, Phase 2, and Phase 3.
- How to run: use `COMMANDS.md`.
- How to test: `make verify` passed for Phase 1. Run `make verify` for each later PR branch.
- Known risks / open questions:
  - Generated index size may approach its cap after adding skills.
  - Broad-trigger warnings may increase if descriptions use overly broad words.
- Next 1-3 steps:
  - Commit, push, and open the Phase 1 draft PR.
  - Branch Phase 2 from Phase 1.
  - Add `performance-review` and rerun `make verify`.
- Pointers:
  - `README.md`
  - `AGENTS.md`
  - `.agents/skills/dev-workflow/SKILL.md`
  - `.agents/skills/quality-gate/SKILL.md`

## Validation & Acceptance

- AC1: Phase 1 PR adds generation-time discipline for code size and responsibility layout.
  - Verification: new skills exist, default lane routes them, evals reference them, and `make verify` passes.
- AC2: Phase 2 PR adds non-embedded performance review.
  - Verification: `performance-review` exists, dev-workflow/requirements/observability/embedded boundaries route it, evals reference it, and `make verify` passes.
- AC3: Phase 3 PR aligns remaining skill goals without deleting study-note assets prematurely.
  - Verification: affected skills document boundaries, generated catalogs are current, and `make verify` passes.

## Outcomes & Retrospective (fill when done)

- What shipped / merged:
- What went well:
- What went wrong:
- Follow-ups / tech debt tickets:
