# Embedded NFR Skill Program — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Add a reusable embedded NFR skill program so agents working on embedded, edge, target-local, daemon, logger, recorder, collector, or sampler work define physical footprint contracts before implementation.
- The user-provided goal requires agents to behave like senior embedded engineers: specify CPU, memory, wakeup, battery, flash wear, thermal, latency, degradation, and observer-effect constraints; design a measurement harness; and block production-readiness claims when evidence is missing.

## Scope

### In scope
- Add embedded NFR skills under `.agents/skills/`:
  - `embedded-nfr-design`
  - `embedded-nfr-harness-design`
  - `embedded-nfr-gate`
  - `embedded-hot-path-review`
  - `embedded-observer-effect-review`
  - `embedded-project-constitution`
- Add references/templates that produce concrete artifacts: NFR matrix, physical budgets YAML, target profile YAML, resource harness plan/report schema, gate report, hot-path report, observer-effect report, and project constitution skeletons.
- Update neighboring skills and references: `dev-workflow`, `requirements-engineering`, `quality-gate`, `observability`, and `project-initialization`.
- Add trigger eval seeds with positive and near-miss negative cases.
- Regenerate `AGENTS.md` and `README.md` generated skill catalogs.
- Address PR review refinements for cadence budgets, gate-friendly resource reports, constitution-only gate scope, runtime mode classification, hot-path budgets, and routing precision.

### Out of scope / non-goals
- Hardware-specific measurement scripts as required defaults.
- ADC-specific implementation details.
- Replacing `requirements-engineering`, `observability`, or `architecture-decision-analysis`.
- Making `quality-gate` carry deep embedded taxonomy; it should only verify required evidence and gate decisions.

## Constraints / Quality targets

- Resource discipline: the skills must enforce no-measurement-no-claim and battery_unknown != AC power.
- Cadence discipline: target-local polling/sampling cadence must be machine-readable in physical budgets and target profiles.
- Gate evidence: resource reports must expose structured budget-to-measurement comparisons for `embedded-nfr-gate`.
- Trigger precision: embedded NFR skills must trigger for always-on embedded physical-footprint work and avoid generic backend/web/schema-only work.
- Compatibility: keep skill names lowercase hyphenated and `SKILL.md` files under 500 lines.
- Validation: after changes, run skill validators, inventory check, generated index check, and canonical verification where practical.

## Context & Orientation

- Key paths:
  - `.agents/skills/*/SKILL.md`
  - `.agents/skills/*/references/`
  - `.agents/skills/*/templates/`
  - `evals/skill-triggers/*.json`
  - `scripts/validate_skills.py`
  - `scripts/validate_skill_trigger_evals.py`
  - `scripts/report_skill_inventory.py`
  - `scripts/generate_agent_index.py`
  - `AGENTS.md`, `README.md`
- Existing behavior: `dev-workflow` routes runtime behavior changes to `observability`; `quality-gate` checks triggered branch artifacts; no embedded physical-footprint-specific skill exists.
- Conventions to follow: concise frontmatter, narrow descriptions, heavy detail in references/templates, trigger eval coverage for broad/core skills, generated index/catalog updated by script.
- Dev-workflow route: high risk because this changes cross-skill routing and submit/no-submit behavior across the playbook.
- Unknowns: exact inventory check thresholds will be discovered by running `report_skill_inventory.py --check --format text`.

## Design

### Boundary sketch

- `embedded-nfr-design`: turns embedded physical-footprint risk into NFR matrix, target assumptions, budgets, degradation policy, measurement plan, and no-claim list.
- `embedded-nfr-harness-design`: converts budgets into target profiles, resource smoke scenarios, baseline/report schema, host fallback, and target smoke commands.
- `embedded-nfr-gate`: makes final submit/no-submit decision for embedded NFR artifacts and unmeasured claims.
- `embedded-hot-path-review`: reviews loop/polling/sampling/recorder hot paths for high-frequency overhead traps.
- `embedded-observer-effect-review`: reviews whether target-local observation changes scheduler, power, thermal, I/O, or memory behavior.
- `embedded-project-constitution`: generates project-start physical contract skeletons for embedded/edge repos.
- Neighboring skills hand off only when their own trigger evidence indicates embedded physical footprint risk.

### Observability

- No runtime observability is added to this repo.
- `observability` guidance will be updated so target-local instrumentation routes to embedded NFR and observer-effect review before adding always-on signals.

### Testing strategy

- Skill validation: `python3 scripts/validate_skills.py`.
- Trigger eval validation: `python3 scripts/validate_skill_trigger_evals.py`.
- Inventory check: `python3 scripts/report_skill_inventory.py --check --format text`.
- Generated index/catalog check: `python3 scripts/generate_agent_index.py --check`.
- Canonical chain per `COMMANDS.md`: `make build-debug`, `make build-release`, `make format`, `make lint`, `make analysis`, `make test-unit`, `make test-integration` or `make verify` if it covers the full chain.

## Milestones (high-level plan)

1. Add the six embedded NFR skills with concise workflows and heavy material in references/templates.
2. Update neighboring workflow skills so embedded physical footprint work routes to the new skills and final gates require their artifacts.
3. Add trigger eval seeds that prove positive embedded prompts route correctly and generic near-misses do not.
4. Regenerate generated indexes/catalogs and run validators.
5. Update this ExecPlan with final outcomes, handoff, and quality-gate evidence.
6. Address review-requested refinements and push a follow-up commit to PR #44.

## Progress (WBS)

Use a checkbox list. Each item should have a concrete deliverable and verification note.

- [x] (P0) Inspect objective, repo workflow, and canonical commands — deliverable: scope and route in this plan — verify: attached goal text and skill references read.
- [x] (P1) Add embedded NFR skills and templates — deliverable: six new skill directories — verify: `python3 scripts/validate_skills.py` passed.
- [x] (P2) Update neighboring workflow/gate skills — deliverable: edited skill docs/references — verify: review diffs and validators passed.
- [x] (P3) Add trigger eval coverage — deliverable: `evals/skill-triggers/embedded-nfr.json` — verify: `python3 scripts/validate_skill_trigger_evals.py` passed.
- [x] (P4) Regenerate catalogs and run final checks — deliverable: updated `AGENTS.md`/`README.md` and command results — verify: `python3 scripts/generate_agent_index.py --check`, `make build-release`, `make format`, and `make verify` passed.
- [x] (P5) Address PR review request changes — deliverable: cadence budgets, `budget_results`, constitution-only gate scope, runtime mode classification, hot-path allowed budgets, routing table, and extra evals — verify: `make build-release` and `make verify` passed.

## Surprises & Discoveries

Record unexpected constraints, gotchas, and newly learned facts (with evidence when possible).

- 2026-06-07: `references/<skill>.md` files are skill-local, not repo-root. Evidence: repo-root `sed references/dev-workflow.md` failed; `.agents/skills/dev-workflow/references/dev-workflow.md` exists.
- 2026-06-07: Local shell exposes `python3`, not `python`. Evidence: `python scripts/init_artifact.py ...` failed with `command not found`; `python3 scripts/init_artifact.py ...` succeeded.
- 2026-06-07: Inventory check reports seven broad-trigger warnings in existing mandatory skills, but no errors and no new warnings for the embedded NFR skills. Evidence: `python3 scripts/report_skill_inventory.py --check --format text` exited 0 with `errors=0 warnings=7`.
- 2026-06-07: PR review requested machine-readable cadence budgets and structured budget results so 10ms default polling cannot evade file-level gates. Evidence: attached review text from `/Users/satoshun/.codex/attachments/0320672e-d380-4604-ba79-00c7411681ac/pasted-text.txt`.

## Decision log

Record decisions and trade-offs (and why).

- 2026-06-07: Implement all six embedded NFR skills in this worktree because the active goal describes a skill program, not only a PR-A foundation.
  - Options considered: add only the core three skills from the recommended PR-A slice; add all six skills with trigger eval boundaries.
  - Chosen: add all six skills while keeping each narrow and artifact-driven.
  - Consequences: larger trigger surface, mitigated by explicit positive/near-miss negative eval seeds and short `SKILL.md` bodies.
- 2026-06-07: Keep project constitution separate from feature-level NFR gate because bootstrap skeletons may not have feature measurements yet.
  - Options considered: always require `embedded-nfr-gate` after constitution; let `quality-gate` validate constitution artifacts when no feature runtime or production claim exists.
  - Chosen: constitution-only path does not require feature-level NFR gate report.
  - Consequences: project bootstrap remains usable while feature submissions still require NFR gate evidence.

## Handoff (update at every stop)

- Current branch / commit: `codex/embedded-nfr-skill-program` at `bc5dbd1`; PR #44 exists and follow-up review changes are in the worktree.
- What is done: six embedded NFR skills added; neighboring workflow/gate handoffs updated; trigger evals added; generated index/catalog updated; PR opened; review refinements implemented and validated locally.
- What is not done: follow-up review commit has not yet been committed or pushed.
- How to run: use `python3` for repo scripts.
- How to test: run `python3 scripts/validate_skills.py`, `python3 scripts/validate_skill_trigger_evals.py`, `python3 scripts/report_skill_inventory.py --check --format text`, `python3 scripts/generate_agent_index.py --check`, `make build-release`, `make format`, and `make verify`.
- Known risks / open questions: none blocking. Inventory warnings are pre-existing broad mandatory-skill warnings.
- Next 1-3 steps: commit review fixes; push to PR #44.
- Pointers: `.agents/skills/dev-workflow/SKILL.md`, `.agents/skills/quality-gate/SKILL.md`, `README.md`, `evals/skill-triggers/core.json`, `scripts/generate_agent_index.py`.

## Validation & Acceptance

List the measurable acceptance criteria and how they are verified.

- AC1: Embedded logger/recorder/background daemon prompts route to embedded NFR design before implementation.
  - Verification: trigger eval positive cases mention embedded daemon/logger/recorder prompts and expected triggered skills.
- AC2: Skills produce physical budget and measurement harness plan artifacts, not prose-only guidance.
  - Verification: templates and `SKILL.md` output expectations include NFR matrix, physical budgets YAML, target profile YAML, resource harness plan, report schema, and gate report.
- AC3: `quality-gate` returns no-submit when embedded NFR was triggered but required embedded NFR artifacts are missing.
  - Verification: updated quality-gate checklist and trigger eval expected decisions.
- AC4: New skills do not trigger for unrelated generic web/backend/schema-only changes.
  - Verification: trigger eval near-miss negative cases.
- AC5: No-measurement-no-claim and battery_unknown != AC power are explicit rules.
  - Verification: rules appear in skills/templates and validation output is green.
- AC5b: Cadence budgets are machine-readable and resource reports include structured budget results.
  - Verification: `physical-budgets.yaml`, target profile templates, and `resource-report.schema.json` include cadence and `budget_results` fields.
- AC5c: Constitution-only bootstrap does not require feature-level NFR gate.
  - Verification: `embedded-nfr-gate` and `quality-gate` distinguish constitution-only artifact checks from feature-level NFR gate reports.
- AC6: `AGENTS.md` generated index and README generated catalog are up to date.
  - Verification: `python3 scripts/generate_agent_index.py --check`.
- AC7: All skill validation and trigger eval scripts pass.
  - Verification: `python3 scripts/validate_skills.py`, `python3 scripts/validate_skill_trigger_evals.py`, `python3 scripts/report_skill_inventory.py --check --format text`.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: PR #44 contains embedded NFR skill program additions and routing/gate integration; follow-up review fixes are validated locally and ready to push.
- What went well: The generated index stayed within limits; skill validation, trigger eval validation, inventory check, generated-index check, and canonical Makefile verification passed.
- What went wrong: The artifact helper uses `python` in its documentation, while this machine requires `python3`.
- Follow-ups / tech debt tickets: Optional future cleanup could reduce existing broad-trigger inventory warnings in older mandatory skills.
