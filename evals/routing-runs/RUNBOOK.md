# RUNBOOK: cross-model routing eval (GPT-class / Codex runner)

Run the identical routing measurement used for the Sonnet baseline with a
non-Claude runner. See `evals/routing-runs/README.md` for the harness
protocol this runbook instantiates; the harness never calls a model itself.

## 1. Build packs at a fixed commit

Build from a clean checkout at the exact commit under test — not a dirty
working tree — so the `commit` recorded in the graded output is trustworthy:

    git worktree add /tmp/routing-checkout <commit-ish>
    cd /tmp/routing-checkout && git rev-parse HEAD   # record this hash

    python3 scripts/run_routing_eval.py build \
      --repo-root /tmp/routing-checkout --out /tmp/routing-packs

This emits `batch-NN.md` prompt packs (case id + prompt only, no
expectations) plus `manifest.json` under `/tmp/routing-packs`.

## 2. The canonical subject instruction (verbatim)

Give each batch to the subject model with exactly this text — this same
instruction was used for every Claude subject; cross-model comparability
requires it unchanged:

```
Read the file <pack>/batch-NN.md and follow its response instruction exactly for
every case in it. Write ONLY the resulting JSON array (no prose, no markdown
fences) to <responses>/batch-NN.json. Do not read any other file. Do not explore
any repository. Judge each case independently on its own facts.
```

Substitute the real pack path, responses directory, and batch number for
`<pack>`, `<responses>`, `NN`.

## 3. One fresh session per batch

Open a new, context-free model session per `batch-NN.md` — no shared context
and no prior batch's answers visible across batches. Save the raw reply
verbatim as `<responses-dir>/batch-NN.json`.

## 4. Grade and report

Grade against the SAME commit used to build the packs:

    python3 scripts/run_routing_eval.py grade \
      --packs /tmp/routing-packs --responses <responses-dir> \
      --out evals/routing-runs/<date>-<variant>-<model>.json \
      --repo-root /tmp/routing-checkout

Name the result `<date>-<variant>-<model>.json`, e.g.
`20260801-main-gpt-5.6.json`.

Compare against the Sonnet baseline recorded for that same commit (check its
`commit` field before comparing — do not diff across different commits):

    python3 scripts/run_routing_eval.py report \
      --graded evals/routing-runs/<sonnet-baseline>.json \
               evals/routing-runs/<date>-<variant>-<model>.json \
      --format md

## 5. Honesty rules

- Never show the subject model `evals/skill-triggers/*.json` expectations —
  packs already withhold them; do not reintroduce them via the runner prompt.
- If a batch response is missing, truncated, or not valid JSON, report it as
  ungraded/corrupt in the writeup — do not guess or backfill it.
- A single-run delta of a few points between models or variants is
  suggestive only; do not report it as a settled finding.
