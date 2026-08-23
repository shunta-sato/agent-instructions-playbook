---
name: research-synthesis
description: "Use when more than five experiment results await synthesis, at a research decision point, after an executable variant-comparison cycle, or before promotion to delivery. Compares ledger evidence and exploration records to decide continue, pivot, kill, or promote. Do not use for per-experiment interpretation (experiment-loop) or delivery planning (execution-plans)."
metadata:
  short-description: Research decision synthesis
---

## Purpose

This skill turns a pile of individually-interpreted experiments or a completed executable-variant cycle into one decision. `$experiment-loop` produces per-experiment interpretation; `$variant-exploration` produces comparative behavior and a convergence package; this skill is where those results get compared, pruned, and resolved into a direction.

## When to use

Use this skill when any of these apply:

- more than 5 experiment results have accumulated since the last synthesis
- the cycle has reached a research decision point (the live hypotheses no longer agree on what to probe next)
- a `$variant-exploration` cycle reached its budget or recorded synthesis point
- before any promotion of a research finding into a delivery path

## How to use

1) Read the ledger: registered experiments, their outcomes, existing claims, and any Exploration Cycle Record.

2) State the knowledge deltas since the last synthesis:
   - **supported** — hypotheses the evidence backs.
   - **falsified** — hypotheses the evidence rules out. Negative results are first-class outcomes here, not noise to omit.
   - **still-open** — questions no registered experiment or bounded exploration protocol has settled yet.
   - **retained product knowledge** — selected and rejected variant behavior, with observation/evidence limits kept explicit.

3) Prune dead exploration directions — lines of probing or variants the evidence has already closed off — so the next cycle's probe selection isn't wasted re-deriving what this synthesis already knows.

4) Decide exactly one of: `continue | pivot | kill | promote`, with rationale tied to the knowledge deltas above.

5) On `promote`:
   - Verify claims first: `python3 scripts/check_research_evidence.py --check-ledger`.
   - When promotion follows `$variant-exploration`, require a Productization Brief with selected Feature/Interaction/Quality/API Contracts, rejected alternatives, accepted claim IDs and limits, open uncertainties, exploration-code disposition, `promotion_strategy: rebuild-from-contract`, and `prototype_source_authority: non-authoritative`.
   - The promotion package must include a committed acknowledgment file under `.agents/promotions/` (see `.agents/promotions/README.md` for the required format: a `Scope:` line, claim IDs or `no research claims promoted`, a `Covers:` path-prefix list, and `Delivery-run:` lines citing run records with passing validation commands and a recorded quality-gate pass, whose digest- and mode-verified `reviewed_files` entries — including tombstoned deletions — cover the promoted paths; permission scope and changed-file lists are never evidence, and only covered, evidence-backed findings downgrade) riding in the same diff as the promoted paths.
   - Hand off to the delivery gates — `$dev-workflow` (risk routing + compat-mode) and `$quality-gate` — for a new feature implementation from the confirmed contracts. Research code does not walk into a delivery path by copy, move, rename, import, or incremental cleanup; the delivery gates own that path from here.

## Adjacent-skill handoff

Hand off to `$failure-retrospective` only when repeated not-evaluable
results accumulate, the experiment/evaluation harness itself has a defect, the same
wrong probe or variant keeps getting selected, exploration review repeatedly escapes
its blocker-only scope, or a promotion-boundary/evidence-integrity failure occurs —
not for an ordinary expected-disconfirmed experiment or dropped variant, which stays
inside this skill / `$experiment-loop` / `$variant-exploration`.

## Output expectation

- Decision: exactly one of `continue | pivot | kill | promote`.
- Knowledge state summary: supported, falsified (including negative results), still-open, and retained product knowledge, each tied to experiment/claim/variant IDs and its evidence limit.
- Claims cited by `claim_id`.
- When the decision is `promote`: the Productization Brief and promotion package boundary — what is re-implemented from contracts, what non-runtime artifacts may be reused, and what is discarded as disposable exploration code.
