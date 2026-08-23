# Variant exploration and blocker-only review — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**,
> **Surprises & Discoveries**, and **Handoff** current.

## Purpose / Big Picture

Add a first-party research workflow that converts lower agentic implementation
cost into more executable product-learning cycles. Agents may build, compare,
and discard multiple variants rapidly without applying production
maintainability review to disposable code.

The workflow must preserve protected boundaries, comparison integrity, evidence
discipline, and a clean production boundary: selected behavior is rebuilt from
confirmed contracts rather than grown from prototype source.

## Scope

### In scope

- Add `variant-exploration` with a compact `SKILL.md`, detailed conditional
  reference, and Exploration Cycle template.
- Route two-or-more executable alternatives from `research-workflow` while
  preserving `poc-workflow` for one cheapest artifact and `experiment-loop` for
  citable evidence.
- Define an exploration maintenance rule: refactor only when needed for the
  next learning step, isolation, comparison integrity, reproducibility, or
  required instrumentation.
- Define a blocker-only review profile with one general pass and a second pass
  limited to previously reported blockers.
- Require a Productization Brief with rebuild-from-contract semantics before
  promotion into delivery.
- Add trigger, behavior, model-routing, workflow-contract, and generated-index
  coverage.

### Out of scope / non-goals

- Building an orchestration runtime, device harness, variant launcher, or UI.
- Weakening security, privacy, authentication, billing, destructive-operation,
  production-resource, migration, external-side-effect, or physical-safety
  boundaries.
- Treating exploration observations as citable empirical claims.
- Assigning a concrete model to a new capability without smoke evidence.
- Adding a prototype-source leakage lint or persistent artifact schema before
  operational evidence shows they are needed.
- Changing production `dev-workflow`, `quality-gate`, or `hardening-workflow`
  semantics.

## Constraints / Quality targets

- **Mode:** relaxed exploration rules apply only in `research` mode with a
  recorded boundary-gate receipt.
- **Safety/security/privacy:** protected boundaries remain mandatory in every
  mode.
- **Review scope:** findings are allowed only for unsafe execution, blocked
  scenarios, invalid comparison/evidence/identity, protected-boundary breaches,
  or blockers to the next learning step.
- **Review exclusions:** naming, DRY, abstraction shape, module layout, broad
  test coverage, production observability, documentation, and future
  extensibility are not findings unless they invalidate current learning.
- **Context budget:** active `SKILL.md` must remain at or below 150 lines and
  unconditional reach at or below 400 lines.
- **Compatibility:** existing single-PoC, experiment, synthesis, promotion, and
  delivery responsibilities remain explicit and non-overlapping.
- **Verification:** all repository validators, tests, generated-file checks, and
  the PR research-promotion/safety boundary must pass.

## Context & Orientation

Primary surfaces:

- `.agents/skills/research-workflow/SKILL.md` — research router.
- `.agents/skills/poc-workflow/` — one cheapest construction artifact.
- `.agents/skills/experiment-loop/SKILL.md` — registered evidence contract.
- `.agents/skills/research-synthesis/SKILL.md` —
  `continue | pivot | kill | promote` decision.
- `.agents/skills/variant-exploration/` — new comparative construction and
  review contract.
- `.agents/model-routing/` — task class, capability profile, catalog, and
  generated route decision.
- `evals/skill-triggers/`, `evals/skill-behavior/`, and
  `evals/model-routing/` — executable contract seeds.
- `reports/workflow-contract-review/variant-exploration.md` — source/consumer
  and claim-boundary review.

The target project continues to own its devices, fixtures, data, accounts,
commands, architecture, and production requirements.

## Design

### Workflow

```text
research-workflow
  ├─ one cheapest artifact → poc-workflow
  ├─ citable empirical probe → experiment-loop
  └─ 2+ executable alternatives → variant-exploration
          ↓
      keep | mutate | drop
          ↓
      research-synthesis
          ↓ promote
      Productization Brief
          ↓
      dev-workflow intent: feature
          ↓
      new production implementation from contracts
```

### Exploration boundary model

Every touched surface is classified as:

1. **Protected boundary** — never relaxed.
2. **Controlled substrate** — fixed within one comparison block.
3. **Variation axis** — intentionally changed between variants.
4. **Disposable surface** — prototype-local implementation that may be thrown
   away.

### Maintenance rule

A refactor is permitted only to:

- keep the next planned variant within budget;
- restore variant isolation or comparison integrity;
- remove a shared defect contaminating multiple variants;
- restore reproducible build/run behavior; or
- add instrumentation required by the declared evaluation protocol.

The stopping criterion is “exploration can continue,” not “the code is clean.”

### Review rule

The routine reviewer asks only:

> Is this disposable variant safe and valid enough to produce the intended
> learning?

Non-blocking production-quality findings are prohibited. The first pass reports
blockers only; a second pass verifies those blockers only. Protected-boundary,
contradictory-evidence, controlled-substrate, and promotion decisions escalate
to high-reasoning review.

### Evidence and promotion

Informal observations may choose the next variant but cannot support an
empirical claim. Claims route through `experiment-loop`. Promotion requires:

```yaml
promotion_strategy: rebuild-from-contract
prototype_source_authority: non-authoritative
```

Prototype runtime code cannot enter delivery by copy, move, rename, import, or
incremental cleanup.

### Responsibility and complexity budget

- New active Skill: 1.
- New capability profile: 1.
- New task class: 1.
- New output template: 1.
- New runtime helper or service: 0.
- Detailed operational policy resides in a conditional Resource rather than
  unconditional Skill reach.

### Testing strategy

- Trigger positives for mobile UX variants, quality-attribute variants,
  convergence, and blocker-only review.
- Near-miss negatives for single PoC, one experiment, paper architecture,
  production implementation, hardening, and Figma-only ideation.
- Behavior cases proving duplication, smoke-only verification, and a large
  prototype file do not become findings.
- Behavior blockers for substrate drift, production side effects, identity
  mismatch, unsupported quantitative claims, advisory over-review, second-pass
  scope creep, and prototype-source promotion.
- Model-routing case proving bounded review is selected before high-reasoning
  review unless escalation is explicit.
- Canonical repository CI for metadata, context, graph, artifacts, structure,
  submission evidence, unit tests, and promotion/safety boundaries.

## Validation & Acceptance

- **AC1 — routing boundary:** two-or-more disposable executable alternatives
  trigger `variant-exploration`; adjacent near misses do not.
  - Evidence: `evals/skill-triggers/variant-exploration.json` and trigger-eval
    validator.
- **AC2 — rapid maintenance:** cosmetic or production-oriented cleanup does not
  block exploration; enabling repairs remain allowed.
  - Evidence: Skill/reference contract and behavior evals.
- **AC3 — blocker-only review:** production maintainability advisories and new
  second-pass review findings are prohibited.
  - Evidence: behavior evals and `variant_exploration_review` success criteria.
- **AC4 — protected learning:** substrate drift, unsafe side effects, identity
  mismatch, and unsupported claims block or escalate.
  - Evidence: behavior evals.
- **AC5 — production boundary:** promotion uses a Productization Brief and a new
  delivery implementation from contracts.
  - Evidence: synthesis handoff, behavior eval, and workflow-contract review.
- **AC6 — model scope:** routine exploration review does not default to a
  high-reasoning production reviewer merely because one is available.
  - Evidence: model-routing eval and generated route lockfile.
- **AC7 — repository verification:** canonical PR workflow is green.
  - Evidence: GitHub Actions run `32617158045` for commit
    `bd84762070e8b06686bcff09d0efeada3c83aef4`; all 23 substantive validation
    steps succeeded.

## Progress (WBS)

- [x] (P0) Confirm Skill Delta Gate and create this ExecPlan.
- [x] (P1) Add Skill, conditional reference, and Exploration Cycle template.
- [x] (P2) Wire research, PoC, evidence, synthesis, and delivery boundaries.
- [x] (P3) Add bounded reviewer capability/task routing and generated lockfile.
- [x] (P4) Add trigger, behavior, and model-routing eval coverage.
- [x] (P5) Update Agent Index, README catalog, and Claude Skill link.
- [x] (P6) Complete Agent workflow-contract review.
- [x] (P7) Run full canonical PR verification and record the result.

## Surprises & Discoveries

- 2026-08-23: `poc-workflow` already supplied a useful disposable-code rigor
  floor and reimplementation boundary, but its one-question/one-cheapest-artifact
  stop rule could not own controlled multi-variant comparison.
- 2026-08-23: No model has evidence-backed membership in the new
  `exploration_evidence_review` profile. The resolver therefore records a
  transparent fallback to `focused_code_edit`; high-reasoning review remains an
  escalation route rather than a false default capability claim.
- 2026-08-23: The first CI run (`32617054909`) failed only the context-budget
  gate: the initial Skill was 185 lines and unconditional reach was 489 lines.
  Moving the 304-line operational reference from `requires` to a conditionally
  loaded `resource` and reducing `SKILL.md` to 121 lines resolved both findings.
- 2026-08-23: The second CI run (`32617158045`) passed every substantive step,
  including context budget, instruction graph, command-doc drift, artifact and
  structure checks, submission evidence, unit tests, and research
  promotion/safety boundaries.

## Decision log

- 2026-08-23: Add a dedicated `variant-exploration` Skill rather than broadening
  `poc-workflow` or invoking it repeatedly.
  - Rationale: comparative construction changes runtime routing, controlled
    variables, review policy, and output contracts.
- 2026-08-23: Treat production maintainability as a temporary non-objective,
  while preserving enough local changeability for the next learning step.
  - Rationale: neither full neglect nor production polish serves rapid,
    trustworthy exploration.
- 2026-08-23: Make exploration review blocker-only and prohibit advisory
  findings.
  - Rationale: severity filtering still permits unbounded low-priority review;
    disposable code should not accumulate a production-debt backlog.
- 2026-08-23: Use one general review pass and a known-blocker-only second pass.
  - Rationale: prevents review scope from reopening after every fix.
- 2026-08-23: Add a capability profile and task class without adding unsupported
  concrete-model capability claims.
  - Rationale: route evidence must precede catalog promotion.
- 2026-08-23: Begin with semantic promotion rules and behavior evals rather than
  a mechanical prototype-copy detector.
  - Rationale: add deterministic enforcement only if observed misuse justifies
    the complexity.
- 2026-08-23: Move detailed policy behind a conditional Resource after the
  context-budget finding.
  - Rationale: routing and hard rules stay visible; full operational detail is
    loaded only when executing a cycle, review, or Productization Brief.

## Handoff

- Branch: `feature/variant-exploration`
- Pull request: `#116` (`Add rapid executable variant exploration workflow`)
- Implementation validation: GitHub Actions run `32617158045`, success.
- What is complete: Skill, workflow wiring, model routing, evals, generated
  surfaces, ExecPlan, workflow-contract review, and canonical validation.
- What remains: final documentation-only commit validation and normal PR review.
- Canonical command: `make verify`.
- Read first:
  - `.agents/skills/variant-exploration/SKILL.md`
  - `.agents/skills/variant-exploration/references/variant-exploration.md`
  - `evals/skill-behavior/variant-exploration.json`
  - `reports/workflow-contract-review/variant-exploration.md`
- Open follow-ups: add artifact-schema or prototype-leakage lint only after
  operational evidence shows field drift or source laundering.

## Outcomes & Retrospective

- Delivered in PR #116:
  - comparative executable exploration lane;
  - enabling-only maintenance policy;
  - blocker-only review with bounded passes;
  - evidence/identity/controlled-substrate protection;
  - Productization Brief and rebuild-from-contract boundary;
  - bounded reviewer model routing and regression evals.
- Failed/rejected attempts:
  - Initial unconditional context surface exceeded policy; corrected by
    Progressive Disclosure rather than raising the budget.
  - Direct network clone was unavailable in this execution environment; GitHub
    connector writes and canonical GitHub Actions supplied repository execution.
- Failure retrospective:
  - not triggered: one mechanically detected integration finding was corrected
    in the next attempt; no repeated materially different failures, rollback,
    rejected completion claim, or reusable process failure occurred.
- Remaining follow-ups:
  - telemetry-gated artifact structure enforcement;
  - telemetry-gated prototype-source leakage lint;
  - smoke evaluation before assigning a concrete model directly to
    `exploration_evidence_review`.
