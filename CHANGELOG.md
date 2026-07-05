# Changelog

All notable changes to this repository are documented in this file.

## v4.8.0

### Added
- Added the `project-structure` skill: generative physical-layout guidance owning the canonical structure budget (source file ≤ 400 lines, entrypoint logic ≤ 150 lines, Rust inline tests ≤ 200 lines/file), with a Rust layout reference (`main.rs`/`lib.rs` split, unit vs integration test placement).
- Added `scripts/check_structure.py`, a stdlib-only state-based structure-budget checker, plus unit tests.
- Added `evals/skill-triggers/project-structure.json` trigger eval seeds, including anti-trigger guards against embedded skill co-firing on plain CLI work.
- Added `reports/skillset-review-20260705.md` strategic review (root cause of the monolithic `main.rs` incident and the Claude Code / mixed-model roadmap).

### Changed
- `dev-workflow`: added a mandatory structure watch at all risk levels (state-based, fires on accumulated file size even for tiny appends); the low-risk lane skip now also requires a passing structure check; added a `project-structure` trigger branch.
- `quality-gate`: added a structural exit check (1b) independent of triggered branches — unresolved `check_structure.py` findings are `no-submit` without an explicit bounded waiver.
- `AGENTS.md`: the smallest-safe-change principle is now bounded by the structure budget; required splits are part of the smallest correct change, not broad cleanups.
- `implementation-economy`: required structure-budget splits are complexity placement, not new abstraction, and never count against the complexity budget.
- `test-driven-development`: tests are placed by `project-structure` conventions and never accumulate in entrypoint files.

## v4.7.0

### Added
- Added a README skill quality bar for future skill additions and rewrites.
- Added a generated README skill catalog that is refreshed by `scripts/generate_agent_index.py`.
- Added behavior-level eval expectations (`expected_artifacts`, `expected_decisions`, `expected_evidence`, `expected_output_contains`) to skill trigger eval seeds.
- Added `scripts/report_skill_inventory.py` for deterministic skill inventory, eval coverage, and broad-trigger risk reporting.

### Changed
- Expanded README onboarding with a quick start and human-readable skill map grouped by workflow role.
- Added live external-tool discovery requirements to relevant workflows before static examples are trusted.
- Updated CI to validate trigger evals, skill inventory, and generated indexes together.

## v4.6.0

### Changed
- Reduced the active repo-local skill set from 38 skills to 25 by merging thin adapters and overlapping template/review skills into parent skills.
- Merged architecture/modularity guidance into `code-smells-and-antipatterns` as diff-focused maintainability references.
- Merged requirements docs, EARS planning, and ISO 25010 NFR guidance into `requirements-engineering`.
- Merged deployment, infrastructure, data-analysis, and library/API template skills into `playbook-template-authoring`.
- Merged UIUX and visual-regression platform adapter skills into `uiux-core` and `visual-regression-testing`.
- Tightened trigger descriptions for `observability`, `error-handling`, `code-readability`, and `uidesign-orchestrator`.

### Added
- Added `reports/skillset-review-20260424.md` with the 38-skill audit and consolidation rationale.
- Added `evals/skill-triggers/core.json` with 35 trigger/near-miss eval seed cases.
- Added `scripts/validate_skill_trigger_evals.py` and wired it into CI.

## v4.5.0

### Changed
- Made `.agents/skills` the single repo-local Agent Skills source for both Codex and GitHub Copilot.
- Removed the duplicated `.github/skills` mirror and the mirror-sync script/check.
- Updated the generated `AGENTS.md` index metadata to show Codex (`$skill`) and Copilot (`/skill`) explicit invocation forms.
- Included `*-template` skills in the generated `AGENTS.md` index instead of hiding installed skills.
- Moved non-standard `inputs` / `outputs` frontmatter from `tonemana-*` skills into the skill bodies.

### Added
- Added `scripts/validate_skills.py` to validate Agent Skills frontmatter, naming, uniqueness, size, and single-source layout.
- Updated CI to validate skills and the generated agent index.

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
