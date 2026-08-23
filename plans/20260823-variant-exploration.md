# Variant exploration and blocker-only review — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

Add a first-party research workflow that turns lower agentic implementation cost
into more executable product-learning cycles. The workflow must let agents build
and discard multiple variants rapidly, while preserving safety, comparison
integrity, evidence discipline, and a clean rebuild-from-contract boundary for
production implementation.

The change also prevents high-reasoning reviewers from applying production
maintainability review to disposable exploration code. Exploration review is a
blocker-only learning-integrity gate; full maintainability review resumes after
promotion into delivery mode.

## Scope

### In scope

- Add `variant-exploration` with a compact `SKILL.md`, detailed reference, and
  Exploration Cycle template.
- Route comparative construction from `research-workflow`, while preserving
  `poc-workflow` for one cheapest artifact and `experiment-loop` for evidence.
- Require a Productization Brief and rebuild-from-contract semantics at
  `research-synthesis`.
- Add blocker-only review rules, one-pass/known-blocker-only review limits, and
  behavior evals that reject production-quality advisory findings.
- Add a model-routing task/profile that avoids high-reasoning review by default
  and escalates only on explicit boundaries.
- Add trigger, behavior, and model-routing evals plus generated indexes/links.
- Produce the required workflow-contract review and run the canonical
  verification chain.

### Out of scope / non-goals

- Building an orchestration runtime, variant launcher, device harness, or UI.
- Adding a persistent artifact kind or mechanical source-copy detector before
  telemetry shows a need.
- Naming a concrete GPT model in reusable skills or routing files.
- Weakening security, privacy, destructive-operation, evidence, or promotion
  gates.
- Changing delivery-mode production implementation or hardening semantics.

## Constraints / Quality targets

- Latency / throughput / resource budgets: not applicable; this is an
  instruction and validation change.
- Safety/security/privacy: protected boundaries remain mandatory in every mode;
  no production side effects or sensitive data are authorized by exploration.
- Compatibility / rollout constraints: existing PoC, experiment, research
  synthesis, and delivery routes retain their current responsibilities; the new
  route must have explicit near-miss negatives.
- Operability: no runtime service is added. Generated indexes, Claude symlink,
  model route lockfile, eval seeds, and workflow report must remain
  machine-valid.
- Review discipline: exploration review may report only safety,
  learning-integrity, identity/evidence, controlled-substrate, or next-step
  blockers; non-blocking production-quality findings are prohibited.

## Context & Orientation

- `AGENTS.md` is the generated always-on index and workflow contract.
- `.agents/skills/research-workflow/SKILL.md` routes research work.
- `.agents/skills/poc-workflow/` owns one cheapest construction artifact.
- `.agents/skills/experiment-loop/SKILL.md` owns registered evidence.
- `.agents/skills/research-synthesis/SKILL.md` owns
  `continue | pivot | kill | promote`.
- `.agents/model-routing/*` separates task classes, capability profiles, model
  catalog, and generated route decisions.
- `evals/skill-triggers/` tests trigger and near-miss boundaries.
- `evals/skill-behavior/` tests runtime decisions and forbidden reviewer
  behavior.
- `reports/workflow-contract-review/` is required because Agent-facing workflow
  surfaces change.
- Unknown: whether telemetry will later justify a mechanical prototype-source
  leakage lint. This PR records the semantic rule and behavior eval first.

## Design

### Boundary sketch

- Components involved (and their roles):
  - `variant-exploration`: comparative construction and evaluation contract.
  - `research-workflow`: mode router.
  - `poc-workflow`: single-artifact anti-overlap boundary.
  - `experiment-loop`: citable evidence boundary.
  - `research-synthesis`: convergence and promotion boundary.
  - model routing: blocker-only default review profile and explicit escalation.
  - evals/validators: trigger and decision enforcement.
- Boundary crossings:
  - research paths remain disposable;
  - promotion into delivery paths requires a Productization Brief,
    acknowledgment/evidence, `dev-workflow`, and `quality-gate`;
  - prototype runtime source remains non-authoritative.
- DTOs / interfaces:
  - Exploration Cycle Record and Productization Brief are Markdown contracts,
    not runtime schemas in this phase.
- Error handling:
  - no research receipt means no relaxed profile;
  - controlled-substrate drift or protected-boundary breach blocks comparison;
  - unsupported quantitative claims escalate to `experiment-loop`;
  - promotion by copy/move/cleanup is blocked.

### Responsibility layout

| Unit | Responsibility | Reason to change |
| --- | --- | --- |
| `variant-exploration/SKILL.md` | routing-level comparative workflow | exploration decision protocol changes |
| `references/variant-exploration.md` | detailed construction/review/evidence rules | operational detail changes |
| `templates/exploration-cycle.md` | record and handoff skeleton | output contract changes |
| research adjacent skills | explicit handoff/anti-trigger boundaries | ownership boundary changes |
| model routing files | bounded default reviewer and escalation | model-role policy changes |
| eval files | trigger/behavior/routing regression seeds | executable contract changes |

### Complexity budget

- New active skill: 1, justified by a runtime decision delta from single-PoC
  construction to comparative variant selection.
- New capability profile: 1.
- New task class: 1.
- New templates: 1.
- New runtime code or helper scripts: 0.
- Mechanical artifact kind or lint: deferred until misuse telemetry exists.

### Observability

- No runtime behavior is introduced.
- Validation output from `make verify`, generated-index checks, model-routing
  validation, eval validation, artifact lint, and workflow-contract review is
  the observable evidence.

### Testing strategy

- Trigger evals: positive executable-comparison cases and near-miss negatives
  for PoC, experiment, architecture, delivery, hardening, and paper ideation.
- Behavior evals: duplicated code, smoke-only tests, and a long file must pass;
  unequal substrate, production side effects, identity mismatch, unsupported
  claims, advisory over-review, second-pass scope creep, and source promotion
  must be handled as specified.
- Model-routing eval: the new task falls back to a bounded focused profile even
  when a higher-reasoning candidate exists, with escalation remaining explicit.
- Integration: canonical `make verify`.
- Manual review: replay the research → variant → synthesis → delivery chain and
  inspect generated indexes and Claude link.

## Milestones (high-level plan)

1. Define the new comparative exploration contract, maintenance rule, review
   scope, and output template.
2. Wire the contract into adjacent research and promotion workflows with
   explicit anti-overlap boundaries.
3. Add bounded model routing and executable trigger/behavior/routing evals.
4. Regenerate Agent/README indexes, Claude skill links, and the route lockfile.
5. Complete workflow-contract review, run canonical verification, and open the
   pull request with exact evidence.

## Progress (WBS)

- [x] (P0) Classify risk, intent, affected workflows, and Skill Delta Gate —
  deliverable: this ExecPlan — verify: artifact lint.
- [x] (P1) Add `variant-exploration` Skill/reference/template — deliverable:
  `.agents/skills/variant-exploration/` — verify: skill metadata and context
  budget validators.
- [x] (P2) Wire research, PoC, synthesis, and rebuild boundaries — deliverable:
  adjacent Skill edits — verify: trigger evals and workflow-contract review.
- [x] (P3) Add blocker-only reviewer routing — deliverable: capability profile,
  task class, route lockfile, routing eval — verify: model-routing validators.
- [x] (P4) Add trigger and behavior regression seeds — deliverable:
  `evals/skill-triggers/variant-exploration.json` and
  `evals/skill-behavior/variant-exploration.json` — verify: eval validators.
- [x] (P5) Update generated indexes and Claude link — deliverable:
  `AGENTS.md`, `README.md`, `.claude/skills/variant-exploration` — verify:
  generator/sync checks.
- [x] (P6) Review Agent-facing contract — deliverable:
  `reports/workflow-contract-review/variant-exploration.md` — verify:
  artifact lint.
- [ ] (P7) Run full canonical verification and record final result —
  deliverable: green PR checks and updated Handoff/Outcomes — verify:
  `make verify`.

## Surprises & Discoveries

- 2026-08-23: Existing `poc-workflow` already removes several delivery-quality
  obligations and requires re-implementation on promotion, but its one-question,
  cheapest-artifact stop rule cannot own multi-variant comparison without
  weakening its trigger boundary.
- 2026-08-23: The model catalog has no evidence-backed
  `exploration_evidence_review` candidate. The resolver therefore uses an
  explicit fallback to `focused_code_edit` rather than falsely granting the new
  capability profile; high-reasoning review remains an escalation target.

## Decision log

- 2026-08-23: Add a new `variant-exploration` Skill instead of broadening
  `poc-workflow`.
  - Options considered: extend PoC; compose repeated PoCs; add a dedicated Skill.
  - Chosen: dedicated Skill.
  - Consequences: clear multi-variant trigger/output contract and preserved
    single-PoC stop semantics.
- 2026-08-23: Treat maintainability as a temporary non-objective but retain
  local changeability as an exploration constraint.
  - Options considered: ignore maintainability; apply production review; use an
    enabling-refactor rule.
  - Chosen: refactor only when it restores budget, isolation, reproducibility,
    instrumentation, or comparison integrity.
  - Consequences: rapid loops without allowing exploration substrate collapse.
- 2026-08-23: Make exploration review blocker-only and prohibit advisory
  findings.
  - Options considered: normal review with severity filtering; deferred
    advisory backlog; strict blocker-only contract.
  - Chosen: one review pass plus known-blocker verification only.
  - Consequences: high-capability reviewers cannot consume the exploration
    budget with production-quality polish.
- 2026-08-23: Use capability fallback rather than assigning a concrete model to
  the new review profile without smoke evidence.
  - Options considered: add the profile directly to an existing model; default
    to high-reasoning review; transparent fallback.
  - Chosen: transparent fallback to `focused_code_edit`, explicit escalation to
    `high_reasoning_review`.
  - Consequences: route lockfile records the limitation and avoids a false
    capability claim.
- 2026-08-23: Start with semantic promotion rules and behavior evals rather than
  a source-copy lint.
  - Options considered: immediate import/copy detector; artifact schema; staged
    enforcement.
  - Chosen: staged enforcement.
  - Consequences: smaller change; add a mechanical lint only if telemetry shows
    prototype leakage.

## Handoff (update at every stop)

- Current branch / commit: `feature/variant-exploration`; initial commit pending.
- What is done: Skill design, adjacent routing, model-routing design, evals,
  plan, and workflow-contract review content are prepared.
- What is not done: GitHub commit, PR creation, CI execution, and final evidence
  update.
- How to run: `make verify`.
- How to test: run the canonical command above; inspect generated index, route
  lockfile, eval validators, artifact lint, and research boundary gate output.
- Known risks / open questions:
  - generated files must exactly match repository generators;
  - full local checkout is unavailable in this execution environment, so GitHub
    Actions will provide the canonical full-repository execution.
- Next 1–3 steps:
  1. Commit the complete change set on the feature branch.
  2. Open a draft PR and inspect all workflow results.
  3. Fix any failures, update this plan, and mark the PR ready.
- Pointers:
  - `.agents/skills/variant-exploration/SKILL.md`
  - `.agents/skills/variant-exploration/references/variant-exploration.md`
  - `.agents/skills/research-workflow/SKILL.md`
  - `.agents/model-routing/task-classes.yml`
  - `evals/skill-behavior/variant-exploration.json`

## Validation & Acceptance

- AC1: Requests for two or more disposable executable alternatives route to
  `variant-exploration`, while single PoCs, registered experiments, paper
  architecture analysis, delivery features, and hardening do not.
  - Verification: trigger eval seeds and `validate_skill_trigger_evals.py`.
- AC2: Exploration maintenance work is permitted only when it enables the next
  learning step or restores safety/comparison integrity.
  - Verification: Skill/reference contract plus behavior evals for duplication,
    broad testing, and large-file near misses.
- AC3: Exploration reviewers report only blockers and cannot append production
  maintainability advisories or start a new general second-pass review.
  - Verification: behavior evals and strict review output contract.
- AC4: Protected boundaries, identity, controlled substrate, and evidence
  limits remain blocking.
  - Verification: behavior evals for production side effects, substrate drift,
    identity mismatch, and unsupported claims.
- AC5: Promotion requires a Productization Brief and a new delivery
  implementation from contracts, not prototype-source cleanup.
  - Verification: adjacent workflow text, promotion behavior eval, and
    workflow-contract review.
- AC6: Default variant review routing does not select a high-reasoning review
  profile merely because one is available.
  - Verification: model-routing eval and generated route lockfile.
- AC7: All repository validators and tests pass.
  - Verification: `make verify` and GitHub Actions.

## Outcomes & Retrospective

- What shipped / merged: pending PR.
- Failed, rejected, or abandoned attempts:
  - Direct network clone was unavailable in the execution environment; the
    implementation uses the GitHub connector and canonical CI for full
    repository verification.
- Failure retrospective:
  - not-triggered: no repeated material implementation failure or rejected
    completion claim at this stage.
  - report: not applicable.
- Remaining follow-ups / debt:
  - Consider artifact-registry enforcement for Exploration Cycle Records only
    if field drift appears.
  - Consider prototype-source leakage lint only if actual promotion misuse is
    observed.
