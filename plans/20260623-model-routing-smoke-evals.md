# Model Routing Smoke Evals — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Finish the PR 6 model-routing half by adding deterministic smoke eval seeds for resolver behavior.
- Keep the scope to schema and resolver checks only; no model calls, generated catalogs, route lockfiles, or generated agents.

## Scope

### In scope

- Add `evals/model-routing/core.json`.
- Add `scripts/validate_model_routing_evals.py`.
- Validate task class names, expected capability profiles, catalog fixture shape, candidate profile/status values, expected resolver result, and fallback reasons.
- Wire validation into `make lint`, `make test-integration`, `make verify`, and GitHub Actions.
- Add workflow-contract evidence for the model-routing eval validation chain.

### Out of scope / non-goals

- Do not add generated model catalogs or lockfiles.
- Do not call external model APIs or grade model output.
- Do not render Copilot custom agents.
- Do not add review-receiving or branch-completion skills.

## Constraints / Quality targets

- Latency / throughput / resource budgets: stdlib-only validation over local JSON files.
- Safety/security/privacy: no network and no credentials.
- Compatibility / rollout constraints: follow existing validator CLI conventions and keep model IDs only inside eval catalog fixtures.
- Operability: error output must include file/case/field context.

## Context & Orientation

- Key paths / entry points:
  - `.agents/model-routing/task-classes.yml`
  - `.agents/model-routing/capability-profiles.yml`
  - `.agents/model-routing/resolver-policy.yml`
  - `scripts/resolve_model_route.py`
  - `scripts/validate_model_routing.py`
  - `scripts/validate_skill_behavior_evals.py`
- Existing behavior:
  - `validate_model_routing.py` already validates core routing artifacts and has an internal resolver smoke.
  - PR #65 added behavior eval validation but not model-routing eval seeds.
- Conventions to follow:
  - Use `--repo-root` and `--eval-dir`.
  - Aggregate all errors and exit non-zero.
- Unknowns:
  - Future generated catalog format may add fields; current eval catalog fixtures use the resolver's existing minimum fields.

## Design

### Boundary sketch

- Components involved:
  - `evals/model-routing/core.json`: deterministic resolver smoke cases.
  - `scripts/validate_model_routing_evals.py`: schema and resolver expectation validator.
  - `Makefile` and `.github/workflows/agent-index.yml`: validation chain.
- Boundary crossings:
  - Local filesystem reads of routing config and eval JSON.
- DTOs / interfaces:
  - Eval file: `{version: 1, cases: [...]}`.
  - Case: `id`, `task_class`, `expected_capability_profile`, `catalog`, `expected`, `checks`.
  - Expected: selected flag, optional selected model, optional selection profile, fallback reasons that must appear.
- Error handling strategy:
  - Accumulate schema and resolver expectation errors with exact contexts.

### Observability

- Logs: success count and path-qualified error bullets.
- Metrics: not applicable.
- Traces: not applicable.

### Testing strategy

- Unit tests: temp fixture checks for valid and invalid eval cases.
- Integration tests: `make lint`, `make test-integration`, `make verify`.
- Manual verification: inspect Makefile and CI workflow wiring.

## Milestones (high-level plan)

1. Confirm Red state for the missing validator.
2. Add model-routing eval seed cases for scope control and rumored-model exclusion.
3. Add validator script and wire it into local/CI verification.
4. Add workflow-contract report and run canonical checks.
5. Publish PR and request review.

## Progress (WBS)

- [x] (P0) Confirm Red state — deliverable: missing validator command fails — verify: `python3 scripts/validate_model_routing_evals.py` returned file-not-found.
- [x] (P1) Add eval seeds — deliverable: `evals/model-routing/core.json` — verify: validator passes.
- [x] (P2) Add validator — deliverable: `scripts/validate_model_routing_evals.py` — verify: targeted valid/invalid fixture checks.
- [x] (P3) Wire verification — deliverable: `Makefile` and `.github/workflows/agent-index.yml` updates — verify: `make lint`, `make test-integration`, `make verify`.
- [x] (P4) Add workflow-contract evidence — deliverable: `reports/workflow-contract-review/20260623-model-routing-smoke-evals.md` — verify: decision is `submit`.
- [ ] (P5) Publish PR — deliverable: draft PR with explicit URL — verify: GitHub PR created.

## Surprises & Discoveries

- 2026-06-23: PR #65 intentionally covered skill-behavior validation only, leaving the model-routing smoke eval half of PR 6 for this small follow-up.

## Decision log

- 2026-06-23: Run resolver checks inside the eval validator, not just schema checks.
  - Options considered: schema-only; schema plus resolver output assertions.
  - Chosen: schema plus resolver output assertions.
  - Consequences: smoke evals prove rumored/unavailable candidates remain non-selectable without external model calls.
- 2026-06-23: Keep eval catalog fixtures local to `evals/model-routing`.
  - Options considered: add generated catalog files; inline catalog fixtures.
  - Chosen: inline fixtures.
  - Consequences: no generated catalog/lockfile scope creep in this PR.

## Function Boundary Evidence

| Function | Concept / invariant | Callers | Semantic neighbors | Decision |
| --- | --- | --- | --- | --- |
| `validate_catalog` | Catalog fixture schema and known status/profile checks | `validate_case` | `resolve_model_route.normalize_catalog` parallel concept | keep; validator needs richer error contexts |
| `validate_expected_result` | Compare resolver output to eval expectations | `validate_case` | `validate_model_routing.validate_resolver_smoke` parallel concept | keep; eval cases are data-driven |
| `validate_case` | Per-case schema and resolver execution | `validate_file` | behavior eval `validate_case` parallel concept | keep; model-routing fields differ |
| `validate_file` | Per-file eval payload validation | `validate_model_routing_evals` | other validators' `validate_file` parallel concept | keep; local schema boundary |
| `validate_model_routing_evals` | Directory aggregation and routing load | `main` | behavior eval validator aggregation parallel concept | keep; CLI-testable boundary |

Ledger update: not required because this PR does not replace an existing abstraction, preserve a staged adapter, or intentionally duplicate a production abstraction.

## Complexity Budget

- Changed files target: 6 files.
- New classes/modules target: 1 new script module.
- New helpers/wrappers/adapters target: 8 small validator helpers.
- New indirection layers target: 0.
- Rough production/check-wiring line budget: <= 320 net lines, excluding eval seed data and plan/report evidence.
- Eval seed data budget: one focused model-routing eval JSON file.
- Evidence document budget: one ExecPlan and one workflow-contract report.

## Post-Implementation Economy Audit

| New abstraction | Justification | Decision | Evidence |
| --- | --- | --- | --- |
| `scripts/validate_model_routing_evals.py` | Makes model-routing smoke evals CI-visible without model calls or generated catalogs. | keep | targeted fixture checks and `make verify` pass |
| Script-local validator helpers | Avoid ad hoc type checks and preserve precise error locations. | keep | invalid fixtures report exact fields |

## Handoff (update at every stop)

- Current branch / commit: `codex/model-routing-smoke-evals` / pending.
- What is done: eval seeds, validator, Makefile/CI wiring, plan, workflow-contract evidence, targeted fixture checks, and canonical verification.
- What is not done: commit, PR creation, review request, merge, review/branch-completion skills.
- How to run: `python3 scripts/validate_model_routing_evals.py`.
- How to test: targeted temp fixture checks; `make lint`; `make test-integration`; `make verify`.
- Known risks / open questions: future generated catalogs may require extra fields beyond current fixture schema.
- Next 1-3 steps: commit, push, open PR, request review.
- Pointers: `scripts/validate_model_routing_evals.py`, `evals/model-routing/core.json`, `scripts/resolve_model_route.py`.

## Validation & Acceptance

- AC1: Model-routing smoke eval seeds are schema-checked and resolver-checked.
  - Verification: `python3 scripts/validate_model_routing_evals.py`.
- AC2: `unit_test_single_case` has a scope-control eval.
  - Verification: inspect `evals/model-routing/core.json` and validator output.
- AC3: Rumored models can appear in eval fixtures but are not selectable.
  - Verification: `rumored-model-not-selectable` case passes.
- AC4: Canonical verification includes model-routing eval validation locally and in CI.
  - Verification: `make lint`, `make test-integration`, `make verify`, and workflow inspection.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: pending PR; model-routing eval seeds and validator are implemented locally.
- What went well: the resolver API could be reused directly, so evals assert real routing behavior without model calls.
- What went wrong: none so far.
- Follow-ups / tech debt tickets: generated catalogs, route lockfiles, generated agents, and review/branch-completion skills remain out of scope.
