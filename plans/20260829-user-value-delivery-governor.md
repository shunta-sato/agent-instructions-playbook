# User-value delivery governor — ExecPlan

## Purpose / Big Picture

Feature delivery currently allows routing, artifacts, reviews, CI, structural
cleanup, and speculative hardening to become the work itself. The change makes
observable user capability the governing outcome while preserving concrete
acceptance, safety, security, privacy, data-integrity, compatibility, and
required-check boundaries.

## Scope

### In scope

- Add `user-value-delivery` and make it the feature/campaign governor.
- Calibrate `dev-workflow`, `quality-gate`, structure, observability,
  implementation economy, C++ readability, Claude roles, and Copilot guidance.
- Add advisory/hard structure modes and regression tests.
- Add trigger and behavior evals.

### Out of scope / non-goals

- Rewrite every specialist skill.
- Weaken real safety/security/data-integrity requirements.
- Change approval semantics covered by open PR #73.
- Add a generic orchestration framework or persistent campaign service.

## Constraints / Quality targets

- The common AGENTS/dev-workflow/quality-gate path remains within 600 lines.
- New default-visible skill has at least two positive and three negative trigger
  cases and stays within the 150-line soft limit.
- Feature structure mode blocks new/crossed limits at 1500 source lines, 400
  entrypoint logic lines, and 800 Rust inline-test lines. Existing hard debt allows
  at most 50 net metric lines before becoming a blocking material regression; lower
  thresholds remain advisory.
- Existing canonical validation remains the source of truth.

## Context & Orientation

- `AGENTS.md`: always-on order and generated index.
- `.agents/skills/dev-workflow`: routing and route lock.
- `.agents/skills/quality-gate`: final blocker standard.
- `scripts/check_structure.py`: mechanical two-tier guardrail.
- `.claude/agents`: exact-once worker/reviewer role split.
- Existing issue #93 and closed PR #94 document earlier structure-debt work; this
  plan uses a simpler two-tier feature/strict model rather than importing the
  larger baseline framework.

## Design

### Boundary sketch

- Root governor owns DoD/non-goals, Delivery Control, route lock, candidate, and
  final-gate owner.
- Workers implement one bounded vertical slice and provide focused evidence.
- Reviewers classify concrete blocking versus optional findings.
- Quality gate accepts optional findings with dispositions.

### Observability

- No runtime product path is introduced. Repository CI output and test failures
  are sufficient diagnostics for this instruction change.

### Testing strategy

- Unit tests cover strict/advisory/hard structure behavior and git selection
  modes.
- Trigger evals cover feature campaigns and near-miss tasks.
- Behavior evals cover optional findings, hard boundaries, repeated attempts,
  and scope inversion.
- `make verify` is the final repository gate.

## Milestones (high-level plan)

1. Define the governor and locked feature-delivery contract.
2. Calibrate routing, gate, structure, readability, observability, and economy.
3. Separate orchestrator, worker, and reviewer ownership.
4. Add mechanical/eval coverage and publish one PR.
5. Use CI findings for at most one consolidated correction pass.

## Progress (WBS)

- [x] Inventory open PRs, branches, issue #93, and closed PR #94.
- [x] Define user-value, blocking-finding, and two-tier structure contracts.
- [x] Implement skill and harness-adapter changes.
- [x] Add structure unit tests and skill eval seeds.
- [ ] Publish PR and verify required CI.
- [ ] Record final candidate and outcome after CI.

## Surprises & Discoveries

- 2026-08-29: open PR #73 changes review approval handling, so this change avoids
  `receiving-code-review` and `branch-completion` to prevent semantic conflict.
- 2026-08-29: issue #93's exact structure baseline is robust but substantially
  larger than needed for the present objective; a two-tier checker gives a
  smaller decision change and preserves strict mode for dedicated refactors.

## Decision log

- 2026-08-29: Keep a separate `user-value-delivery` governor because it changes
  scope admission and stopping before risk routing, rather than adding more
  checklist items inside `dev-workflow`.
- 2026-08-29: Use `zero blocking findings` instead of `zero findings`; blocking
  requires a violated criterion and concrete failure path.
- 2026-08-29: Use advisory/hard thresholds instead of a 400-line touched-file
  hard gate; strict mode remains available for structural work.
- 2026-08-29: Keep one final-gate owner per candidate; workers and reviewers do
  not repeat the full chain.

## Handoff

- Current branch / commit: `feat/user-value-delivery-governor` / pending publish.
- What is done: implementation and targeted local structure tests.
- What is not done: GitHub CI result and merge.
- How to run: `make verify`.
- How to test: targeted `python -m unittest tests.test_check_structure tests.test_check_structure_modes` followed by `make verify`.
- Known risks / open questions: other specialist skills may still need later
  calibration if evals show they expand scope despite the route lock.
- Next steps: publish, inspect CI once, batch required fixes, report PR state.
- Pointers: `AGENTS.md`, `user-value-delivery`, `dev-workflow`, `quality-gate`,
  `scripts/check_structure.py`.

## Validation & Acceptance

- AC1: Feature campaigns route through user-value governance before development.
  - Verification: generated index and trigger evals.
- AC2: Optional findings and structure advisories do not block a complete feature.
  - Verification: behavior evals and structure mode unit tests.
- AC3: Concrete boundary defects and hard structure findings still block.
  - Verification: behavior evals and hard-limit tests.
- AC4: Worker/reviewer roles do not repeat the final gate by default.
  - Verification: static workflow-contract review and instruction lint.
- AC5: Repository validators pass.
  - Verification: `make verify` / required CI.

## Outcomes & Retrospective

- What shipped / merged: PR pending.
- Failed, rejected, or abandoned attempts: exact-baseline implementation from
  closed PR #94 was not copied because its larger framework is unnecessary here.
- Failure retrospective:
  - not-triggered: no implementation rollback or repeated failed approach in this branch.
  - report: not applicable.
- Remaining follow-ups / debt: evaluate issue #93 after this policy lands; add an
  explicit baseline only if strict-mode legacy repositories still need it.
