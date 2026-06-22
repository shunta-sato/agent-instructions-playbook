# Skill Bootstrap And Description Hardening — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Improve the repository-local Agent Skills so agents reliably inspect the Agent Index, load explicit skills before acting, enter code/test changes through `dev-workflow`, and finish through `quality-gate`.
- Start the broader Superpowers-inspired improvement as a reviewable PR 1: bootstrap rules plus trigger-only description hardening.

## Scope

### In scope
- Add a short `AGENTS.md` bootstrap rule block for Agent Index inspection, explicit skill loading, code/test workflow routing, and subagent task briefs.
- Add `.agents/bootstrap/using-playbook.md` as a referenced helper document, not as a special auto-loaded directory.
- Add non-blocking description-style lint that warns when skill frontmatter descriptions look procedural instead of trigger-only.
- Surface description-style flags in the deterministic skill inventory report.
- Produce workflow-contract evidence because this PR changes Agent-facing workflow instructions and validation artifacts.

### Out of scope / non-goals
- Do not copy Superpowers skills wholesale.
- Do not add model-routing catalogs, lockfiles, generated custom agents, run-ledger scripts, behavior evals, or review/branch-completion skills in this PR.
- Do not introduce OpenTelemetry or require token counts.
- Do not change generated Agent Index content by hand.

## Constraints / Quality targets

- Latency / throughput / resource budgets: not applicable; scripts remain simple repository validation commands.
- Safety/security/privacy: no credentials, external endpoints, model names, or organization-specific routing policy are introduced.
- Compatibility / rollout constraints: `validate_skills.py` description hardening is warning-only for this PR so existing legitimate trigger wording does not break CI unexpectedly.
- Operability: warnings include file paths and reason labels so maintainers can tighten descriptions incrementally.

## Context & Orientation

- Key paths / entry points:
  - `AGENTS.md`
  - `.agents/skills/*/SKILL.md`
  - `scripts/validate_skills.py`
  - `scripts/report_skill_inventory.py`
  - `COMMANDS.md`
- Existing behavior:
  - `AGENTS.md` already requires `dev-workflow` and `quality-gate` for code/test changes.
  - `validate_skills.py` validates metadata and layout but only enforces length for descriptions.
  - `report_skill_inventory.py` reports broad trigger flags and eval coverage.
- Conventions to follow:
  - Keep `AGENTS.md` short and detailed rationale in on-demand docs.
  - Do not hand-edit the generated Agent Index.
  - Use canonical verification from `COMMANDS.md`.
- Unknowns:
  - Exact future model catalog format is deferred to later PRs.

## Design

### Boundary sketch

- Components involved:
  - `AGENTS.md`: minimal always-present bootstrap instructions.
  - `.agents/bootstrap/using-playbook.md`: explanatory helper for humans and agents that need rationale/examples.
  - `validate_skills.py`: local metadata/layout validator; adds warning-only description style checks.
  - `report_skill_inventory.py`: inventory artifact; adds description style flags next to broad trigger flags.
- Boundary crossings: repository instruction surface to Codex/Copilot; validation command output to downstream reports and CI logs.
- DTOs / interfaces: no persistent schema change beyond adding `description_trigger_only_flags` to inventory output.
- Error handling strategy: style issues are warnings in PR 1; metadata/layout errors remain blocking.

### Observability

- Logs: validation scripts print warning sections with path-qualified messages.
- Metrics: inventory totals continue to include warning count; description flags increase warning count when present.
- Traces: not applicable.

### Testing strategy

- Unit tests: none configured locally.
- Integration tests: `make verify` canonical chain.
- Manual verification: inspect warnings and final diff scope.

## Milestones (high-level plan)

1. Add the ExecPlan and record dev-workflow routing, complexity budget, and workflow-contract review requirement.
2. Update `AGENTS.md` and add `.agents/bootstrap/using-playbook.md` with bootstrap rules and non-auto-load boundary.
3. Add description-style warning logic to `validate_skills.py` and inventory reporting.
4. Run canonical verification, generate workflow-contract review evidence, and update the plan with outcomes.
5. Commit, push, and open a GitHub PR against `main`.

## Progress (WBS)

- [x] (P0) Create branch and ExecPlan — deliverable: `plans/20260622-skill-bootstrap-description-hardening.md` — verify: plan exists and records scope.
- [x] (P1) Bootstrap docs — deliverable: `AGENTS.md`, `.agents/bootstrap/using-playbook.md` — verify: generated index remains untouched.
- [x] (P2) Description lint — deliverable: script warnings and inventory flags — verify: `python3 scripts/validate_skills.py`, `python3 scripts/report_skill_inventory.py --format text`.
- [x] (P3) Workflow contract review — deliverable: `reports/workflow-contract-review/20260622-skill-bootstrap-description-hardening.md` — verify: report decision is `submit`.
- [ ] (P4) Final verification and publish — deliverable: green canonical checks, commit, pushed branch, PR — verify: PR URL.

## Dev-Workflow Route

- Risk level: high.
- Why this level: the change modifies Agent-facing bootstrap instructions and validation artifacts consumed by downstream reports.
- Escalation trigger: if model routing, run-ledger scripts, generated agents, or behavior eval schemas are added, split into a later PR or expand the plan.
- Default lane: required.
- Required branches:
  - `implementation-economy`: triggered by high-risk implementation and script helper changes.
  - `function-boundary-governor`: triggered by script function/helper edits.
  - `agent-workflow-contract-review`: triggered by Agent-facing workflow and validation artifact changes.
  - `quality-gate`: mandatory before submission.
- Non-triggered branches:
  - `design-balance`: no module/class responsibility layout or new layer/interface in this PR.
  - `requirements-engineering`: provided plan is specific enough for PR 1 acceptance.
  - `observability`: no runtime behavior or external call path.
  - `performance-review`: no hot request/render/job path.
  - embedded/concurrency/UI/legacy/staged-lowering branches: not applicable.
- Required verification depth before gate: full canonical chain from `COMMANDS.md`.

## Implementation Economy

- Changed files target: 5 tracked files plus one required report.
- New classes/modules target: 0.
- New helpers/wrappers/adapters target: 2-4 local helper functions/constants across existing scripts.
- New indirection layers target: 0.
- Rough production/test line budget: under 220 net non-test lines for PR 1.

### Post-Implementation Economy Audit

| New abstraction | Justification | Decision | Evidence |
| --- | --- | --- | --- |
| `DESCRIPTION_STYLE_PATTERNS` in validation scripts | Keeps trigger-only style checks declarative and easy to extend without embedding multiple ad hoc regex checks in control flow. | keep | Used by `description_style_warnings` and `description_trigger_only_flags`; `make verify` passed. |
| `description_style_warnings` | Separates non-blocking style warnings from blocking metadata/layout errors in `validate_skills.py`. | keep | `python3 scripts/validate_skills.py` reports zero description warnings after description cleanup. |
| `description_trigger_only_flags` | Mirrors existing inventory flag style next to `broad_trigger_flags` without creating a shared module for two scripts. | keep | Inventory output includes `description_flags`; `make verify` passed. |

Budget result: within file and abstraction budget; no new classes, modules, wrappers, adapters, or indirection layers were added.

## Function Boundary Notes

- Planned function edits:
  - `validate_skills.py`: keep existing validation boundary; add a local description-style warning helper and wire warnings into `main`.
  - `report_skill_inventory.py`: keep existing inventory/report boundary; add description flags beside existing broad trigger flags.
- Semantic neighbors:
  - `broad_trigger_flags` in `report_skill_inventory.py` is a parallel concept, not a shared abstraction target in PR 1.
  - Existing `validate_skill` error checks are a parallel blocking-validation concept; style warnings stay separate.
- Decision: keep parallel local helpers in each script for consistency with existing duplicated parsing helpers and to avoid a new shared module.
- Ledger update: not required; no abstraction replacement, intentional staged adapter, or preserved old/new abstraction.
- Verification: `make verify` passed with description-style flags clear and only pre-existing broad-trigger warnings remaining.

## Surprises & Discoveries

- 2026-06-22: The worktree already contained two unrelated untracked files under `plans/` and `reports/bug-reports/`; they are excluded from this PR.
- 2026-06-22: Description-style warnings went to zero after narrowing 15 frontmatter descriptions; only pre-existing broad-trigger inventory warnings remain.

## Decision log

- 2026-06-22: Limit this PR to bootstrap and description hardening because the provided plan already splits model routing, run ledger, quality-gate ledger integration, behavior evals, and branch completion into later PRs.
  - Options considered: implement the first minimal set from section 8 in one broad PR; implement PR 1 only.
  - Chosen: implement PR 1 only.
  - Consequences: review scope stays narrow; model routing and run ledger remain follow-ups.
- 2026-06-22: Make description style checks warning-only because existing skills include mandatory trigger wording and a blocking switch would create broad churn before maintainers agree on thresholds.
  - Options considered: fail `validate_skills.py` on style flags; warn only in PR 1.
  - Chosen: warn only.
  - Consequences: CI remains stable while inventory makes follow-up tightening visible.

## Handoff (update at every stop)

- Current branch / commit: `codex/skill-bootstrap-description-hardening`, uncommitted changes in progress.
- What is done: goal created; bootstrap docs added; description lint added; skill descriptions narrowed; workflow-contract report added; `make verify` passed.
- What is not done: commit, push, PR.
- How to run: `make verify`.
- How to test: `python3 scripts/validate_skills.py`; `python3 scripts/report_skill_inventory.py --check --format text`; `make verify`.
- Known risks / open questions: warning thresholds may need tightening in later PRs; model routing and run ledger remain explicitly deferred.
- Next 1-3 steps: run quality gate review, stage intended files, commit and open PR.
- Pointers: `AGENTS.md`, `scripts/validate_skills.py`, `scripts/report_skill_inventory.py`, `COMMANDS.md`.

## Validation & Acceptance

- AC1: Code/test changes still route through `dev-workflow` and completion through `quality-gate`.
  - Verification: inspect `AGENTS.md`; `make verify`.
- AC2: Explicit skill requests require loading the named skill before acting.
  - Verification: inspect `AGENTS.md` bootstrap section.
- AC3: `.agents/bootstrap` is documented as an ordinary referenced helper directory, not a special auto-load mechanism.
  - Verification: inspect `.agents/bootstrap/using-playbook.md`.
- AC4: Skill descriptions that look procedural are flagged without blocking this PR.
  - Verification: `python3 scripts/validate_skills.py`; `python3 scripts/report_skill_inventory.py --format text`.
- AC5: Agent-facing workflow contract review is present and submit-ready.
  - Verification: `reports/workflow-contract-review/20260622-skill-bootstrap-description-hardening.md`.

## Outcomes & Retrospective (fill when done)

- What shipped / merged:
- What went well: `make verify` passed; description-style lint now reports no description flags.
- What went wrong: none so far.
- Follow-ups / tech debt tickets: later PRs should add model routing foundation, subagent execution references/templates, run ledger, quality-gate delegated-run evidence, behavior/model-routing evals, and review/branch-completion skills.
