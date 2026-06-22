# Skill Behavior Eval Validator — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Add a repository-local validator for `evals/skill-behavior/*.json` so behavior seed files become part of the canonical verification chain.
- This is the PR 6 follow-up to the quality-gate behavior seeds added in PR 5.

## Scope

### In scope

- Add `scripts/validate_skill_behavior_evals.py`.
- Validate behavior eval JSON shape, referenced skill names, required case fields, duplicate case ids, and quality-gate decision values.
- Wire the validator into `make lint`, `make test-integration`, `make verify`, and the GitHub Actions workflow.
- Add workflow-contract review evidence for the new validation artifact chain.

### Out of scope / non-goals

- Do not add a model-based behavior runner.
- Do not execute prompts or grade natural-language model outputs.
- Do not change existing run-ledger schema or quality-gate behavior text.
- Do not add generated model catalogs, route lockfiles, generated custom agents, review-receiving skills, or branch-completion skills.

## Constraints / Quality targets

- Latency / throughput / resource budgets: validator should be linear over JSON files and local skill metadata; no network or model calls.
- Safety/security/privacy: no external data access; only repository files under the explicit repo root.
- Compatibility / rollout constraints: keep Python stdlib-only and follow existing script CLI conventions.
- Operability: failures must list exact file/case context and required fix.

## Context & Orientation

- Key paths / entry points:
  - `evals/skill-behavior/quality-gate.json`
  - `scripts/validate_skill_trigger_evals.py`
  - `Makefile`
  - `.github/workflows/agent-index.yml`
  - `reports/workflow-contract-review/`
- Existing behavior:
  - Trigger evals are validated by `scripts/validate_skill_trigger_evals.py`.
  - Behavior eval seeds are valid JSON but were intentionally not in `make verify` before this PR.
- Conventions to follow:
  - CLI supports `--repo-root` and defaults to the script's parent repository root.
  - Aggregate schema errors and print one failure header.
- Unknowns:
  - Future non-quality-gate behavior evals may need broader decision vocabularies; this PR validates current quality-gate decision values without adding a runner.

## Design

### Boundary sketch

- Components involved:
  - `scripts/validate_skill_behavior_evals.py`: validates schema and local skill references.
  - `Makefile`: invokes validator in lint and integration checks.
  - `.github/workflows/agent-index.yml`: invokes validator in CI.
- Boundary crossings:
  - Filesystem-only reads under repo root.
- DTOs / interfaces:
  - JSON object with `version`, `skill`, and non-empty `cases`.
  - Case object with `id`, `prompt`, `given`, `expected_decision`, `expected_findings`, and `expected_output_contains`.
- Error handling strategy:
  - Accumulate all validation errors, print exact contexts, and exit non-zero.

### Observability

- Logs: command output reports case count on success and per-error bullets on failure.
- Metrics: not applicable.
- Traces: not applicable.

### Testing strategy

- Unit tests: temp fixture command checks for valid and invalid behavior eval schema.
- Integration tests: `make lint`, `make test-integration`, and `make verify`.
- Manual verification: inspect CI workflow and Makefile wiring.

## Milestones (high-level plan)

1. Add a focused validator script following existing repository validation style.
2. Wire the validator into local and CI verification.
3. Add plan and workflow-contract report evidence.
4. Run targeted fixture checks and canonical verification.

## Progress (WBS)

- [x] (P0) Confirm Red state — deliverable: missing validator command fails — verify: `python3 scripts/validate_skill_behavior_evals.py` returned file-not-found.
- [x] (P1) Add validator — deliverable: `scripts/validate_skill_behavior_evals.py` — verify: targeted valid/invalid fixture checks.
- [x] (P2) Wire verification — deliverable: `Makefile` and `.github/workflows/agent-index.yml` updates — verify: `make lint`, `make test-integration`, `make verify`.
- [x] (P3) Add workflow-contract evidence — deliverable: `reports/workflow-contract-review/20260623-skill-behavior-eval-validator.md` — verify: decision is `submit`.
- [ ] (P4) Publish PR — deliverable: draft PR with explicit URL — verify: GitHub PR created.

## Surprises & Discoveries

- 2026-06-23: `gh` is not installed in this environment, so GitHub PR state is read through the connector surfaces.
- 2026-06-23: Existing `make verify` compiles `scripts/*.py`, so the new script automatically participates in build checks once added.

## Decision log

- 2026-06-23: Keep this PR to schema validation, not model-output grading.
  - Options considered: schema-only validator; prompt execution runner; model-assisted grader.
  - Chosen: schema-only validator.
  - Consequences: behavior seeds become CI-visible without introducing model nondeterminism.
- 2026-06-23: Reuse existing script conventions instead of introducing a shared skill-catalog module.
  - Options considered: duplicate small skill-name loader; shared helper module.
  - Chosen: duplicate the small local loader.
  - Consequences: smallest PR surface; shared helper can be extracted later if more validators need it.

## Function Boundary Evidence

| Function | Concept / invariant | Callers | Semantic neighbors | Decision |
| --- | --- | --- | --- | --- |
| `load_skill_names` | Local skill catalog names from SKILL.md frontmatter | validator main path | `validate_skill_trigger_evals.load_skill_names` parallel concept | keep local copy; avoids cross-script refactor in this PR |
| `require_str` | Required non-empty string field check | case/file validators | `validate_skill_trigger_evals.require_str` same concept | keep local copy; script-local context keeps errors simple |
| `require_str_list` | Required list-of-strings field check | case validator | trigger eval optional list helpers parallel concept | keep; behavior eval requires empty-list control |
| `validate_case` | Per-case schema and decision validation | `validate_file` | no direct behavior eval neighbor | keep; separates case rules from file rules |
| `validate_file` | Per-file behavior eval schema | `validate_skill_behavior_evals` | trigger eval `validate_file` parallel concept | keep; file-level skill field differs |
| `validate_skill_behavior_evals` | Directory aggregation and result contract | `main` | trigger eval `main` aggregation parallel concept | keep; testable boundary for CLI |

Ledger update: not required because this PR does not replace an existing abstraction, keep staged adapters, or intentionally duplicate production abstractions beyond script-local validation helpers.

## Complexity Budget

- Changed files target: 5 files.
- New classes/modules target: 1 new script module.
- New helpers/wrappers/adapters target: 6 small validator helpers.
- New indirection layers target: 0.
- Rough production/check-wiring line budget: <= 220 net lines, excluding plan/report evidence.
- Evidence document budget: bounded to one ExecPlan and one workflow-contract report.

## Post-Implementation Economy Audit

| New abstraction | Justification | Decision | Evidence |
| --- | --- | --- | --- |
| `scripts/validate_skill_behavior_evals.py` | Gives behavior seeds a dedicated CI-visible contract without model execution. | keep | targeted fixture checks and `make verify` pass |
| Script-local validator helpers | Avoid ad hoc repeated type checks while preserving precise error contexts. | keep | invalid fixture reports multiple exact errors |

## Handoff (update at every stop)

- Current branch / commit: `codex/skill-behavior-eval-validator` / pending.
- What is done: validator, Makefile wiring, CI workflow wiring, plan, workflow-contract evidence, targeted fixture checks, and canonical verification.
- What is not done: PR creation, review request, merge, later PRs.
- How to run: `python3 scripts/validate_skill_behavior_evals.py`.
- How to test: targeted temp fixture checks; `make lint`; `make test-integration`; `make verify`.
- Known risks / open questions: future non-quality-gate behavior evals may need a broader decision vocabulary.
- Next 1-3 steps: commit, publish PR, request GitHub review.
- Pointers: start with `scripts/validate_skill_behavior_evals.py` and `evals/skill-behavior/quality-gate.json`.

## Validation & Acceptance

- AC1: Behavior eval files are schema-checked.
  - Verification: `python3 scripts/validate_skill_behavior_evals.py`.
- AC2: Invalid behavior eval fixtures fail with actionable errors.
  - Verification: temp fixture negative checks for unknown skill, duplicate id, and invalid quality-gate decision.
- AC3: Canonical verification includes behavior eval validation locally and in CI.
  - Verification: `make lint`, `make test-integration`, `make verify`, and workflow inspection.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: pending PR; validator and verification wiring implemented locally.
- What went well: existing validator conventions made the new behavior schema check small and deterministic.
- What went wrong: first negative fixture used `status`, which is readonly in zsh; reran with `rc`.
- Follow-ups / tech debt tickets: future behavior runner/grader remains out of scope.
