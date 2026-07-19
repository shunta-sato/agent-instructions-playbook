---
name: poc-workflow
description: "Use for PoC, prototype, demo, or feasibility-spike construction answering one question with the cheapest artifact, on the research-mode substrate (a poc/ path or explicitly declared research task). Frames the question, exit criteria, and rigor floor first; ends in discard, promotion, or a citable-evidence handoff. Do not use for delivery feature work (dev-workflow) or registered experiments (experiment-loop)."
metadata:
  short-description: PoC construction on the research substrate
  requires:
    - references/poc-workflow.md
---

## Purpose

PoC construction is research-mode work, not a fourth mode and not a delivery shortcut. This skill makes that concrete: it owns the CONSTRUCTION activity of building a demo, prototype, or feasibility artifact, with a rigor floor low enough that disposable code stays disposable and high enough that nothing unsafe ships.

## When to use

Use this skill when the task is to build a demo, prototype, or feasibility spike to answer one question cheaply. It applies only inside the research-mode boundary:

- the target path resolves to `research` under `.agents/project-policy.yml` `path_modes` (this repo maps `poc/`), or
- the task explicitly declares mode `research`.

A PoC built on a delivery path in delivery mode gets **no** exemptions — `$dev-workflow` applies in full. Do not use this skill for delivery feature work or for a registered evidence-bearing probe (that is `$experiment-loop`).

## Boundaries

- `$research-workflow` owns mode routing and evidence-loop dispatch.
- `$experiment-loop` owns registered probes (hypothesis + disconfirm predicate + command).
- `poc-workflow` owns CONSTRUCTION only: building the demo/feasibility artifact itself.
- Promotion re-enters `$dev-workflow` as intent `feature` on the promoted diff, in full.

## How to use

0) Confirm the entry precondition above and record the RECEIPT before any exemption is claimed: the resolved mode for the target paths (from `.agents/project-policy.yml` or the explicit declaration) plus the output of `python3 scripts/check_research_evidence.py --working-tree --policy .agents/project-policy.yml --mode research`. No receipt, no rigor floor. If neither precondition holds, stop and route to `$dev-workflow` — do not proceed under a relaxed rigor floor.

1) Open `references/poc-workflow.md` and record, before writing any code: the QUESTION the PoC answers, the cheapest artifact that answers it, and the exit criteria that ends the PoC.

2) Build to the rigor floor only (always on, never relaxed): it runs; one smoke-level check proves the demo path works; the safety overlay (secrets handling, destructive-operation rules, physical-safety rules) applies as in every mode; structure-budget violations are tolerated but noted, not fixed.

3) Acknowledge the OFF list explicitly (full table in the reference file): `$unit-test-design` case-depth tiers (smoke only), `$test-driven-development`, `$observability` plans, `$implementation-economy` budgets, requirements/NFR machinery, and the `$quality-gate` delivery profile — the research working-tree gate applies instead: `python3 scripts/check_research_evidence.py --working-tree --policy .agents/project-policy.yml --mode research`.

4) Stop the moment the recorded QUESTION is answered. Continuing to build after the answer is known is feature creep wearing a PoC label.

5) Close with exactly one exit (decision table in the reference file):
   - **discard** — record the answer and the discard;
   - **promote** — re-enter `$dev-workflow` as `feature` intent on the promoted diff; the mechanical boundary gate fail-closes silent promotion, and a promotion acknowledgment under `.agents/promotions/` rides in the same diff; PoC code is never shipped by renaming or moving it;
   - **evidence** — route the observation to `$experiment-loop`, which registers a FRESH confirmation on a new variation axis; the PoC's own already-executed run is never cited directly (post-hoc registration fails the ledger gate).

## Output expectation

- The mode receipt: resolved research mode for the target paths + the research working-tree gate output.
- The recorded question, cheapest artifact, and exit criteria.
- Rigor-floor results: it runs, the smoke-level check, and the safety-overlay check.
- The OFF list, explicitly acknowledged as skipped.
- The chosen exit (discard | promote | evidence) with its evidence: the discard record, the promotion routing + acknowledgment reference, or the `$experiment-loop` registration ID.
