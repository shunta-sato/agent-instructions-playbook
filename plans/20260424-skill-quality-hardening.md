# Skill Quality Hardening — ExecPlan

> Living plan for turning the 25-skill set into a measurable, self-checking skill system.

## Purpose / Big Picture

- Add live external-tool discovery rules, resource inventory checks, behavior-level eval expectations, and generated catalog support.
- Keep the repo small and software-development-specific while making the quality bar measurable.

## Scope

### In scope
- Update relevant skills so external tools and live systems are discovered before static recipes are trusted.
- Add a script-backed skill inventory/risk report.
- Extend trigger eval seeds with expected artifacts/decisions.
- Add generated README catalog support if it can coexist with the human role-based skill map.
- Wire deterministic checks into CI and README validation guidance.

### Out of scope
- Adding app-specific integration wrapper skills.
- Running a true LLM dispatch benchmark in this pass.

## Progress (WBS)

- [x] (P0) Define the quality-hardening implementation themes.
- [x] (P1) Add live external-tool discovery guidance to relevant workflows.
- [x] (P2) Add skill inventory/risk reporting script and CI/docs integration.
- [x] (P3) Extend eval seeds with behavior-level artifact/decision expectations.
- [x] (P4) Add generated human-readable README catalog support.
- [x] (P5) Validate all checks and update changelog/report/plan outcomes.
- [x] (P6) Commit if requested.

## Decision Log

- 2026-04-24: Harden through scripts/evals rather than more always-on prose.
  - Options considered: add more guidance to `AGENTS.md`; add deterministic scripts and conditional skill guidance.
  - Chosen: scripts/evals plus narrow skill edits.
  - Consequences: lower prompt bloat and stronger CI guardrails.
- 2026-04-24: Keep adapters collapsed.
  - Options considered: add active tool-specific skills for GitHub/CI/UI tools; keep live-discovery rules inside parent workflows.
  - Chosen: parent workflows with live-discovery steps.
  - Consequences: avoids growing the active trigger surface.

## Validation

- `python scripts/validate_skills.py`
- `python scripts/validate_skill_trigger_evals.py`
- `python scripts/report_skill_inventory.py --check`
- `python scripts/generate_agent_index.py --check`
- `git diff --check`
- `make verify` remains expected to fail until the template command system is initialized.

## Handoff

- Current base commit: `5a6868c`.
- Pre-existing uncommitted files at start: `README.md`, `CHANGELOG.md`.
- Implemented:
  - live external-tool discovery rules in relevant parent workflows
  - generated README skill catalog support
  - behavior-level eval expectations
  - `scripts/report_skill_inventory.py`
  - CI/docs/changelog/report integration
- Next: none; committed on request.
