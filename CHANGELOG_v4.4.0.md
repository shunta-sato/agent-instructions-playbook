# Changelog v4.4.0

## Added
- Added ExecPlan guidance via new root `PLANS.md` and `plans/` docs (`plans/README.md`, `plans/_template_execplan.md`) to standardize planning, WBS tracking, progress reporting, and handoff.
- Added new `execution-plans` skill under `.agents/skills/execution-plans/` with a dedicated reference doc.
- Added new prompts:
  - `.github/prompts/execution-plans.prompt.md`
  - `.github/prompts/status-update.prompt.md`

## Changed
- Updated `dev-workflow` reference to include an explicit **0.5 ExecPlan decision** gate before editing code for complex/long-running work.
- Updated `quality-gate` reference to include ExecPlan completion checks (plan link + WBS/decision/discovery/handoff freshness).
- Updated root docs (`AGENTS.md`, `README.md`, `REFERENCES.md`) to include ExecPlan entry points and references.
- Updated agent index generator to include `PLANS.md` and `plans/README.md` in core docs and map `status-update` prompt to `execution-plans`.

## Regenerated
- Regenerated mirrored GitHub skills and AGENTS index after adding the new skill/prompt and metadata updates.
