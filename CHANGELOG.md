# Changelog

All notable changes to this repository are documented in this file.

## v4.4.0

### Added
- Added ExecPlan guidance via new root `PLANS.md` and `plans/` docs (`plans/README.md`, `plans/_template_execplan.md`) to standardize planning, WBS tracking, progress reporting, and handoff.
- Added new `execution-plans` skill under `.agents/skills/execution-plans/` with a dedicated reference doc.
- Added new prompts:
  - `.github/prompts/execution-plans.prompt.md`
  - `.github/prompts/status-update.prompt.md`

### Changed
- Updated `dev-workflow` reference to include an explicit **0.5 ExecPlan decision** gate before editing code for complex/long-running work.
- Updated `quality-gate` reference to include ExecPlan completion checks (plan link + WBS/decision/discovery/handoff freshness).
- Updated root docs (`AGENTS.md`, `README.md`, `REFERENCES.md`) to include ExecPlan entry points and references.
- Updated agent index generator to include `PLANS.md` and `plans/README.md` in core docs and map `status-update` prompt to `execution-plans`.

### Regenerated
- Regenerated mirrored GitHub skills and AGENTS index after adding the new skill/prompt and metadata updates.

## v4.3.2

### Highlights
- Added `staged-lowering` skill: IR/DSL-first, multi-pass lowering workflow for strict-constraint implementations with per-pass verification logs.
- Integrated staged lowering into `dev-workflow` and `quality-gate` as a conditional mandatory step when strict constraints apply.
- Added VS Code prompt file `/staged-lowering` for consistent invocation.
- Updated REFERENCES with AscendCraft (arXiv:2601.22760).

## v4.3.1

### Highlights
- Migrated Codex skills path from `.codex/skills` to `.agents/skills` as the repository source of truth.
- Added `scripts/sync_agent_skills.py` to sync `.agents/skills` into `.github/skills` (write/check modes).
- Updated CI to enforce skills sync before AGENTS index checks.
- Updated AGENTS/README/Copilot instructions and regenerated the AGENTS index for the new layout.

## v4.3.0

### Added
- New Codex skills for concurrency planning and verification:
  - `concurrency-core`
  - `concurrency-ros2`
  - `concurrency-android`
  - `thread-safety-tooling`
- Concurrency plan template asset for reuse.

### Updated
- `dev-workflow` now includes a mandatory Concurrency & Performance check with skill invocation rules.
- `quality-gate` includes a Concurrency gate checklist.
- `nfr-iso25010` adds performance metric examples and ties concurrency to measurable targets.
- `observability` adds concurrency-specific logging/metric guidance.
- `README.md` and `REFERENCES.md` mention the new skills and sources.

## v4.2.2

### Added
- New `bug-investigation-and-rca` skill in both `.codex/skills/` and `.github/skills/`, including:
  - deterministic Bug Report (RCA) output format,
  - anti-cheat evidence-first workflow,
  - references with Five Whys, prevention taxonomy, and tool selection matrix,
  - optional standalone bug report template.
- New Copilot prompt: `.github/prompts/bug-report.prompt.md`.

### Updated
- `dev-workflow` (Codex + GitHub skills): added conditional Bugfix mode enforcement before implementation.
- `quality-gate` (Codex + GitHub skills): added required bugfix evidence/report checklist and workaround-only guardrails.
- Docs updated in `AGENTS.md`, `README.md`, `.github/copilot-instructions.md`, and `REFERENCES.md` for triggers and usage guidance.

## v4.2.1

### Added
- New skill: `code-smells-and-antipatterns` (Codex + Copilot mirror) with references and finding template.
- Copilot prompt: `/review-antipatterns`.
- Documentation updates for smells/anti-patterns sources.

### Updated
- `dev-workflow` includes an optional smells/anti-patterns scan for structural changes.
- `quality-gate` adds a smells/anti-patterns checklist item.
- `README.md`, `AGENTS.md`, and Copilot instructions list the new skill/prompt.
