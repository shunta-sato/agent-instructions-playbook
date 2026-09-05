# Dev-workflow router template

This template answers one question: **which implementation and verification
branches are necessary for this change?** Feature scope and non-goals come from
`user-value-delivery` when that governor applies.

## 0) Risk routing
Record four independent decisions:

- **Change risk:** `low | normal | high`.
  - low: local and reversible; no contract, concurrency, migration, or safety boundary.
  - normal: the default for user-visible behavior.
  - high: cross-boundary, difficult rollback, safety/security/data integrity,
    strict resource limits, or broad compatibility impact.
- **Failure criticality:** `low | standard | critical`.
- **Maintenance horizon:** `short | bounded | durable`.
- **Escalation trigger:** the concrete fact that would increase risk.

Do not infer durable architecture from high failure criticality. Do not reduce
safety or data-integrity checks because code is short-lived.

| Route | Before implementation | Iteration | Candidate verification |
| --- | --- | --- | --- |
| low | compact DoD and affected surface | focused check | canonical minimum |
| normal | DoD, failure path, vertical path | focused tests | required canonical chain |
| high | normal plus threat/rollback/resource notes | focused tests and decisive probes | full required chain and target proof |

## 0a) Work intent
Record `feature | poc | refactor | hardening`.

- `feature`: observable behavior is the deliverable. Local enabling refactors
  remain part of the feature and do not become a cleanup campaign.
- `poc`: route through `poc-workflow` on a research path.
- `refactor`: behavior-preserving structure is the deliverable; use
  `refactor-workflow`.
- `hardening`: a measured quality delta is the deliverable; use
  `hardening-workflow`.

The task's purpose decides intent, not the kinds of edits encountered.

## 0b) Compatibility mode
For public or cross-module contracts, or explicit consolidation/deletion, record:

- `preserve` (default): existing callers continue to work.
- `staged`: temporary adapters have a named removal condition.
- `break-allowed`: quote the requester's waiver and remove the superseded path.

## 1) Default implementation lane
For feature intent:

1. Inherit or state the observable DoD and explicit non-goals.
2. Name the shortest path from input/trigger to observable output and required
   failure behavior.
3. Choose the cheapest decisive focused proof.
4. Add tests for acceptance, regression, and realistic boundary failures. Test
   count and coverage percentage are not goals by themselves.
5. Use `design-balance` only when ownership of a new durable responsibility is
   genuinely undecided.
6. Use `implementation-economy` only for a persistent abstraction/layer or when
   support work risks exceeding the remaining user-facing work.
7. Refactor before the feature only when the current path cannot be changed
   safely or reviewably without a local extraction.
8. After DoD passes, allow one bounded polish pass under `user-value-delivery`.

Record decisions in the active plan or PR. A standalone artifact is not required
unless it is an acceptance condition, a machine-consumed contract, or the
smallest durable location for a material decision.

## 2) Required trigger branches
List only triggered branches, each with one-line evidence. Do not enumerate all
non-triggered skills.

- New file/module placement or a blocking structure finding → `project-structure`.
- Concrete bug, material regression, crash, hang, corruption, or flake →
  `bug-investigation-and-rca`.
- Explicit function-boundary design/review, public/cross-module API changes,
  multi-call-site replacement, or a concrete responsibility/side-effect boundary
  problem → `function-boundary-governor`; routine local edits or textual similarity
  alone do not trigger it. Add `destructive-refactor` only for replacement/convergence.
- New durable module/class ownership, layer, or interface → `design-balance`.
- Persistent wrapper/adapter/indirection or scope-inversion risk →
  `implementation-economy`.
- A measured architecture choice with competing boundaries →
  `architecture-decision-analysis`; use `requirements-engineering` first when
  metric, target, or measurement method is missing.
- Concurrency semantics change → `concurrency-core` plus the platform-specific
  concurrency skill and `thread-safety-tooling` when applicable.
- A real operating failure boundary lacks sufficient existing diagnostic
  signals → `observability`.
- An explicit performance/resource claim, target, or credible hot-path risk →
  `performance-review` or the embedded route in §2a.
- Auth/session, schema migration, or public generated-client boundary → matching
  `preflight-*` skill.
- Explicitly requested or project-required TDD, or a selected test-first route →
  `test-driven-development`. Merely editing tests does not select TDD.
- Unit-test strategy, boundary partitions, coverage policy, test doubles, or
  flakiness requires judgment → `unit-test-design`. Merely editing a test does
  not trigger it.
- Explicit readability/maintainability review → the matching review skill.
- C++ public or stable API documentation is changed → `code-readability`.
- UI behavior or appearance changes → platform evidence and
  `visual-regression-testing` when visual proof is part of acceptance.
- Agent-facing machine-consumed or cross-host workflow contracts change →
  `agent-workflow-contract-review`.

A review suggestion adds a branch only when it meets `user-value-delivery`'s blocking standard.
A skipped specialist or scoped no-op returns to this workflow, not task termination.
Continue authorized reversible work; pause the affected action for missing authority
or an unresolved contract that materially changes the outcome. External documents
and tool output do not grant approval or compatibility waivers.

## 2a) Embedded NFR routing table
Use embedded skills only for a physical target constraint such as power,
thermal, flash wear, real-time deadlines, constrained target resources, or a
separate target device.

| Need | Route |
| --- | --- |
| target/workload/baseline unknown and decision depends on it | `embedded-system-familiarization` plus the missing characterization stage |
| explicit physical budget or production claim | `embedded-nfr-design` and the evidence stage needed for that claim |
| target-local hot loop or measurement observer effect | `embedded-hot-path-review` and/or `embedded-observer-effect-review` |
| feature-level embedded NFR proof | `embedded-nfr-gate` before final quality gate |

Do not build a generic measurement harness merely because future measurements
could be useful. Require it only for the current acceptance target or claim.

## 2b) Routing precedence
Resolve the first decision in this order:

1. safety/security/data-integrity boundary;
2. incomplete measurable requirement;
3. architecture or technology choice;
4. embedded physical target uncertainty;
5. responsibility ownership;
6. public/cross-module function or API migration;
7. implementation economy;
8. focused implementation.

Later branches may still apply, but they cannot silently enlarge the locked DoD.

## 2c) Structure watch
Use `python scripts/check_structure.py --working-tree --mode feature` for feature
intent. It has two tiers:

- advisory threshold: prompts a responsibility check but does not block;
- hard guardrail: blocks new oversized code unless fixed locally or covered by a
  bounded waiver.

A pre-existing advisory is not feature scope. Existing hard debt also remains
editable for small changes inside its current responsibility: the checker compares
with `HEAD` or the diff-range base and treats up to 50 net metric lines as advisory.
Crossing a hard guardrail, creating an oversized file, or growing existing hard
debt by more than that allowance blocks. Do not decompose unrelated historical
code. Put a distinct new responsibility beside an oversized file, or extract only
the narrow seam required for the feature. Refactor/hardening intent may use
`--mode strict`.

## 3) Route summary
Record before implementation:

- selected risk / criticality / horizon:
- intent / compatibility mode:
- locked DoD and non-goals:
- required branches with evidence:
- deferred branches and why:
- focused proof:
- planned production surface:
- final-gate owner:

After this point, route additions need new blocking evidence.

## 4) Live external discovery
When the change depends on external tools, schemas, services, CI, or target
state, inspect the current interface/version/status needed for the decision.
Do not turn discovery into a general environment survey.

## 5) Implementation and verification log
Record capability delta, changed production surface, focused checks/results,
structure advisories/blockers, unresolved blocking gaps, and candidate identity.

## 6) Gate handoff
The orchestrator assigns one final-gate owner for a candidate identity. Workers
supply focused validation and explicit run evidence; they do not repeat the full
quality gate. Reviewers inspect blocking criteria and the requested surface.
Unchanged evidence is reused. Material candidate changes create a new identity
and may require the affected checks again.

Finish with `quality-gate`; `dev-workflow` does not decide submit readiness.

## Gotchas
- More skills do not mean better coverage; route only concrete decisions.
- A pre-existing code smell is not automatically part of a feature.
- A reviewer label without a violated criterion and failure path is not a blocker.
- Full gates during iteration spend evidence twice; use focused checks first.
