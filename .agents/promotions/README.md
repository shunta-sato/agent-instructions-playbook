# Promotion acknowledgments

An acknowledgment is the committed record of a research→delivery crossing. Add one `*.md` file here (any name but `README.md`) in the **same diff** that promotes research into a delivery path.

## Required format

To count as valid, the file must contain:

1. A line beginning `Scope:` (case-insensitive) — a one-line description of the crossing.
2. A claim reference matching `C-\d+` (e.g. `C-0002`) for each promoted research claim, **or** the literal phrase `no research claims promoted` when the diff is infrastructure-only.
3. A `Covers:` section: a line beginning `Covers:` followed by one or more `- <path-prefix>` lines naming every delivery-path prefix this acknowledgment covers.
4. One or more `Delivery-run:` lines (R4), each citing the `run_id` of an `agent_run` record in the canonical ledger (`.agents/runs/agent-runs.jsonl`) that produced the promoted work.

Example:

```
Scope: land the Research OS v0 delivery surface
no research claims promoted
Delivery-run: 20260712T151808Z-focused_code_change-641da0ad
Covers:
- scripts/
- tests/
- .agents/
```

## What the gate does with it

`scripts/check_research_evidence.py --diff-range` / `--working-tree` parses every acknowledgment file in the changed-path set and **binds it to recorded ledger evidence** (R4), not just to its own syntax:

- Every cited `C-\d+` claim must resolve to a `research_claim` record that passes re-derivation in the canonical ledger.
- Every cited `Delivery-run:` `run_id` must resolve to an `agent_run` record whose validation passed (`validation.passed` / `outcome.validation_passed`).
- A `promotion-required` path is downgraded to a non-blocking `NOTE promotion acknowledged:` line only when it is **both** under one of the acknowledgment's `Covers:` prefixes **and** contained in the union of the cited runs' `changed_files` ∪ `allowed_files` (a listed directory covers its subtree). A delivery path not spanned by that union stays blocking.

An invalid acknowledgment — missing any required element, or citing an unresolved claim, an unknown run, or a run that did not pass validation — downgrades **nothing**: the gate prints `NOTE invalid-acknowledgment: <file> (<reason>)` and every `promotion-required` finding stays blocking. This includes the acknowledgment file's own path — list `.agents/promotions/` (or `.agents/`) in `Covers:` and make sure a cited run's files span it. `safety-review-required` is **never** downgraded, by any acknowledgment.

## Scope and honest limitation

This gate verifies **consistency with recorded evidence**, not authorship. The acknowledgment file itself is agent-writable, and the run records it cites live on the same agent-writable JSONL ledger (see the tamper-EVIDENT-not-tamper-PROOF threat model in `scripts/research_ledger.py`). A determined agent with write access could fabricate a self-consistent acknowledgment together with matching run records. Adversarial-grade protection — a protected/attested writer for run records and external anchoring of the ledger head — remains the documented follow-up; until then, treat a green promotion gate as evidence that the crossing is consistent with the recorded runs, not as proof of who produced them.
