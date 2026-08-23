# Harness-aware model routing — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**,
> **Surprises & Discoveries**, and **Handoff** current.

## Purpose / Big Picture

Prevent a concrete model selected for one execution harness from being treated
as available in another. Task Classes and Capability Profiles remain reusable,
but concrete model selection is bound to the active harness and fails closed
when that identity is missing or mismatched.

The motivating failure was a Codex/ChatGPT session reading a repository-global
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
- **Evidence:** existing Claude selections remain unchanged when
  `harness=claude-code` matches the catalog.
- **No guessed availability:** no new Codex/Copilot model IDs are introduced.
- **Structure:** every touched Python source remains within the repository's
  400-line structure budget.
- **Verification:** `make verify` and the PR workflow must pass.

## Context & Orientation

- `.agents/model-routing/task-classes.yml` and
  `.agents/model-routing/capability-profiles.yml` are model-independent.
- `.agents/model-routing/model-catalog.json` contains concrete Claude model IDs.
- `.agents/model-routing/route-lockfile.json` materializes the catalog through
  the resolver.
- `scripts/resolve_model_route.py` owns candidate selection and profile fallback.
- `scripts/generate_route_lockfile.py` materializes all Task Classes.
- `scripts/validate_model_routing.py` owns generic routing schema validation.
- `scripts/model_routing_harness_validation.py` owns harness policy, catalog
  identity, and fail-closed resolver smoke tests.
- `scripts/validate_model_routing_evals.py` checks routing eval fixtures.
- `.agents/skills/execution-plans/references/model-routing.md` is shared
  delegated-execution guidance.
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
2. If no catalog exists, return `catalog_not_provided`.
3. If a catalog exists but active harness is absent, return
   `active_harness_missing`.
4. If the catalog lacks its identity, return `catalog_harness_missing`.
5. If identities differ, return `catalog_harness_mismatch:<catalog>:<active>`.
6. Only after equality may candidate filtering and same-harness profile fallback
   run.

### Artifact contract

- Model Catalog: top-level `harness` identifies where listed models were smoke
  evaluated and can be invoked.
- Route Lockfile: top-level `harness` plus per-route `harness` and
  `catalog_harness` preserve the binding.
- Current concrete artifacts declare `claude-code`.
- A future Codex or Copilot catalog requires separate availability evidence and
  smoke evaluation; it cannot reuse the Claude catalog by changing an argument.

### Error handling

Harness mismatch is an ordinary unresolved route, not a parser failure. Callers
can inspect model-independent metadata while concrete delegation remains
blocked. Invalid files and unknown Task Classes remain hard errors.

### Observability

Resolver JSON/text output reports active harness, catalog harness, selected
flag/model, and explicit fallback reasons. No background service or external
telemetry is added.

### Testing strategy

- Existing status/smoke filtering under a matching fixture harness.
- Missing catalog remains unresolved.
- Missing active harness remains unresolved.
- Claude Code catalog with active `codex` remains unresolved before candidate
  selection.
- Same-harness profile fallback continues to work.
- Generated lockfile equals regeneration and records `harness=claude-code` at
  every route.
- Shared and client-specific docs state the same authority boundary.

## Validation & Acceptance

- **AC1:** a matching harness preserves existing Claude selections.
  - Evidence: generated lockfile equality and unit tests.
- **AC2:** a Claude Code catalog cannot select a model for active Codex.
  - Evidence: model-routing eval and unit test.
- **AC3:** missing active or catalog harness cannot select a model.
  - Evidence: resolver smoke validation.
- **AC4:** mismatch stops before candidate/profile fallback.
  - Evidence: `selected: false`, no selected model, explicit mismatch reason.
- **AC5:** route artifacts expose their harness identity.
  - Evidence: lockfile generator and tests.
- **AC6:** shared instructions forbid cross-harness fallback; client entries
  describe the Claude artifacts accurately.
  - Evidence: instruction graph and Workflow Contract Review.
- **AC7:** all canonical checks pass.
  - Evidence: GitHub Actions run `32619716410` for head
    `1539dba948a25572195ccb4ae0ea74841eb94f0f`, conclusion `success`.

## Progress (WBS)

- [x] (P0) Record the authority defect and implementation boundary.
- [x] (P1) Add harness fields and fail-closed resolver policy.
- [x] (P2) Update resolver, generator, and validators.
- [x] (P3) Add eval and unit-test coverage.
- [x] (P4) Update shared, Claude Code, Copilot, and reviewer instructions.
- [x] (P5) Regenerate the harness-bound Route Lockfile.
- [x] (P6) Add this ExecPlan and Workflow Contract Review.
- [x] (P7) Run canonical PR validation and address findings.
- [x] (P8) Record final run identity and prepare the PR for review.

## Surprises & Discoveries

- 2026-08-23: The concrete catalog and lockfile originated in Claude Code wiring,
  but their generic repository paths made them appear harness-independent.
- 2026-08-23: Static Claude custom agents already declare Claude aliases in
  `.claude/agents/`; the defect was the shared authority implied by the generic
  Catalog/Lockfile and delegated-execution reference.
- 2026-08-23: No evidence-backed Codex or Copilot catalog exists. Leaving those
  concrete routes unresolved is the honest behavior.
- 2026-08-23: Initial CI run `32619594154` passed every contract and routing check
  but found `scripts/validate_model_routing.py` at 433 lines, above the 400-line
  structure budget.
- 2026-08-23: Harness-specific policy/catalog/smoke validation was extracted to
  `scripts/model_routing_harness_validation.py`; run `32619716410` then passed
  the complete validation chain.

## Decision log

- 2026-08-23: Keep Task Classes and Capability Profiles shared.
  - Rationale: they describe work and required capability, not a provider.
- 2026-08-23: Bind the concrete Catalog and Lockfile with a top-level harness.
  - Alternatives: infer provider from model ID; rely on client convention; add
    explicit harness identity.
  - Chosen: explicit identity because inference is ambiguous and unenforceable.
- 2026-08-23: Treat mismatch as unresolved rather than falling back.
  - Rationale: a weaker profile in an unavailable harness remains unavailable.
- 2026-08-23: Do not add speculative Codex/Copilot catalogs.
  - Rationale: availability and smoke evidence must precede selection.
- 2026-08-23: Retain existing artifact paths but make their harness binding
  explicit in schema, output, validation, and instructions.
  - Rationale: fixes authority without premature multi-catalog path migration.
- 2026-08-23: Split generic and harness-specific validation modules.
  - Rationale: preserve the source-file structure budget and align module
    responsibility with the shared-versus-harness-specific authority boundary.

## Handoff

- Branch: `fix/harness-aware-model-routing`
- Pull request: `#117` (`Make concrete model routing harness-aware`).
- Verified head: `1539dba948a25572195ccb4ae0ea74841eb94f0f`.
- Validation: GitHub Actions run `32619716410`, success.
- What is complete: implementation, generated lockfile, docs, evals, tests,
  structure split, plan, Workflow Contract Review, and canonical validation.
- What remains: normal PR review and merge decision.
- Canonical command: `make verify`.
- Read first:
  - `scripts/resolve_model_route.py`
  - `scripts/model_routing_harness_validation.py`
  - `.agents/model-routing/model-catalog.json`
  - `.agents/model-routing/route-lockfile.json`
  - `.agents/skills/execution-plans/references/model-routing.md`

## Outcomes & Retrospective

- Delivered in PR #117:
  - explicit active/catalog harness identity;
  - fail-closed mismatch and missing-identity behavior;
  - same-harness-only profile fallback;
  - harness-bound generated routes;
  - client and shared instruction boundaries;
  - eval and unit regression coverage.
- Failed/rejected attempts:
  - Initial validator composition exceeded the structure budget; responsibility
    was split rather than waived.
- Failure retrospective:
  - not triggered: one deterministic integration finding was corrected directly;
    there was no rollback, repeated materially different failed attempt, or
    rejected completion claim.
- Remaining follow-ups:
  - create Codex/Copilot catalogs only after current capability discovery and
    smoke evidence;
  - consider path-level catalog separation when a second concrete harness
    catalog exists.
