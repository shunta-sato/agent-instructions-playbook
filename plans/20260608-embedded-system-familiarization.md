# Embedded System Familiarization — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Add `embedded-system-familiarization` as a principal-level orchestration skill for broad embedded target-learning, optimization, and architecture-constraint formation.
- The skill coordinates existing concrete embedded skills rather than replacing them, so agents learn target behavior and hardware capability before optimizing, constraining, or making production claims.

## Scope

### In scope

- Add `.agents/skills/embedded-system-familiarization/SKILL.md`.
- Add templates for:
  - system familiarization pack
  - hardware capability map
  - workload map
  - bottleneck and margin map
  - architecture constraints
- Update concise handoffs in neighboring skills:
  - `dev-workflow`
  - `embedded-project-constitution`
  - `embedded-target-characterization`
  - `embedded-operating-envelope-discovery`
  - `embedded-nfr-calibration`
  - `architecture-decision-analysis`
  - `quality-gate`
- Add positive and negative trigger evals for the orchestrator boundary.
- Update README Skill Map and generated catalogs/indexes.

### Out of scope / non-goals

- No hardware-specific scripts.
- No ADC-specific content.
- No real-hardware requirement for repo validation.
- No replacement of target characterization, operating envelope discovery, calibration, NFR design, harness, hot-path, observer-effect, or gate skills.
- No trigger that makes the orchestrator run for every embedded task.

## Constraints / Quality targets

- Principle: understand the target before optimizing it; discover the envelope before constraining it; measure before claiming.
- Keep `SKILL.md` concise and move reusable forms into templates.
- Preserve precise trigger boundaries:
  - broad target-learning / unknown hardware capability / architecture optimization triggers the orchestrator
  - narrow calibration with current evidence does not
  - generic backend, schema, and doc-only work does not
- Validation must pass with the repo's canonical skill and generated-index commands.

## Context & Orientation

- Base: `origin/main` at `c8582e2`, after PR #45 merged the target-learning skills.
- Key paths:
  - `.agents/skills/embedded-system-familiarization/`
  - `.agents/skills/embedded-*/SKILL.md`
  - `.agents/skills/dev-workflow/SKILL.md`
  - `.agents/skills/architecture-decision-analysis/SKILL.md`
  - `.agents/skills/quality-gate/SKILL.md`
  - `evals/skill-triggers/*.json`
  - `README.md`
  - `AGENTS.md`
- Existing behavior: target characterization, operating envelope discovery, and NFR calibration exist as concrete skills, but no single orchestrator builds a System Familiarization Pack that maps hardware capability, workload, bottlenecks, margins, and architecture constraints.
- Dev-workflow route: high risk for playbook behavior because this adds a broad skill and modifies cross-skill routing/gate behavior.

## Design

### Boundary sketch

- `embedded-system-familiarization` decides what must be learned and which concrete skills to run.
- Concrete execution remains in existing embedded skills:
  - target facts -> `embedded-target-characterization`
  - normal/degraded/blackout behavior -> `embedded-operating-envelope-discovery`
  - budget values -> `embedded-nfr-calibration`
  - physical constraints -> `embedded-nfr-design`
  - measurement plans -> `embedded-nfr-harness-design`
  - hot paths -> `embedded-hot-path-review`
  - observer perturbation -> `embedded-observer-effect-review`
  - submit readiness -> `embedded-nfr-gate` then `quality-gate`
- Architecture choices with unknown target constraints route through familiarization before final `architecture-decision-analysis`.

### Observability

- This repository change adds reusable playbook artifacts only; no runtime observability instrumentation is introduced.
- The new pack template records observer effect, telemetry blackout, evidence paths, and claims blocked by missing evidence.

### Testing strategy

- Skill metadata validation: `python3 scripts/validate_skills.py`
- Trigger eval validation: `python3 scripts/validate_skill_trigger_evals.py`
- Inventory check: `python3 scripts/report_skill_inventory.py --check --format text`
- Generated index check: `python3 scripts/generate_agent_index.py --check`
- Canonical verification: `make build-release` and `make verify`

## Milestones (high-level plan)

1. Create the orchestrator skill and templates for the System Familiarization Pack.
2. Wire neighboring skills and gates with concise handoffs.
3. Add trigger evals that prove broad positive routing and near-miss negatives.
4. Update README and generated index/catalog.
5. Run validators and canonical verification, then publish the PR branch if requested by the workflow.

## Progress (WBS)

- [x] (P0) Read request and route workflow — deliverable: risk route and this ExecPlan — verify: attachment read.
- [x] (P1) Add skill and templates — deliverable: `embedded-system-familiarization` package — verify: `validate_skills.py` passed.
- [x] (P2) Update neighboring handoffs — deliverable: concise routing/gate edits — verify: diff review and validators passed.
- [x] (P3) Add trigger evals — deliverable: positive/negative orchestrator evals — verify: `validate_skill_trigger_evals.py` passed with 98 cases.
- [x] (P4) Update generated artifacts — deliverable: `README.md` and `AGENTS.md` updated — verify: `generate_agent_index.py --check` passed.
- [x] (P5) Run final verification — deliverable: green checks — verify: `make build-release` and `make verify` passed.
- [x] (P6) Publish PR — deliverable: commit, push, draft PR — verify: PR #46 opened.
- [x] (P7) Address PR review cleanup — deliverable: path naming consistency, artifact freshness/revisit fields, handoff status table, capability-to-constraint traceability, and current-familiarization negative eval — verify: validators passed with 99 eval cases.

## Surprises & Discoveries

- 2026-06-08: `origin/main` is at `c8582e2`, which includes merged PR #45 with the target-learning skills.
- 2026-06-08: Initial inventory before this change is 42 skills, 6 eval files, 296 eval references, 0 errors, and 7 existing broad-trigger warnings.
- 2026-06-08: After adding the orchestrator, inventory is 43 skills, 7 eval files, 332 eval references, 0 errors, and the same 7 existing broad-trigger warnings. The new skill has no broad-trigger risk flag.
- 2026-06-08: PR review requested small cleanup: align `bottleneck-margin-map.md` artifact paths, add artifact freshness/revisit conditions, make handoff closure structured, trace hardware capability to architecture constraints, and add a current-familiarization near-miss negative.
- 2026-06-08: After review cleanup, inventory is 43 skills, 7 eval files, 338 eval references, 0 errors, and the same 7 existing broad-trigger warnings.

## Decision log

- 2026-06-08: Add a dedicated orchestrator skill instead of only broadening existing embedded skills because the requested behavior changes routing and output contracts across target learning, hardware capability mapping, bottleneck/margin analysis, NFR calibration, and architecture constraints.
  - Options considered: update only `dev-workflow`; broaden `embedded-target-characterization`; add orchestrator.
  - Chosen: add orchestrator with precise negative triggers.
  - Consequences: clearer principal-level coordination while concrete execution remains in existing skills.

## Handoff (update at every stop)

- Current branch: `codex/embedded-system-familiarization`, PR #46.
- What is done: request read; branch and ExecPlan created; orchestrator skill, templates, handoffs, trigger evals, README map, generated index/catalog, validation, and review cleanup are complete. `make build-release` and `make verify` passed after review cleanup.
- What is not done: commit and push the review cleanup.
- How to run: use `python3` for scripts.
- How to test: `python3 scripts/validate_skills.py`, `python3 scripts/validate_skill_trigger_evals.py`, `python3 scripts/report_skill_inventory.py --check --format text`, `python3 scripts/generate_agent_index.py --check`, `make build-release`, `make verify`.
- Known risks / open questions: the orchestrator description must stay narrow enough to avoid broad-trigger warnings or accidental all-embedded routing.
- Next 1-3 steps: run final post-plan checks; commit review cleanup; push branch to update PR #46.
- Pointers: `.agents/skills/embedded-system-familiarization/SKILL.md`, `.agents/skills/embedded-system-familiarization/templates/system-familiarization.md`, `.agents/skills/dev-workflow/SKILL.md`, `evals/skill-triggers/embedded-system-familiarization.json`.

## Validation & Acceptance

- AC1: Broad embedded target-learning or optimization prompts trigger `embedded-system-familiarization`.
  - Verification: trigger eval positive cases.
- AC2: Narrow calibration-only prompt with current characterization does not trigger `embedded-system-familiarization`.
  - Verification: trigger eval negative case.
- AC3: Generic backend/schema/doc-only prompts do not trigger `embedded-system-familiarization`.
  - Verification: trigger eval negative cases.
- AC4: The skill provides a System Familiarization Pack template covering target identity, workload map, hardware capability map, operating envelope summary, bottleneck/margin map, NFR calibration inputs, architecture constraints, and handoffs.
  - Verification: template review.
- AC5: Specific embedded skills remain concrete execution skills; `embedded-system-familiarization` only orchestrates and routes.
  - Verification: `SKILL.md` workflow and neighboring handoffs.
- AC6: `quality-gate` checks system-familiarization artifacts when the skill is triggered.
  - Verification: quality-gate checklist update.
- AC7: `architecture-decision-analysis` routes to `embedded-system-familiarization` when choices depend on unknown hardware capability or bottleneck/margin data.
  - Verification: architecture skill/reference update.
- AC8: Skill validation and trigger eval scripts pass.
  - Verification: `python3 scripts/validate_skills.py`, `python3 scripts/validate_skill_trigger_evals.py`, `python3 scripts/report_skill_inventory.py --check --format text`, `python3 scripts/generate_agent_index.py --check`, `make build-release`, and `make verify` passed.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: PR #46 contains the embedded system familiarization orchestrator; review cleanup is in progress locally.
- What went well: Validators pass with 43 skills and 99 trigger eval cases, and inventory remains at 0 errors with no new broad-trigger warning for the orchestrator.
- What went wrong: Nothing blocking.
- Follow-ups / tech debt tickets: None for this scope.
