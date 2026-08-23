# Harness-aware model routing — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**,
> **Surprises & Discoveries**, and **Handoff** current.

## Purpose / Big Picture

Prevent a concrete model selected for one execution harness from being treated
as available in another. Task classes and capability profiles remain reusable,
but concrete model selection must be bound to the active harness and fail closed
when that identity is missing or mismatched.

The motivating failure is a Codex/ChatGPT session reading a repository-global
route that selected a Claude Sonnet model and discussing it as an available
worker, even though the current harness could not invoke it.

## Scope

### In scope

- Add a required top-level `harness` identity to the concrete Model Catalog and
  generated Route Lockfile.
- Require the active harness when resolving a concrete model from a catalog.
- Return `selected: false` before candidate evaluation when the active harness
  is absent or differs from the catalog harness.
- Prohibit cross-harness profile fallback.
- Record harness and catalog harness in every resolved route.
- Add validator, unit-test, and model-routing eval coverage for mismatch cases.
- Clarify Claude Code, Copilot, and shared delegated-execution instructions.
- Update the Claude reviewer contract and generated lockfile.

### Out of scope / non-goals

- Claiming which concrete model Codex or Copilot currently supports.
- Adding Codex or Copilot catalogs without evidence-backed availability and
  smoke runs.
- Changing Task Class, Capability Profile, Risk Gate, or Prompt Detail meaning.
- Creating a multi-provider model broker or invoking another harness remotely.
- Replacing the existing static Claude Code custom agents.
- Changing run evidence, quality gates, or research evidence semantics.

## Constraints / Quality targets

- **Fail closed:** catalog selection without a known matching harness returns no
  concrete model.
- **No cross-harness fallback:** profile fallback may occur only after harness
  equality is established.
- **Compatibility:** route resolution without a catalog still returns
  model-independent metadata and `catalog_not_provided`.
- **Evidence:** existing Claude model selections remain unchanged when
  `harness=claude-code` matches the catalog.
- **No guessed availability:** no new Codex/Copilot model IDs are introduced.
- **Structure:** touched Python files must stay within repository structure
  budgets; split if a validator exceeds the limit.
- **Verification:** `make verify` and the PR workflow must pass.

## Context & Orientation

- `.agents/model-routing/task-classes.yml` and
  `.agents/model-routing/capability-profiles.yml` are model-independent.
- `.agents/model-routing/model-catalog.json` contains concrete Claude model IDs.
- `.agents/model-routing/route-lockfile.json` materializes the catalog through
  the resolver.
- `scripts/resolve_model_route.py` owns candidate selection and profile fallback.
- `scripts/generate_route_lockfile.py` materializes all Task Classes.
- `scripts/validate_model_routing.py` checks configuration and resolver smoke
  behavior.
- `scripts/validate_model_routing_evals.py` checks routing eval fixtures.
- `.agents/skills/execution-plans/references/model-routing.md` is the shared
  delegated-execution guidance used across clients.
- `CLAUDE.md` and `.github/copilot-instructions.md` are client-specific entries.

## Design

### Authority split

```text
Task Class / Capability Profile / Risk Gate / Prompt Detail
                    │
                    └── shared across harnesses

Active harness + matching harness-scoped catalog
                    │
                    └── concrete model selection
```

A concrete model route is valid only when:

```text
active_harness is known
AND catalog.harness is known
AND active_harness == catalog.harness
```

Otherwise:

```json
{
  "selected": false,
  "selected_model": null,
  "fallback_reasons": ["catalog_harness_mismatch:claude-code:codex"]
}
```

### Resolver sequence

1. Resolve Task Class, Capability Profile, Risk Gate, and Prompt Detail.
2. If no catalog exists, retain the existing `catalog_not_provided` result.
3. If a catalog exists but active harness is absent, return
   `active_harness_missing`.
4. If the catalog lacks its own identity, return `catalog_harness_missing`.
5. If identities differ, return `catalog_harness_mismatch:<catalog>:<active>`.
6. Only after equality may candidate filtering and same-harness profile fallback
   run.

### Artifact contract

- Model Catalog: top-level `harness` identifies where listed models were smoke
  evaluated and can be invoked.
- Route Lockfile: top-level `harness` plus per-route `harness` and
  `catalog_harness` preserve the binding.
- Current concrete artifacts declare `claude-code`.
- A future Codex or Copilot catalog must be created separately with current
  availability evidence; it cannot reuse the Claude catalog by renaming an
  argument.

### Error handling

Harness mismatch is an ordinary unresolved route, not a parser failure. This
lets callers inspect model-independent route metadata while preventing an
unavailable concrete delegation. Invalid files and unknown Task Classes remain
hard errors.

### Observability

Resolver JSON/text output reports:

- active harness
- catalog harness
- selected flag/model
- explicit fallback reasons

No background service or external telemetry is added.

### Testing strategy

- Existing status/smoke candidate filtering under a matching fixture harness.
- Missing catalog remains unresolved.
- Missing active harness remains unresolved.
- Claude Code catalog with active `codex` remains unresolved before candidate
  selection.
- Same-harness profile fallback continues to work.
- Generated repository lockfile equals regeneration and records
  `harness=claude-code` at every route.
- Shared and client-specific docs state the same authority boundary.

## Validation & Acceptance

- **AC1:** a matching harness preserves existing Claude selections.
  - Verify: generated lockfile equality and unit tests.
- **AC2:** a Claude Code catalog cannot select a model for active Codex.
  - Verify: model-routing eval and unit test.
- **AC3:** missing active or catalog harness cannot select a model.
  - Verify: resolver smoke validation.
- **AC4:** mismatch stops before candidate/profile fallback.
  - Verify: only the harness mismatch reason is required; no candidate is
    described as selected or available.
- **AC5:** route artifacts expose their harness identity.
  - Verify: lockfile generator and tests.
- **AC6:** shared instructions forbid cross-harness fallback; client entries
  describe the current Claude artifacts accurately.
  - Verify: instruction graph and workflow-contract review.
- **AC7:** all canonical checks pass.
  - Verify: `make verify` and GitHub Actions.

## Progress (WBS)

- [x] (P0) Record the authority defect and implementation boundary.
- [x] (P1) Add harness fields and fail-closed resolver policy.
- [x] (P2) Update resolver, generator, and validators.
- [x] (P3) Add eval and unit-test coverage.
- [x] (P4) Update shared, Claude Code, Copilot, and reviewer instructions.
- [x] (P5) Regenerate the harness-bound Route Lockfile.
- [x] (P6) Add this ExecPlan and Workflow Contract Review.
- [ ] (P7) Run canonical PR validation and address findings.
- [ ] (P8) Record final run identity and mark the PR ready.

## Surprises & Discoveries

- 2026-08-23: The concrete catalog and lockfile originated in the Claude Code
  wiring work, but their generic repository paths made them appear
  harness-independent.
- 2026-08-23: Static Claude custom agents already declare Claude aliases in
  `.claude/agents/`; the defect is not their local invocation but the shared
  authority implied by the catalog/lockfile and delegated-execution reference.
- 2026-08-23: No evidence-backed Codex or Copilot catalog exists in the
  repository. Leaving those concrete routes unresolved is the honest behavior.

## Decision log

- 2026-08-23: Keep Task Classes and Capability Profiles shared.
  - Rationale: their semantics describe work and required capability, not a
    provider or client.
- 2026-08-23: Bind the concrete Catalog and Lockfile with a top-level harness.
  - Alternatives: infer provider from model ID; maintain implicit client-local
    convention; add explicit harness identity.
  - Chosen: explicit identity because inference is ambiguous and not
    mechanically enforceable.
- 2026-08-23: Treat mismatch as unresolved rather than falling back to another
  profile or model.
  - Rationale: a weaker profile in an unavailable harness remains unavailable.
- 2026-08-23: Do not add speculative Codex/Copilot catalogs.
  - Rationale: availability and smoke evidence must precede selection.
- 2026-08-23: Retain existing generic artifact paths in this PR, but make their
  harness binding explicit in schema, output, validation, and instructions.
  - Rationale: fixes authority without an unnecessary path migration; future
    multi-harness catalogs may be split after concrete second-harness evidence
    exists.

## Handoff

- Branch: `fix/harness-aware-model-routing`
- Base: `main` at `7c82a14add3534095f64f7ea03abd1015a27a2a1`.
- What is complete: implementation, generated lockfile, docs, evals, tests, plan.
- What remains: workflow-contract report, PR creation, CI, final plan update.
- Canonical command: `make verify`.
- Read first:
  - `scripts/resolve_model_route.py`
  - `.agents/model-routing/model-catalog.json`
  - `.agents/model-routing/route-lockfile.json`
  - `.agents/skills/execution-plans/references/model-routing.md`
  - `evals/model-routing/core.json`
- Known risk: touched validators may cross the 400-line structure budget and
  require a focused split after CI measurement.

## Outcomes & Retrospective

- Shipped/merged: pending PR.
- Failed/rejected attempts: none recorded yet.
- Failure retrospective:
  - not triggered at this checkpoint; no repeated implementation failure,
    rollback, or rejected completion claim has occurred.
- Remaining follow-ups:
  - create separate Codex/Copilot catalogs only after current harness capability
    discovery and smoke evidence;
  - consider path-level catalog separation when a second concrete harness
    catalog exists.
