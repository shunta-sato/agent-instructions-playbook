---
name: variant-exploration
description: "Use in research mode when two or more disposable executable variants must be built and compared to discover product behavior, UX/workflow, or quality-attribute trade-offs. Covers controlled comparison, blocker-only exploration review, and rebuild-from-contract handoff. Do not use for a single cheapest PoC, one registered experiment, paper-only architecture analysis, or delivery implementation."
metadata:
  short-description: Executable variant exploration
  requires:
    - references/variant-exploration.md
  templates:
    - templates/exploration-cycle.md
---

## Purpose

Use this skill to turn lower implementation cost into more learning cycles rather
than premature production polish. It coordinates multiple disposable executable
variants, keeps their comparison trustworthy, and converts the selected behavior
into a productization contract.

The optimization target is **decision quality per unit cost**. Production
maintainability is not ignored; it is temporarily removed from the objective
function. Exploration code keeps only enough local changeability to sustain the
next planned learning step.

## When to use

Use this skill only in `research` mode when all are true:

- two or more executable alternatives are intentionally being constructed
- the alternatives answer one product, UX/workflow, or quality-attribute decision
- the alternatives can share a controlled evaluation protocol
- the implementation is disposable and will not be shipped as the production implementation

Examples include comparing three mobile interaction models on devices, comparing
startup/memory/cache trade-offs through runnable variants, or combining retained
behavior from several variants into a final product contract.

Do not use for:

- one cheapest prototype answering one feasibility question — use `$poc-workflow`
- one evidence-bearing hypothesis and metric — use `$experiment-loop`
- an implementation-free architecture option comparison — use `$architecture-decision-analysis`
- confirmed product behavior being implemented for delivery — use `$dev-workflow`
- quality improvement on existing delivery code — use `$hardening-workflow`

## Boundaries

- `$research-workflow` owns mode routing and research framing.
- `$variant-exploration` owns comparative construction, shared evaluation,
  exploration review discipline, and the convergence package.
- `$experiment-loop` owns every citable empirical claim.
- `$research-synthesis` owns `continue | pivot | kill | promote`.
- Promotion re-enters `$dev-workflow` as `feature`; exploration exemptions do not
  cross the research/delivery boundary.

## How to use

0) Open `references/variant-exploration.md`. Confirm and record research mode plus
the working-tree boundary gate before claiming any exploration exemption:

```sh
python3 scripts/check_research_evidence.py --working-tree \
  --policy .agents/project-policy.yml --mode research
```

No mode receipt means no relaxed exploration profile.

1) Frame the cycle before implementation:

- `cycle_id`
- decision question and the product decision it unlocks
- variant count/time/cost budget
- shared scenarios and evaluation protocol
- stop condition and synthesis point

2) Classify every touched surface:

- **protected boundary** — never relaxed: security, privacy, secrets,
  authentication/authorization, billing, destructive operations, production
  resources, persistent migrations, external side effects, physical safety
- **controlled substrate** — fixed inside the comparison cycle: base revision,
  fixture/backend, data, account, device/OS, network profile, build mode
- **variation axes** — intentionally changed between variants
- **disposable surface** — prototype-local presentation, wiring, state,
  abstractions, fixtures, and smoke checks

Prefer fakes, sandboxes, test accounts, disposable databases, and reversible
local state at protected boundaries.

3) Define the evaluation protocol before building variants. Record shared user
scenarios, human rubric, machine measurements, source/build/target identity, and
what counts as `pass`, `inconclusive`, or `invalid comparison`. An observation
may steer the next variant, but a citable quantitative claim must be handed to
`$experiment-loop` for fresh registered confirmation.

4) Create one Variant Brief per alternative. Fix the controlled substrate, name
the primary variation axis, isolate writable files or worktrees, state the
variant-specific hypothesis, and define the smoke command plus stop condition.

5) Build only to the exploration rigor floor:

- each variant starts and can execute the shared scenarios
- variant identity and source/build/target/configuration identity are recordable
- the safety overlay and protected boundaries hold
- comparison instrumentation is sufficient for the declared evaluation
- common-substrate failures can be distinguished from variant-specific failures

Production architecture, DRY, broad unit-test coverage, production observability,
future extensibility, and comprehensive documentation are not required unless
one directly determines the current product question.

6) Apply the exploration maintenance rule. Refactor only when needed to:

- keep the next planned variant within budget
- restore variant isolation or comparison integrity
- remove a shared defect that contaminates multiple variants
- restore reproducible build/run behavior
- add the instrumentation required by the evaluation protocol

Stop refactoring as soon as exploration can continue. Do not refactor merely
because code is duplicated, a file is large, an abstraction is inelegant, or a
production review would prefer another structure.

7) Run exactly one blocker-only exploration review. The reviewer asks only:

**Is this variant safe and valid enough to produce the intended learning?**

Report a finding only when it makes execution unsafe, blocks a declared
scenario, invalidates comparison/evidence/identity, crosses a protected
boundary, or blocks the next planned learning step. Every finding must name the
learning or protected boundary it invalidates and the minimum fix.

Non-blocking production-quality findings are prohibited. After blocker fixes, a
second pass verifies only the reported blockers; it must not open a fresh
general review cycle. Use model-routing task class
`variant_exploration_review`; escalate to high-reasoning review only for a
protected-boundary breach, contradictory evidence, a controlled-substrate
decision, or promotion.

8) Evaluate each variant as `keep | mutate | drop`. Record retained knowledge and
rejected behavior; do not create a production technical-debt backlog for
disposable code.

9) Stop at the recorded budget or decision point and hand the cycle to
`$research-synthesis`. On a promotion candidate, produce a Productization Brief
that states:

- selected Feature, Interaction, Quality, and API Contracts
- accepted claim IDs and explicit evidence limits
- rejected variants and retained knowledge
- open uncertainties
- `promotion_strategy: rebuild-from-contract`
- `prototype_source_authority: non-authoritative`
- exploration code disposition and approved reusable non-runtime artifacts

Prototype runtime code is not promoted by copy, move, rename, import, or gradual
cleanup. Delivery implementation starts from the confirmed contracts and passes
the full delivery workflow.

## Hard rules

- Rapid means narrower objective and review scope, not weaker safety boundaries.
- A reviewer may not emit naming, DRY, abstraction, module layout, broad testing,
  documentation, production observability, or future-extensibility findings
  unless the issue directly invalidates current learning.
- Do not retain a long list of advisory findings for disposable code.
- No empirical claim without an experiment/claim ID.
- Do not silently vary the controlled substrate between alternatives.
- Do not let exploration code become authoritative production source.
- Stop when the decision is unlocked; extra prototype scope is not progress.

## Output expectation

Produce an Exploration Cycle Record using
`templates/exploration-cycle.md`, normally under
`research/explorations/<cycle-id>/cycle.md`, containing:

- mode receipt, question, budget, stop condition
- protected/controlled/variation/disposable classification
- evaluation protocol and identity fields
- Variant Briefs and `keep | mutate | drop` decisions
- blocker-only review decision (`pass | block | escalate`)
- observations versus registered evidence
- retained and rejected knowledge
- handoff to `$research-synthesis`
- Productization Brief when promotion is recommended
