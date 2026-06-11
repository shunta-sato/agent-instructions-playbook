# Study-Note Migration Hold — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Preserve the user's migration intent: study-note skills will move to a separate repository.
- Prevent premature deletion: the destination study-note repository does not exist yet, so this repository must keep the current study-note skills and validation assets until a verified destination is available.

## Scope

### In scope
- Track the temporary hold state for study-note skills in this repository.
- Identify the assets that must move together once the destination repository exists.
- Define the proof required before removing study-note assets from this repository.

### Out of scope / non-goals
- Creating the destination study-note repository in this change.
- Removing study-note skills, evals, checker scripts, Makefile targets, or quality-gate references before the destination exists.
- Reworking the study-note workflows while they are on migration hold.

## Constraints / Quality targets

- Latency / throughput / resource budgets: not applicable; this is repository documentation and workflow inventory.
- Safety/security/privacy: do not copy private study-note content into this repository while planning the migration.
- Compatibility / rollout constraints: keep current `make verify` behavior green until the destination repository replaces the study-note checker and trigger eval coverage.
- Operability: future agents must be able to determine from README and this plan that study-note removal is blocked by missing destination repo.

## Context & Orientation

- Key paths / entry points:
  - `.agents/skills/textbook-structured-content-workflow/SKILL.md`
  - `.agents/skills/textbook-learning-content-review/SKILL.md`
  - `.agents/skills/textbook-quality-gate/SKILL.md`
  - `.agents/skills/problem-framing-narrative-study-workflow/SKILL.md`
  - `.agents/skills/technical-essay-study-workflow/SKILL.md`
  - `.agents/skills/textbook-quality-gate/scripts/check_study_notes.py`
  - `evals/skill-triggers/study-note-workflows.json`
  - `Makefile`
  - `README.md`
  - `AGENTS.md`
- Existing behavior:
  - README and the generated catalogs list study-note skills as active repo-local skills.
  - `make test-unit` smoke-tests the study-note checker.
  - `make verify` depends on the checker and trigger eval validation.
- Conventions to follow:
  - Generated skill catalogs and `AGENTS.md` index are updated via `python scripts/generate_agent_index.py --write`, not by hand.
  - Canonical verification commands are defined in `COMMANDS.md`.
- Unknowns (explicit):
  - Destination repository path, name, remote, ownership, and validation command contract are not known yet.
  - Whether study-note checker tests should move intact or be split into source-repo and destination-repo checks is not known yet.

## Design

### Boundary sketch

- Components involved (and their roles):
  - Current repository: temporary owner of study-note skills and validation until migration destination exists.
  - Future study-note repository: eventual owner of study-note skills, checker, evals, and quality-gate semantics.
- Boundary crossings:
  - Repository-to-repository migration once destination exists.
- DTOs / interfaces:
  - Not applicable.
- Error handling strategy:
  - If the destination repo is missing, treat removal from this repo as blocked.
  - If migration verification fails in the destination repo, keep source assets here and document the failure.

### Observability

- Logs: not applicable.
- Metrics: not applicable.
- Traces: not applicable.

### Testing strategy

- Unit tests: keep current `make test-unit` passing while assets remain here.
- Integration tests: keep `make test-integration` and generated index checks passing.
- Manual verification:
  - Confirm destination repo exists before any deletion.
  - Confirm the destination repo can run its own checker and trigger eval validation before source cleanup.

## Milestones (high-level plan)

1. Mark the study-note skills as migration-held while the destination repo is missing.
2. Inventory all study-note assets that must move as a unit.
3. After the destination repo is created, copy/move the skills, checker, evals, reports, and command wiring into that repo.
4. Verify the destination repo's command contract, then remove source-repo references and regenerate catalogs/indexes here.
5. Run this repository's canonical verification after cleanup.

## Progress (WBS)

- [x] (P0) Record migration hold in this repository — deliverable: README note and this ExecPlan — verify: `rg -n "Migration status|destination study-note repository|migration hold" README.md plans/20260611-study-note-migration-hold.md`.
- [x] (P0) Inventory current study-note assets to keep — deliverable: Context & Orientation key paths — verify: paths are listed in this plan.
- [x] (P0) Verify current source repo remains green while assets stay here — deliverable: canonical verification result — verify: `make verify` passed on 2026-06-11.
- [ ] (P1) Create or identify destination repository — deliverable: destination path/remote/owner recorded here — verify: repo exists and has a command contract.
- [ ] (P1) Move study-note skills and checker into destination repository — deliverable: migrated files and generated indexes in destination repo — verify: destination validation passes.
- [ ] (P2) Remove source-repo study-note references after migration — deliverable: source repo no longer lists study-note skills/evals/checker commands — verify: source `make verify` passes.

## Surprises & Discoveries

- 2026-06-11: Destination repository is explicitly not available yet; source cleanup must wait. Evidence: user goal says study-note skills will move to another repository, but the destination does not exist now.
- 2026-06-11: Study-note assets are wired into validation, not just documentation. Evidence: `Makefile` compiles and smoke-tests `.agents/skills/textbook-quality-gate/scripts/check_study_notes.py`, and `evals/skill-triggers/study-note-workflows.json` validates trigger coverage.
- 2026-06-11: Current repo validation stays green with study-note assets retained. Evidence: `make verify` passed with 43 skills, 103 trigger eval cases, 0 inventory errors, and 7 existing broad-trigger warnings.

## Decision log

- 2026-06-11: Keep study-note assets active in this repository until the destination repository exists and passes validation.
  - Options considered:
    - Remove study-note skills now and accept missing destination.
    - Mark them deprecated without an execution plan.
    - Keep them active and document a migration hold.
  - Chosen: keep them active and document a migration hold.
  - Consequences: current validation remains intact, and future cleanup has an explicit prerequisite instead of relying on memory.

## Handoff (update at every stop)

- Current branch / commit: `codex/controlled-hardware-operating-points`; uncommitted changes exist.
- What is done: README now states that study-note skills are planned for a separate repository but remain here until that repo exists; this ExecPlan captures the hold, inventory, milestones, and verification criteria.
- What is not done: destination repo creation, migration, and source cleanup.
- How to run: use the commands in `COMMANDS.md`.
- How to test: `make verify` passed on 2026-06-11. For targeted checks, run `python scripts/generate_agent_index.py --check`, `python scripts/validate_skills.py`, `python scripts/validate_skill_trigger_evals.py`, and `python scripts/report_skill_inventory.py --check --format text`.
- Known risks / open questions:
  - Destination repo path and command contract are unknown.
  - Source cleanup must not happen until destination validation passes.
- Next 1-3 steps:
  - Create or identify the destination study-note repository.
  - Move study-note skills/checker/evals as a coherent package.
  - Regenerate and verify both repositories before deleting source assets.
- Pointers:
  - `README.md`
  - `Makefile`
  - `evals/skill-triggers/study-note-workflows.json`
  - `.agents/skills/textbook-quality-gate/scripts/check_study_notes.py`

## Validation & Acceptance

- AC1: Future agents can see that study-note skills are migration-held, not ready for deletion.
  - Verification: README contains the migration status and links to this plan.
- AC2: The plan records that the destination repository is missing.
  - Verification: Scope, Context & Orientation, and Handoff state that destination repo details are unknown.
- AC3: The plan identifies assets that must remain until migration.
  - Verification: Context & Orientation lists study-note skills, checker script, trigger evals, Makefile, README, and AGENTS index.
- AC4: Source cleanup is blocked until destination validation exists.
  - Verification: WBS and Decision log require destination repo creation and validation before source removal.

## Outcomes & Retrospective (fill when done)

- What shipped / merged:
- What went well:
- What went wrong:
- Follow-ups / tech debt tickets:
