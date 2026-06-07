# Embedded Target Characterization & NFR Calibration — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Add a pre-NFR target-learning layer to the embedded NFR playbook so agents characterize the target, discover the operating envelope, and calibrate budgets before treating embedded physical NFRs as production constraints.
- The prior embedded NFR skill program defines budgets, harnesses, gates, hot-path review, observer-effect review, and project constitution. This change fills the earlier step: learn the target before budgeting.

## Scope

### In scope
- Add three skills:
  - `embedded-target-characterization`
  - `embedded-operating-envelope-discovery`
  - `embedded-nfr-calibration`
- Add templates and report schemas for target characterization, operating envelope discovery, and calibrated NFR provenance.
- Update neighboring embedded and workflow skills:
  - `embedded-project-constitution`
  - `embedded-nfr-design`
  - `embedded-nfr-harness-design`
  - `embedded-nfr-gate`
  - `dev-workflow`
  - `requirements-engineering`
  - `architecture-decision-analysis`
  - `quality-gate`
- Add trigger eval seeds for positive and near-miss cases.
- Update README Skill Map and generated catalogs/indexes.

### Out of scope / non-goals
- No ADC-specific content.
- No hardware-specific measurement scripts.
- No replacement of existing embedded NFR design/harness/gate skills.
- No all-embedded-skills-trigger-unconditionally route.
- No real-hardware requirement for repository validation.

## Constraints / Quality targets

- Principle: characterize before budgeting, calibrate before constraining, measure before claiming.
- Production NFR budgets require provenance, or they must be explicit unknown/provisional values.
- Keep `SKILL.md` bodies concise; put forms and schema detail in templates.
- Preserve trigger precision so generic schema/docs/backend prompts do not trigger target characterization.
- Validation must pass with the repository's existing skill and generated-index scripts.

## Context & Orientation

- Current base: `origin/main` at `491fb8f`, after the embedded NFR skill program was merged.
- Key paths:
  - `.agents/skills/embedded-*/SKILL.md`
  - `.agents/skills/*/templates/`
  - `evals/skill-triggers/*.json`
  - `README.md`
  - `AGENTS.md`
  - `scripts/validate_skills.py`
  - `scripts/validate_skill_trigger_evals.py`
  - `scripts/report_skill_inventory.py`
  - `scripts/generate_agent_index.py`
- Existing behavior: embedded NFR routes can define budgets, harnesses, and gates, but do not yet require target characterization or budget provenance before production constraints.
- Dev-workflow route: high risk because this adds new skills and changes cross-skill routing/gate behavior.

## Design

### Boundary sketch

- `embedded-target-characterization`: discovers target identity, measurement surfaces, workload catalog, idle/nominal baselines, unavailable signals, safety constraints, and confidence.
- `embedded-operating-envelope-discovery`: explores normal, peak, near-boundary, degraded, observer-on/off, recovery, and blackout behavior within safe limits.
- `embedded-nfr-calibration`: derives or revises budgets from characterization/envelope evidence, with source, evidence, confidence, rationale, and revisit conditions.
- Existing `embedded-nfr-design` consumes calibration output before finalizing production budgets.
- Existing `embedded-nfr-harness-design` distinguishes discovery harnesses from gate harnesses.
- Existing `embedded-nfr-gate` and `quality-gate` check characterization/calibration/provenance for production claims.

### Observability

- This repo change adds playbook artifacts only; no runtime observability instrumentation is added.
- The new envelope skill includes telemetry blackout and observer-on/off scenarios as review artifacts.

### Testing strategy

- Skill metadata validation: `python3 scripts/validate_skills.py`
- Trigger eval validation: `python3 scripts/validate_skill_trigger_evals.py`
- Inventory check: `python3 scripts/report_skill_inventory.py --check --format text`
- Generated index check: `python3 scripts/generate_agent_index.py --check`
- Canonical verification: `make build-release` and `make verify`

## Milestones (high-level plan)

1. Add the three target-learning skills with concise workflows and reusable templates/schemas.
2. Wire existing embedded NFR and workflow skills to require characterization/calibration when target facts or budget provenance are missing.
3. Add trigger evals for missing target profile, unknown envelope, budget calibration, logger blackout, and near-miss negatives.
4. Regenerate README/AGENTS generated catalogs and run validators.
5. Commit, push, and open a draft PR.

## Progress (WBS)

Use a checkbox list. Each item should have a concrete deliverable and verification note.

- [x] (P0) Read user request and route workflow — deliverable: this ExecPlan and high-risk route — verify: attached request read.
- [x] (P1) Add new skill directories — deliverable: three `SKILL.md` files plus templates/schemas — verify: `validate_skills.py` passed.
- [x] (P2) Update neighboring skills — deliverable: handoff and gate edits — verify: diff review and validators passed.
- [x] (P3) Add trigger evals — deliverable: `evals/skill-triggers/embedded-target-learning.json` — verify: `validate_skill_trigger_evals.py` passed.
- [x] (P4) Regenerate catalogs/indexes — deliverable: updated `README.md` and `AGENTS.md` — verify: `generate_agent_index.py --check` passed.
- [x] (P5) Run final verification — deliverable: green checks — verify: `make build-release` and `make verify` passed.
- [x] (P6) Publish PR — deliverable: commit, push, draft PR — verify: PR #45 opened.
- [x] (P7) Address PR review must-fixes — deliverable: broadened calibrated budgets, reordered embedded routing, safe-boundary envelope rules, stricter schemas, source/claim rules, template-budget eval — verify: `make build-release` and `make verify` passed with 91 trigger eval cases.

## Surprises & Discoveries

Record unexpected constraints, gotchas, and newly learned facts (with evidence when possible).

- 2026-06-07: `origin/main` advanced to `491fb8f` after the embedded NFR skill program merge, so this work starts from `origin/main`, not the previous PR branch.
- 2026-06-07: Adding three skills keeps generated index under the default 8192-byte limit. Evidence: `python3 scripts/generate_agent_index.py --write` and `--check` succeeded.
- 2026-06-07: Inventory check remains at seven broad-trigger warnings from existing mandatory skills, with zero errors. Evidence: `python3 scripts/report_skill_inventory.py --check --format text` exited 0.
- 2026-06-07: PR review requested changes focused on calibrated budget coverage, routing order, operating-envelope safety preconditions, schema strictness, source/claim rules, staleness, and template-budget production-claim regression coverage.
- 2026-06-07: PyYAML is not installed in this local environment, so YAML template syntax was checked with Ruby/Psych instead.

## Decision log

Record decisions and trade-offs (and why).

- 2026-06-07: Do not add the optional `embedded-system-familiarization` orchestrator in this PR because the request recommends keeping the first PR to three skills unless trigger surface remains manageable.
  - Options considered: add orchestrator now; mention future candidate only; omit entirely.
  - Chosen: omit orchestrator from active skill catalog for this PR.
  - Consequences: fewer trigger surfaces, clearer routing through the three concrete skills.
- 2026-06-07: Address the three merge-blocking review items in this PR and include low-risk related hardening while the same files are open.
  - Options considered: only the three must-fixes; include all follow-ups; include must-fixes plus small schema/eval/gate hardening.
  - Chosen: include must-fixes plus structured boundary/blackout schema fields, target characterization freshness fields, claim-source rules, staleness gate text, and a template-budget production-claim eval.
  - Consequences: stronger governance artifacts without adding new skills or hardware-specific scripts.

## Handoff (update at every stop)

- Current branch: `codex/embedded-target-characterization`, PR #45.
- What is done: request read; branch and ExecPlan created; three skills, templates, schemas, routing/gate updates, trigger evals, and generated catalogs are implemented, reviewed, and hardened for the requested PR changes.
- What is not done: none for the current review-fix scope.
- How to run: use `python3` for scripts.
- How to test: `python3 scripts/validate_skills.py`, `python3 scripts/validate_skill_trigger_evals.py`, `python3 scripts/report_skill_inventory.py --check --format text`, `python3 scripts/generate_agent_index.py --check`, `ruby -e 'require "yaml"; ...'`, `make build-release`, `make verify`.
- Known risks / open questions: generated agent index size may need concise short descriptions; trigger surface must not imply all embedded skills always open.
- Next 1-3 steps: push the review-fix commit to PR #45; wait for review.
- Pointers: `.agents/skills/embedded-nfr-design/SKILL.md`, `.agents/skills/embedded-nfr-gate/SKILL.md`, `.agents/skills/dev-workflow/references/dev-workflow.md`, `evals/skill-triggers/embedded-nfr.json`.

## Validation & Acceptance

List the measurable acceptance criteria and how they are verified.

- AC1: Missing embedded target profile or unknown measurement surfaces route to `embedded-target-characterization` before `embedded-nfr-design` finalizes budgets.
  - Verification: trigger eval and skill routing text.
- AC2: Normal/degraded/failure-adjacent discovery prompts route to `embedded-operating-envelope-discovery`.
  - Verification: trigger eval and skill routing text.
- AC3: Budget derivation from target baselines routes to `embedded-nfr-calibration`.
  - Verification: trigger eval and calibration output contract.
- AC4: `embedded-nfr-design` does not finalize production budgets when target characterization is missing unless budgets are provisional/unknown.
  - Verification: updated design skill preconditions.
- AC5: `embedded-nfr-gate` checks budget provenance and blocks or limits placeholder_unknown production budgets.
  - Verification: updated gate rules.
- AC6: `quality-gate` requires characterization/calibration artifacts when production-ready or resource-safety claims depend on embedded NFRs.
  - Verification: updated quality-gate checklist.
- AC7: Generic backend/schema/docs near-misses do not trigger target characterization.
  - Verification: trigger eval negative cases.
- AC8: Validation commands pass.
  - Verification: `python3 scripts/validate_skills.py`, `python3 scripts/validate_skill_trigger_evals.py`, `python3 scripts/report_skill_inventory.py --check --format text`, `python3 scripts/generate_agent_index.py --check`, `make build-release`, and `make verify` passed.
- AC9: Template-copied budgets cannot support production-ready or battery-safe claims without target evidence.
  - Verification: `embedded-template-budget-production-claim` trigger eval and budget provenance rules.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: PR #45 contains the embedded target-learning layer and the review-fix hardening for calibrated budget coverage, routing order, safe envelope discovery, stricter schemas, and template-budget production-claim regression coverage.
- What went well: Validators pass with 42 skills and 91 trigger eval cases; canonical verification passes.
- What went wrong: PyYAML was unavailable locally, so YAML template parsing used Ruby/Psych.
- Follow-ups / tech debt tickets: Optional future orchestrator skill `embedded-system-familiarization` remains out of scope.
