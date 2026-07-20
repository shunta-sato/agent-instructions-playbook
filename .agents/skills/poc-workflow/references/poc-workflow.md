# PoC workflow reference

Checklist form of the construction contract. Fill top-down before building.

## 1) Entry preconditions (boundary check)

| Condition | Result |
| --- | --- |
| Target path matches `path_modes` as `research` (e.g. `poc/`) | Boundary satisfied — proceed. |
| Task explicitly declares mode `research` | Boundary satisfied — proceed. |
| Neither holds, even for a "quick PoC" | STOP. No exemption. Route to `$dev-workflow` in full; this skill does not apply. |

A PoC built on a delivery path in delivery mode gets **no** rigor discount. Do not relabel a delivery task as a PoC to skip gates.

## 2) Record before building (all three, before writing code)

- **QUESTION** — the one thing this PoC must answer, one sentence.
- **Cheapest artifact** — the smallest build that can answer the QUESTION (script, stub, mocked call, single screen — not a feature).
- **Exit criteria** — the observable result that ends the PoC (a number crossing a threshold, an API call succeeding once, a UI interaction completing).

If any of the three cannot be stated, the task is not ready to build; clarify first.

## 3) Rigor floor (always on, every PoC, no exceptions)

- It runs.
- One smoke-level check proving the demo path works end-to-end (not a case matrix — `$unit-test-design` depth is OFF, see below).
- Safety overlay: secrets handling, destructive-operation rules, physical-safety rules — these apply in every mode and are never waived by PoC status.
- Structure-budget violations (`scripts/check_structure.py`) are tolerated but must be noted in the report, not silently ignored.

## 4) Explicitly OFF for PoC construction

| Off | Why |
| --- | --- |
| `$unit-test-design` case-depth tiers | Smoke-level only; no E/S/H tiering. |
| `$test-driven-development` | No Red-Green-Refactor loop required. |
| `$observability` plans | No logging/metrics/tracing plan required. |
| `$implementation-economy` budgets | No abstraction-count audit. |
| Requirements/NFR machinery | No acceptance criteria doc, no NFR budgets. |
| `$quality-gate` delivery profile | Replaced by the research working-tree gate: `python3 scripts/check_research_evidence.py --working-tree --policy .agents/project-policy.yml --mode research`. |

State each OFF item as acknowledged in the report; do not silently add any of them back in.

## 5) Stop rule

The moment the recorded QUESTION is answered (exit criteria met, or definitively falsified), **stop building**. Adding more scope after the answer is known is the over-quality failure in miniature — a PoC that keeps growing is laundering feature work through a research-mode exemption.

## 6) Choose exactly one exit

| Exit | What it requires |
| --- | --- |
| **Discard** | Record the answer to the QUESTION and the discard decision. Delete or leave the PoC artifact in its research-mode path; it is never referenced as shipped code. |
| **Promote** | The promoted diff re-enters `$dev-workflow` with intent `feature` — full `$unit-test-design` tiers, `$observability`, structure budget. The mechanical boundary gate (`scripts/check_research_evidence.py`) fail-closes silent promotion of research-mode paths; the promotion acknowledgment under `.agents/promotions/` (see its `README.md`) is required in the same diff. PoC code is never shipped by renaming or moving the research-mode files — it is re-implemented under delivery gates. |
| **Evidence** | An observation worth citing (a number, a benchmark, a comparison) routes through `$experiment-loop` for registration; an unregistered PoC observation is never citable on its own. |

## Boundaries (restated)

- `$research-workflow` owns mode routing and evidence-loop dispatch.
- `$experiment-loop` owns registered probes.
- `poc-workflow` owns CONSTRUCTION only: building the demo/feasibility artifact itself.
