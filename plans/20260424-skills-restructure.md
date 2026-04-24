# Skills Restructure — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Align this playbook with current Agent Skills guidance for OpenAI Codex and GitHub Copilot.
- Reduce duplicated skill maintenance while keeping project skills usable from both agents.
- Add deterministic validation so skill metadata and generated indexes do not drift.

## Scope

### In scope
- Treat `.agents/skills` as the single project-skill directory for both Codex and GitHub Copilot.
- Remove the duplicated `.github/skills` mirror and its sync workflow.
- Update documentation, Copilot instructions, and CI to match the single-source layout.
- Add local skill validation for Agent Skills frontmatter, names, descriptions, and index freshness.

### Out of scope / non-goals
- Rewriting the content of all 38 skills.
- Changing `.github/prompts` semantics.
- Packaging this repository as a Codex plugin.
- Changing user-level or admin-level skill locations.

## Constraints / Quality targets

- Compatibility / rollout constraints: `.agents/skills` must remain the canonical repo path because Codex scans it and GitHub Copilot supports it for project skills.
- Operability: CI must fail when skill metadata or `AGENTS.md` index drift.
- Maintainability: avoid two physical copies of each skill.
- Safety/security/privacy: do not pre-approve shell execution via `allowed-tools` unless a skill explicitly requires and documents the risk.

## Context & Orientation

- Key paths / entry points:
  - `AGENTS.md`: always-loaded Codex guidance and generated skill index.
  - `.agents/skills/*/SKILL.md`: current canonical skill source.
  - `.github/skills/*/SKILL.md`: generated mirror; currently identical to `.agents/skills`.
  - `.github/copilot-instructions.md`: Copilot always-on repository guidance.
  - `.github/workflows/agent-index.yml`: CI checks index and mirror drift.
  - `scripts/generate_agent_index.py`: builds `AGENTS.md` index from `.agents/skills`.
  - `scripts/sync_agent_skills.py`: mirror sync script to remove.
- Existing behavior:
  - 38 skills exist under both `.agents/skills` and `.github/skills`.
  - `scripts/sync_agent_skills.py --check` reports the directories are in sync.
  - `scripts/generate_agent_index.py --check` reports the index is current.
- Conventions to follow:
  - Keep `AGENTS.md` short; detailed workflows stay in skills/references.
  - Skill body is loaded only when selected; metadata must be precise.
  - Reference files and templates should be loaded only when relevant.
- Unknowns:
  - Whether all downstream users expect `.github/skills`; mitigate by documenting why `.agents/skills` is now the single cross-agent location.

## Design

### Boundary sketch

- Source skills: `.agents/skills`.
- Generated always-on index: `AGENTS.md`.
- Copilot prompts/instructions: `.github/prompts`, `.github/instructions`, `.github/copilot-instructions.md`.
- Validation scripts:
  - `scripts/validate_skills.py`: structural validation of `.agents/skills` against current Agent Skills constraints.
  - `scripts/generate_agent_index.py --check`: generated index freshness.

### Observability

- CI logs should clearly state which validation failed and how to fix it.
- Validation errors must include the offending file path.

### Testing strategy

- Run `python scripts/validate_skills.py`.
- Run `python scripts/generate_agent_index.py --check`.
- Run a file-system check that no `.github/skills` mirror remains.
- Do not run `make verify`: this template is intentionally uninitialized and the Makefile gates all targets.

## Milestones (high-level plan)

1. Record current official guidance and local inventory in this plan.
2. Remove `.github/skills` mirror and sync script/check.
3. Add deterministic skill validation and wire it into CI.
4. Update docs and always-on instructions for the single-source skill layout.
5. Run targeted validation and update handoff/outcomes.

## Progress (WBS)

- [x] (P0) Research current Codex, GitHub Copilot, and Agent Skills guidance — deliverable: documented design basis — verify: cited sources in final response.
- [x] (P1) Inventory current skill directories and sync state — deliverable: local facts above — verify: `sync_agent_skills.py --check` and counts showed 38/38.
- [x] (P2) Remove duplicated `.github/skills` mirror and obsolete sync script — deliverable: single physical skill tree — verify: `test ! -d .github/skills`.
- [x] (P3) Add skill validation and CI wiring — deliverable: validator script + workflow update — verify: `python scripts/validate_skills.py`.
- [x] (P4) Update docs and generated index — deliverable: docs reflect `.agents/skills` as cross-agent path — verify: `python scripts/generate_agent_index.py --check`.
- [x] (P5) Final quality gate — deliverable: gate notes in final response — verify: command results recorded below.

## Surprises & Discoveries

- 2026-04-24: GitHub Copilot now supports project skills in `.agents/skills` as well as `.github/skills` and `.claude/skills`, so a separate `.github/skills` mirror is not required for Copilot compatibility.
- 2026-04-24: Codex documentation says duplicate skill names are not merged; duplicate physical skill trees increase selector noise and maintenance risk.

## Decision log

- 2026-04-24: Use `.agents/skills` as the single repo-local skill location.
  - Options considered: keep `.github/skills` mirror; move to `.github/skills`; keep both with sync.
  - Chosen: `.agents/skills` only.
  - Consequences: one source of truth, lower CI complexity, compatible with both Codex and Copilot per current docs.
- 2026-04-24: Replace mirror-sync CI with structural validation.
  - Options considered: rely only on generated index check; add external `skills-ref`; add local validator.
  - Chosen: local validator.
  - Consequences: no new dependency, clearer failures, easy to run in CI.
- 2026-04-24: Include `*-template` skills in the generated `AGENTS.md` index.
  - Options considered: keep hiding template skills; remove template skills; include all installed skills.
  - Chosen: include all installed skills.
  - Consequences: the index reflects actual discoverable skills and avoids a hidden-skill mismatch.

## Handoff (update at every stop)

- Current branch / commit: uncommitted changes exist on `main`.
- What is done: research, inventory, ExecPlan, mirror removal, validator, CI, docs, generated index updates, and targeted validation.
- What is not done: no commit was created.
- How to run:
  - `python scripts/validate_skills.py`
  - `python scripts/generate_agent_index.py --check`
- How to test: run the targeted commands above.
- Known risks / open questions: downstream tooling may still hardcode `.github/skills`; docs now call out the migration.
- Next 1-3 steps:
  1. Review and commit the restructuring change.
  2. Watch CI for the new validator step.
  3. Decide later whether any broad domain skills should be split or retired based on real trigger/eval data.
- Pointers (files/dirs to read first):
  - `AGENTS.md`
  - `.agents/skills`
  - `.github/copilot-instructions.md`
  - `.github/workflows/agent-index.yml`
  - `scripts/generate_agent_index.py`

## Validation & Acceptance

- AC1: Only one physical project-skill tree remains.
  - Verification: `test ! -d .github/skills`.
- AC2: Skill metadata follows current Agent Skills constraints.
  - Verification: `python scripts/validate_skills.py`.
- AC3: Generated `AGENTS.md` index is current.
  - Verification: `python scripts/generate_agent_index.py --check`.
- AC4: Docs explain Codex/Copilot invocation and source layout.
  - Verification: inspect updated `README.md`, `AGENTS.md`, `.github/copilot-instructions.md`, `REFERENCES.md`.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: pending user review; uncommitted local changes restructure skill layout and validation.
- What went well: current official docs allowed replacing the duplicate `.github/skills` mirror with `.agents/skills` only; validation found and fixed the two non-standard frontmatter cases.
- What went wrong: `make verify` remains intentionally unavailable because this repository template is uninitialized (`COMMANDS.md` contains `<fill>`).
- Follow-ups / tech debt tickets: add trigger evals for high-traffic skills before deleting or merging domain skills beyond the physical mirror removal.
