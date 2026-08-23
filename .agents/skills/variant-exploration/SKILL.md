---
name: variant-exploration
description: "Use in research mode when two or more disposable executable variants must be built and compared to discover product behavior, UX/workflow, or quality-attribute trade-offs. Covers controlled comparison, blocker-only exploration review, and rebuild-from-contract handoff. Do not use for a single cheapest PoC, one registered experiment, paper-only architecture analysis, or delivery implementation."
metadata:
  short-description: Executable variant exploration
  resources:
    - references/variant-exploration.md
  templates:
    - templates/exploration-cycle.md
---

## Purpose

Compare disposable executable alternatives to improve product decisions per unit
cost. Production maintainability is temporarily removed from the optimization
target; retain only enough local changeability to complete the next learning step.

## When to use

Use only in `research` mode when two or more executable alternatives intentionally
answer one product, UX/workflow, or quality-attribute decision under a shared
evaluation protocol, and the implementations will not ship.

Do not use for one cheapest feasibility artifact (`$poc-workflow`), one registered
hypothesis (`$experiment-loop`), implementation-free architecture comparison
(`$architecture-decision-analysis`), confirmed delivery work (`$dev-workflow`), or
quality improvement on shipped code (`$hardening-workflow`).

## Boundaries

- `$research-workflow` owns mode routing.
- This skill owns comparative construction, evaluation, blocker-only review, and
  the convergence package.
- `$experiment-loop` owns citable empirical claims.
- `$research-synthesis` owns `continue | pivot | kill | promote`.
- Promotion re-enters `$dev-workflow` as `feature`; no exploration exemption crosses
  into delivery.

## How to use

0) Record research mode and run the boundary gate before claiming exemptions:

```sh
python3 scripts/check_research_evidence.py --working-tree \
  --policy .agents/project-policy.yml --mode research
```

1) Before implementation, record cycle ID, decision question, decision unlocked,
variant/time/cost budget, shared scenarios, evaluation protocol, and stop/synthesis
point.

2) Classify touched surfaces:

- **protected boundary** — never relaxed: security, privacy, secrets, auth, billing,
  destructive operations, production resources, persistent migrations, external
  side effects, and physical safety
- **controlled substrate** — fixed within a comparison: revision, fixture/backend,
  data/account, target/OS, network, and build mode
- **variation axes** — intentionally changed
- **disposable surface** — prototype-local presentation, wiring, state,
  abstractions, fixtures, and smoke checks

3) Define shared scenarios, human rubric, machine measurements, and
source/build/target/protocol identity before building. Observations may select the
next variant; quantitative or otherwise citable claims require fresh
`$experiment-loop` registration.

4) Give every variant an isolated Variant Brief: ID, base revision, primary axis,
hypothesis, controlled substrate, allowed files, forbidden boundaries, smoke command,
evaluation scenarios, and stop condition.

5) Build only to the exploration floor: variants run the shared scenarios; identity
is recordable; protected boundaries hold; required instrumentation exists; and
shared-substrate failures can be separated from variant failures. Production
architecture, DRY, broad tests, production observability, documentation, and future
extensibility are out of scope unless they determine the current decision.

6) Refactor only to keep the next variant within budget, restore isolation or
comparison integrity, remove a shared contaminating defect, restore reproducibility,
or add required instrumentation. Stop once exploration can continue. Duplication,
large files, naming, abstraction elegance, and possible reuse are not reasons.

7) Run one blocker-only review. Ask only:

**Is this variant safe and valid enough to produce the intended learning?**

A finding is allowed only when it makes execution unsafe, blocks a declared scenario,
invalidates comparison/evidence/identity, crosses a protected boundary, or blocks the
next learning step. It must state the invalidated learning/boundary and minimum fix.
Non-blocking production-quality findings are prohibited. A second pass verifies only
reported blockers. Use only a reviewer actually available in the active harness; do
not infer a concrete model from a catalog or lockfile whose harness identity is absent
or does not match. Model selection is outside this Skill, while this review output
contract remains binding regardless of model.

8) Evaluate each variant as `keep | mutate | drop`; retain selected and rejected
knowledge, not a production-debt backlog for disposable code.

9) At the budget or decision point, hand off to `$research-synthesis`. A promotion
candidate must include selected Feature/Interaction/Quality/API Contracts, accepted
claim IDs and limits, rejected alternatives, open uncertainties, code disposition,
`promotion_strategy: rebuild-from-contract`, and
`prototype_source_authority: non-authoritative`. Prototype runtime code must not enter
delivery by copy, move, rename, import, or incremental cleanup.

Open `references/variant-exploration.md` when preparing or executing a cycle,
performing its blocker-only review, or producing its Productization Brief.

## Hard rules

- Rapid narrows objective and review scope; it never weakens protected boundaries.
- No empirical claim without an experiment/claim ID.
- Do not vary controlled substrate silently.
- Do not treat exploration source as authoritative production source.
- Stop when the decision is unlocked.

## Output expectation

Use `templates/exploration-cycle.md`, normally at
`research/explorations/<cycle-id>/cycle.md`, to record the receipt, boundaries,
protocol, variants, review, observations/evidence, decisions, synthesis handoff, and
Productization Brief when promotion is recommended.
