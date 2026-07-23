# Routing eval runs

Model-executable routing measurement built on `scripts/run_routing_eval.py`
over the corpus under `evals/skill-triggers/`. The harness never calls a
model itself.

## Protocol

1. **Build**: `python3 scripts/run_routing_eval.py build --repo-root <checkout> --out <packs-dir>`
   Emits self-contained `batch-NN.md` prompt packs (case id + prompt only,
   no expectations) plus `manifest.json`.
2. **Run**: hand each `<packs-dir>/batch-NN.md` to the target model runner
   (Claude Code subagent, Codex CLI, an API script, ...) without ever
   showing it `evals/skill-triggers/*.json`. Save the runner's raw JSON
   array reply as `<responses-dir>/batch-NN.json`.
3. **Grade**: `python3 scripts/run_routing_eval.py grade --packs <packs-dir> --responses <responses-dir> --out <result>.json --repo-root <checkout>`
   Grades against the corpus read fresh from `<checkout>`, never from the
   packs.
4. **Report**: `python3 scripts/run_routing_eval.py report --graded <fileA.json> [<fileB.json>] --format md`
   Prints a deterministic markdown comparison.

## Results-file naming

Save each graded result under this directory as:

    <date>-<variant>-<model>.json

e.g. `20260723-wt-wsb-claude-sonnet-5.json`. `<variant>` is the checkout
label from the graded file's `variant` field; `<model>` is whichever
runner/model answered the packs.

## Runner-agnostic by design

The harness measures whatever model answered the packs. A Codex CLI or GPT
run over the same `batch-NN.md` files grades identically to a Claude Code
subagent run: packs carry no Claude-specific instructions, and grading
never inspects which runner produced the response.
