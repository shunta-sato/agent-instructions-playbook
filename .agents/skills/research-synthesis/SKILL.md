---
name: research-synthesis
description: "Use when more than five experiment results have accumulated without synthesis, at a research decision point, or before promoting a research finding into a delivery path. Reads the experiment ledger for knowledge deltas — supported, falsified, still-open — to decide continue, pivot, kill, or promote. Do not use for per-experiment interpretation (experiment-loop) or delivery-mode planning (execution-plans)."
metadata:
  short-description: Research decision synthesis
---

## Purpose

This skill turns a pile of individually-interpreted experiments into one decision. `$experiment-loop` produces per-experiment interpretation; this skill is where those interpretations get compared, pruned, and resolved into a direction.

## When to use

Use this skill when any of these apply:

- more than 5 experiment results have accumulated since the last synthesis
- the cycle has reached a research decision point (the live hypotheses no longer agree on what to probe next)
- before any promotion of a research finding into a delivery path

## How to use

1) Read the ledger: registered experiments, their outcomes, and existing claims.

2) State the knowledge deltas since the last synthesis:
   - **supported** — hypotheses the evidence backs.
   - **falsified** — hypotheses the evidence rules out. Negative results are first-class outcomes here, not noise to omit.
   - **still-open** — questions no registered experiment has settled yet.

3) Prune dead exploration directions — lines of probing the evidence has already closed off — so the next cycle's probe selection isn't wasted re-deriving what this synthesis already knows.

4) Decide exactly one of: `continue | pivot | kill | promote`, with rationale tied to the knowledge deltas above.

5) On `promote`:
   - Verify claims first: `python3 scripts/check_research_evidence.py --check-ledger`.
   - The promotion package must include a committed acknowledgment file under `.agents/promotions/` (see `.agents/promotions/README.md` for the required format: a `Scope:` line, claim IDs or `no research claims promoted`, and a `Covers:` path-prefix list — only covered findings downgrade) riding in the same diff as the promoted paths.
   - Hand off to the delivery gates — `$dev-workflow` (risk routing + compat-mode) and `$quality-gate` — for re-implementation or hardening of the promoted candidate. Research code does not walk into a `runtime/` path unreviewed; the delivery gates own that path from here.

## Output expectation

- Decision: exactly one of `continue | pivot | kill | promote`.
- Knowledge state summary: supported, falsified (including negative results), and still-open, each tied to experiment IDs.
- Claims cited by `claim_id`.
- When the decision is `promote`: the promotion package boundary — what gets re-implemented for delivery vs. what gets discarded as disposable probe code.
