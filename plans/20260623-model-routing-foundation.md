# Model Routing Foundation — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Add the PR 2 foundation for dynamic model routing without hard-coding concrete model IDs in skill bodies or routing tables.
- Establish task classes, capability profiles, risk gates, prompt detail levels, and resolver policy so later PRs can generate catalogs, lockfiles, custom agents, and run ledgers from a stable contract.

## Scope

### In scope
- Add `.agents/model-routing/task-classes.yml` with task classes and success criteria.
- Add `.agents/model-routing/capability-profiles.yml` with model-agnostic capability profiles.
- Add `.agents/model-routing/resolver-policy.yml` with selectable/excluded status policy and fallback rules.
- Add `.agents/model-routing/risk-gates.yml` and `.agents/model-routing/prompt-detail-levels.md`.
- Add `scripts/resolve_model_route.py` to resolve task class to profile and, when a catalog is supplied, select a model candidate.
- Add `scripts/validate_model_routing.py` to validate config consistency and resolver invariants.
- Add canonical Makefile validation coverage.
- Add workflow-contract evidence because validation and agent-routing artifacts are changed.

### Out of scope / non-goals
- Do not add generated model catalogs, route lockfiles, generated Copilot custom agents, or concrete production model IDs.
- Do not add run ledger scripts or token collection.
- Do not use OpenTelemetry.
- Do not change existing skill behavior beyond adding validation coverage.

## Constraints / Quality targets

- No external Python dependencies; routing files are JSON-compatible YAML so stdlib `json` can validate them.
- No concrete model IDs in `.agents/model-routing/*.yml`; sample resolver tests may use placeholder IDs only.
- Resolver must record fallback reasons instead of silently selecting an unavailable candidate.
- Existing `make verify` must remain the canonical acceptance command.

## Context & Orientation

- Key paths:
  - `.agents/model-routing/`
  - `scripts/resolve_model_route.py`
  - `scripts/validate_model_routing.py`
  - `Makefile`
  - `reports/workflow-contract-review/`
- Existing behavior:
  - PR #59 added bootstrap guidance saying models should be resolved through task class, capability profile, current catalog, policy, and lockfile once those artifacts exist.
  - No model-routing artifacts exist yet.
  - PyYAML is not installed; repository scripts are stdlib-only.
- Unknowns:
  - Future generated catalog and lockfile schemas may evolve; this PR defines only the minimum fields needed for validation and later extension.

## Design

### Boundary sketch

- Static routing definitions:
  - `task-classes.yml`: task class responsibility, profile, prompt detail, default effort, max scope, success criteria, escalation.
  - `capability-profiles.yml`: model-agnostic capability requirements and fallback profile names.
  - `resolver-policy.yml`: selectable/excluded status values, fallback order, and no-concrete-model-id policy.
  - `risk-gates.yml`: route labels and escalation triggers.
  - `prompt-detail-levels.md`: human-readable prompt detail contract.
- Scripts:
  - `resolve_model_route.py`: reusable CLI and importable functions for task-class resolution and optional catalog candidate selection.
  - `validate_model_routing.py`: repository validation command with config consistency and resolver smoke tests.
- Error handling:
  - Unknown task/profile/status returns nonzero validation error or JSON result with explicit `selected: false` and fallback reasons.
  - Missing catalog is not a task-class resolution failure.
- Observability:
  - CLI JSON output includes task class, profile, prompt detail, risk gate, selected model if available, and fallback reasons.

### Testing strategy

- Unit-like script smoke:
  - `python3 scripts/validate_model_routing.py`
  - `python3 scripts/resolve_model_route.py unit_test_single_case`
  - `python3 scripts/resolve_model_route.py ci_failure_diagnosis --catalog <temp-catalog>`
- Integration:
  - `make verify`

## Milestones (high-level plan)

1. Define model-routing static artifacts with JSON-compatible YAML.
2. Implement resolver and validator scripts with stdlib-only parsing.
3. Wire validation into `Makefile`.
4. Add workflow-contract report and update this plan with route/economy/function-boundary evidence.
5. Run verification, publish PR, request review, and update automation to the new PR.

## Progress (WBS)

- [x] (P0) Sync after PR #60 merge and create branch — deliverable: `codex/model-routing-foundation` — verify: branch exists from `origin/main`.
- [x] (P1) Static routing artifacts — deliverable: `.agents/model-routing/*` — verify: `python3 scripts/validate_model_routing.py` loaded and validated all artifacts.
- [x] (P2) Resolver/validator scripts — deliverable: `scripts/resolve_model_route.py`, `scripts/validate_model_routing.py` — verify: targeted resolver and validator commands passed.
- [x] (P3) Makefile integration — deliverable: `make lint`/`make test-integration` run model routing validation — verify: `make verify` passed.
- [ ] (P4) Workflow evidence and publication — deliverable: report, commit, PR, review request — verify: raw PR URL.

## Dev-Workflow Route

- Risk level: normal.
- Why this level: adds new validation scripts and routing artifacts but no runtime product behavior, no external calls, and no concrete model selection in repo state.
- Escalation trigger: adding generated agents, generated catalogs, lockfiles, or run-ledger execution moves this into a broader multi-PR/high-risk workflow.
- Default lane: required.
- Required branches:
  - `implementation-economy`: normal-risk default lane and new script/module code.
  - `function-boundary-governor`: new resolver/validator functions and call-site boundaries.
  - `agent-workflow-contract-review`: new Agent-facing routing and validation artifacts.
  - `quality-gate`: mandatory final submit gate.
- Non-triggered branches:
  - `design-balance`: no class/module ownership split beyond file-level scripts; responsibilities are simple and recorded here.
  - `architecture-decision-analysis`: no competing cross-boundary technology options; JSON-compatible YAML is chosen due stdlib constraint.
  - `observability`: no runtime service behavior.
  - embedded/concurrency/UI/legacy/staged-lowering branches: not applicable.
- Required verification depth before gate: full canonical chain.

## Implementation Economy

- Changed files target: 10 tracked files or fewer.
- New classes/modules target: 0 classes, 2 scripts, 1 config directory.
- New helpers/wrappers/adapters target: small local helpers only; no shared package unless duplication appears.
- New indirection layers target: 0.
- Rough production/test line budget: initially under 500 net lines; actual staged implementation/config is larger because it includes self-contained schema validation, resolver smoke tests, and five static routing artifacts.
- Complexity decision: accept the larger line count for this PR because it preserves zero external dependencies, zero classes, and one canonical validation path instead of introducing a package/dependency layer.

## Function Boundary Notes

- Implemented functions:
  - config loading from JSON-compatible YAML files.
  - schema validation helpers.
  - `resolve_route()` for task class to route summary.
  - catalog candidate filtering/selection helpers.
- Decision: keep resolver and validator as separate scripts because resolver is a user-facing CLI while validator owns repository consistency checks.
- Ledger update: not expected; no staged adapter or replacement of existing abstraction.
- Post-implementation boundary audit:
  - `select_candidate()` owns one profile attempt; `profile_fallback_chain()` owns fallback traversal.
  - `resolve_route()` is the importable boundary that combines task class lookup, risk gate lookup, and optional external catalog selection.
  - `validate_model_routing()` returns an error list and keeps CLI rendering in `main()`.

## Surprises & Discoveries

- 2026-06-23: PyYAML is not installed, so model-routing `.yml` files will be JSON-compatible YAML and parsed with stdlib `json`.
- 2026-06-23: Resolver policy named profile fallback order; the resolver now executes the fallback chain instead of only documenting it.

## Decision log

- 2026-06-23: Use JSON-compatible YAML in `.yml` files because the repository has no YAML dependency and current Makefile validation relies on stdlib Python.
  - Options considered: add PyYAML dependency; write a custom YAML parser; use JSON-compatible YAML.
  - Chosen: JSON-compatible YAML.
  - Consequences: files are valid YAML and simple to validate, but authors must keep object syntax JSON-compatible until a YAML parser is introduced.
- 2026-06-23: Keep concrete model IDs out of routing files and accept candidates only through an explicit external catalog path.
  - Options considered: seed static model IDs in `resolver-policy.yml`; store current catalog in repo; require `--catalog` for candidate selection.
  - Chosen: require an explicit external catalog for candidate selection.
  - Consequences: route resolution without a catalog is still useful and returns `selected: false`; later PRs can add generated catalogs and lockfiles without rewriting task classes.

## Handoff (update at every stop)

- Current branch / commit: `codex/model-routing-foundation`, uncommitted changes ready for review.
- What is done: PR #60 merged; local `main` synced; branch created; routing artifacts, resolver, validator, Makefile wiring, workflow-contract report, and canonical verification are complete.
- What is not done: commit, push, PR creation, review request.
- How to run: `make verify`.
- How to test: `python3 scripts/validate_model_routing.py`; `python3 scripts/resolve_model_route.py unit_test_single_case`; `make verify`.
- Known risks / open questions: future catalog/lockfile schema may need extension; this PR intentionally avoids concrete model IDs.
- Next 1-3 steps: commit, push, open draft PR, request review.
- Pointers: `.agents/model-routing/`, `scripts/resolve_model_route.py`, `scripts/validate_model_routing.py`, `Makefile`.

## Validation & Acceptance

- AC1: Task class resolves to capability profile and route metadata.
  - Verification: `python3 scripts/resolve_model_route.py unit_test_single_case`.
- AC2: Concrete model IDs are not stored in routing definitions.
  - Verification: `python3 scripts/validate_model_routing.py`.
- AC3: Unavailable, disabled, retired, policy-blocked, and rumored candidates are excluded.
  - Verification: validator built-in resolver smoke.
- AC4: Fallback reasons are explicit when no candidate is selectable.
  - Verification: validator built-in resolver smoke.
- AC5: Canonical verification includes model routing validation.
  - Verification: `make verify`.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: pending PR.
- What went well: stdlib-only routing validation fits the existing Makefile contract and targeted resolver smoke covers fallback behavior.
- What went wrong: none so far.
- Follow-ups / tech debt tickets: generated model catalog, route lockfile, generated custom agents, behavior evals, and run ledger remain later PRs.
