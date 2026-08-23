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
- Route two-or-more executable alternatives from `research-workflow`, while
  preserving `poc-workflow` for one cheapest artifact and `experiment-loop` for
  citable evidence.
- Define an exploration maintenance rule: refactor only when required for the
  next learning step, isolation, comparison integrity, reproducibility, or
  evaluation instrumentation.
- Define blocker-only review with one general pass and a second pass limited to
  previously reported blockers.
- Require a Productization Brief with rebuild-from-contract semantics before
  promotion into delivery.
- Add trigger and behavior evals, generated indexes, and workflow-contract
  evidence.

### Out of scope / non-goals

- Building an orchestration runtime, device harness, variant launcher, or UI.
- Weakening security, privacy, authentication, billing, destructive-operation,
  production-resource, migration, external-side-effect, or physical-safety
  boundaries.
- Treating exploration observations as citable empirical claims.
- Selecting a concrete reviewer model or changing shared Model Routing.
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
- **Model neutrality:** the Skill binds review behavior, not a concrete model;
  only a reviewer actually invokable in the active harness may be used.
- **Context budget:** active `SKILL.md` must remain at or below 150 lines and
  unconditional reach at or below 400 lines.
- **Verification:** all repository validators, tests, generated-file checks, and
  the PR research-promotion/safety boundary must pass.

## Context & Orientation

Primary surfaces:

- `.agents/skills/research-workflow/SKILL.md` — research router.
- `.agents/skills/poc-workflow/` — one cheapest construction artifact.
- `.agents/skills/experiment-loop/SKILL.md` — registered evidence contract.
- `.agents/skills/research-synthesis/SKILL.md` —
  `continue | pivot | kill | promote` decision.
- `.agents/skills/variant-exploration/` — comparative construction and review
  contract.
- `evals/skill-triggers/variant-exploration.json` — trigger and near-miss
  boundaries.
- `evals/skill-behavior/variant-exploration.json` — blocker-only review and
  production-boundary decisions.
- `reports/workflow-contract-review/variant-exploration.md` — workflow and
  claim-boundary review.

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

The reviewer asks only:

> Is this disposable variant safe and valid enough to produce the intended
> learning?

Non-blocking production-quality findings are prohibited. The first pass reports
blockers only; a second pass verifies those blockers only. The contract applies
to whichever reviewer is actually available in the active harness. Concrete
model selection is deliberately outside this PR.

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
- New conditional reference: 1.
- New output template: 1.
- New runtime helper or service: 0.
- Shared Model Routing changes: 0; harness-aware routing is a separate PR.

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
- Canonical repository CI for metadata, context, graph, artifacts, structure,
  submission evidence, unit tests, and promotion/safety boundaries.

## Validation & Acceptance

- **AC1 — routing boundary:** two-or-more disposable executable alternatives
  trigger `variant-exploration`; adjacent near misses do not.
  - Evidence: trigger eval seeds and validator.
- **AC2 — rapid maintenance:** cosmetic or production-oriented cleanup does not
  block exploration; enabling repairs remain allowed.
  - Evidence: Skill/reference contract and behavior evals.
- **AC3 — blocker-only review:** production maintainability advisories and new
  second-pass review findings are prohibited.
  - Evidence: behavior evals and review output contract.
- **AC4 — protected learning:** substrate drift, unsafe side effects, identity
  mismatch, and unsupported claims block or escalate.
  - Evidence: behavior evals.
- **AC5 — production boundary:** promotion uses a Productization Brief and a new
  delivery implementation from contracts.
  - Evidence: synthesis handoff, behavior eval, and workflow-contract review.
- **AC6 — harness honesty:** the Skill does not claim or select a concrete model;
  a mismatched or unidentified model lockfile cannot justify delegation.
  - Evidence: Skill text and absence of Model Routing changes in the PR diff.
- **AC7 — repository verification:** canonical PR workflow is green.
  - Evidence: final GitHub Actions run after the split commit.

## Progress (WBS)

- [x] (P0) Confirm Skill Delta Gate and create this ExecPlan.
- [x] (P1) Add Skill, conditional reference, and Exploration Cycle template.
- [x] (P2) Wire research, PoC, evidence, synthesis, and delivery boundaries.
- [x] (P3) Add trigger and behavior eval coverage.
- [x] (P4) Update Agent Index, README catalog, and Claude Skill link.
- [x] (P5) Complete Agent workflow-contract review.
- [x] (P6) Remove concrete Model Routing changes and record them as a separate
  follow-up PR.
- [ ] (P7) Run full canonical PR verification after the split and record the
  final result.

## Surprises & Discoveries

- 2026-08-23: `poc-workflow` already supplied a useful disposable-code rigor
  floor and reimplementation boundary, but its one-question/one-cheapest-artifact
  stop rule could not own controlled multi-variant comparison.
- 2026-08-23: The first CI run failed only the context-budget gate. Moving the
  detailed operational reference from `requires` to a conditional `resource`
  and reducing `SKILL.md` resolved the finding without raising the budget.
- 2026-08-23: The repository-global Model Catalog and Lockfile are materially
  Claude Code-specific. Treating their selected models as invokable from Codex
  or another harness is unsafe, so Model Routing work was removed from this PR.

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
- 2026-08-23: Split Model Routing into a separate PR.
  - Rationale: Task Class and Capability Profile can be shared, but concrete
    model selection is harness-dependent and must fail closed when the active
    harness cannot invoke the selected model.
- 2026-08-23: Begin with semantic promotion rules and behavior evals rather than
  a mechanical prototype-copy detector.
  - Rationale: add deterministic enforcement only if observed misuse justifies
    the complexity.

## Handoff

- Branch: `feature/variant-exploration`
- Pull request: `#116` (`Add rapid executable variant exploration workflow`)
- What is complete: Skill, workflow wiring, trigger/behavior evals, generated
  surfaces, ExecPlan, and workflow-contract review.
- What remains: post-split CI and PR metadata update.
- Canonical command: `make verify`.
- Read first:
  - `.agents/skills/variant-exploration/SKILL.md`
  - `.agents/skills/variant-exploration/references/variant-exploration.md`
  - `evals/skill-behavior/variant-exploration.json`
  - `reports/workflow-contract-review/variant-exploration.md`
- Separate follow-up: harness-aware Model Routing with explicit harness identity,
  fail-closed mismatch behavior, and no cross-harness fallback.

## Outcomes & Retrospective

- Delivered in PR #116:
  - comparative executable exploration lane;
  - enabling-only maintenance policy;
  - blocker-only review with bounded passes;
  - evidence/identity/controlled-substrate protection;
  - Productization Brief and rebuild-from-contract boundary.
- Failed/rejected attempts:
  - Initial unconditional context surface exceeded policy; corrected through
    Progressive Disclosure.
  - Initial Model Routing addition assumed a repository-global concrete route;
    removed after identifying the missing harness-invokability boundary.
- Failure retrospective:
  - not triggered: both findings were detected before merge and corrected in the
    same workstream; no rollback or repeated unresolved failure remains.
- Remaining follow-ups:
  - harness-aware Model Routing PR;
  - telemetry-gated artifact structure enforcement;
  - telemetry-gated prototype-source leakage lint.
