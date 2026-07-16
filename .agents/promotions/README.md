# Promotion acknowledgments

An acknowledgment is the committed record of a research→delivery crossing. Add one `*.md` file here (any name but `README.md`) in the **same diff** that promotes research into a delivery path.

## Required format

To count as valid, the file must contain:

1. A line beginning `Scope:` (case-insensitive) — a one-line description of the crossing.
2. A claim reference matching `C-\d+` (e.g. `C-0002`) for each promoted research claim, **or** the literal phrase `no research claims promoted` when the diff is infrastructure-only.
3. A `Covers:` section: a line beginning `Covers:` followed by one or more `- <path-prefix>` lines naming every delivery-path prefix this acknowledgment covers.
4. One or more `Delivery-run:` lines (R4), each citing the `run_id` of an `agent_run` record in the canonical ledger (`.agents/runs/agent-runs.jsonl`) that produced or reviewed the promoted work. A cited run counts as evidence only when it recorded **passing validation commands** (`validation.commands` non-empty, all exit 0) **and** an explicit **`quality_gate` of `pass` or `submit`** **and** its own outcome re-derives as **accepted** (`agent_run.evaluate_run_record` — `agent_completed: true` and every `changed_files` entry within the run's own `allowed_files`) — a caller-written `validation.passed`/`outcome.validation_passed`/`outcome.accepted` boolean is not sufficient on its own.

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
- Every cited `Delivery-run:` `run_id` must resolve to an `agent_run` record with passing validation commands, a recorded quality-gate pass, and its own re-derived acceptance (see requirement 4).
- A `promotion-required` path is downgraded to a non-blocking `NOTE promotion acknowledged:` line only when it is **both** under one of the acknowledgment's `Covers:` prefixes **and** spanned by a **digest-verified `reviewed_files`** entry naming that exact path. Neither `changed_files` (a listed path carries no content guarantee against a *later* edit of the same path) nor `allowed_files` (authorization scope, not evidence) ever covers a promoted path on their own. A delivery path not spanned this way stays blocking.
- `reviewed_files` entries carry a `path` and the `sha256` the recorder computed at record time (via `agent_run record --reviewed-file PATH`, or `--review-changed` to also add every `--changed-file` path). Before a reviewed entry covers a path, the gate re-hashes the blob at the diff head (or the working-tree file) and compares; a drifted digest covers nothing and prints `NOTE stale-review: <path>`.

An invalid acknowledgment — missing any required element, or citing an unresolved claim, an unknown run, a run without passing validation commands, a run without a recorded quality-gate pass, or a run whose own outcome does not re-derive as accepted — downgrades **nothing**: the gate prints `NOTE invalid-acknowledgment: <file> (<reason>)` and every `promotion-required` finding stays blocking. Acknowledgment files under `.agents/promotions/` and the run ledger `.agents/runs/agent-runs.jsonl` are the promotion/recording **mechanism**, not promoted content, so they are never themselves `promotion-required` (they need no self-coverage). `safety-review-required` is **never** downgraded, by any acknowledgment.

## Deletions

A DELETED delivery path has no head blob to digest, so it needs a different evidence shape: record it with `agent_run record --reviewed-deleted PATH` *before* the deleting commit — the script hashes the path's blob at current HEAD and stores a tombstone (`deleted: true`, `base_sha256`). The gate covers a deletion only when a cited run's tombstone `base_sha256` matches the blob at the diff's **BASE** ref; a normal (non-tombstone) `reviewed_files` entry never covers a deletion, and a tombstone never covers a live file. A tombstone digest mismatch prints `NOTE stale-tombstone: <path>` instead of `stale-review`.

## Scope and honest limitation

This gate verifies **consistency with recorded evidence**, not authorship. The acknowledgment file itself is agent-writable, and the run records it cites live on the same agent-writable JSONL ledger (see the tamper-EVIDENT-not-tamper-PROOF threat model in `scripts/research_ledger.py`). A determined agent with write access could fabricate a self-consistent acknowledgment together with matching run records. Adversarial-grade protection — a protected/attested writer for run records and external anchoring of the ledger head — remains the documented follow-up; until then, treat a green promotion gate as evidence that the crossing is consistent with the recorded runs, not as proof of who produced them.

A run's `validation.commands` strings and a recorded `quality_gate: pass`/`submit` are **corroborating self-reports** written by the same caller that recorded the run — not proof that anything was actually executed. The one piece of evidence in this chain that IS executed, independently of the agent, is the CI workflow itself running at the reviewed head: `.github/workflows/agent-index.yml` runs every other validator step before the `--diff-range` boundary gate (asserted by test), so the boundary gate's own pass/fail is the closest thing to ground truth here. A trusted execute-and-record wrapper — one that runs validation commands itself rather than trusting a caller-supplied exit code — remains the documented follow-up for the self-report gap.
