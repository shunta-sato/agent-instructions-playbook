---
name: research-workflow
description: "Use when the task's epistemic mode is research: exploratory optimization, feasibility probes, model/architecture exploration, benchmark investigation, or proof-of-concept work where learning per unit cost matters more than shipping. Routes probes to experiment-loop and synthesis to research-synthesis. Do not use in delivery mode, or once findings are being promoted into a delivery path (dev-workflow, quality-gate)."
metadata:
  short-description: Research-mode router
  requires:
    - references/research-framing.md
---

## Purpose

This skill is the research-mode peer of `dev-workflow`. It routes exploratory, evidence-gathering work the way `dev-workflow` routes delivery work.

Its goal is to maximize learning per unit cost. Unknowns are assets to reduce, not blockers to clear before starting. Termination is one of `continue | pivot | kill | promote` — never `submit`/`no-submit`; that vocabulary belongs to `quality-gate` and only applies once work is promoted into a delivery path.

## When to use

Use this skill when the task's mode is `research`: exploratory optimization, feasibility probes, model/architecture exploration, benchmark investigation, or proof-of-concept work. Mode is resolved by explicit declaration > `.agents/project-policy.yml` `path_modes` > the policy's `default_mode`.

Do not use it for delivery-mode work; that stays on `dev-workflow` + `quality-gate`. Do not use it once a research result is being promoted into a delivery path — promotion re-enters `dev-workflow` and `quality-gate` in full, even though the finding originated here.

## How to use

0) Confirm the recorded mode is `research` (see When to use). If mode is `delivery`, stop and route to `dev-workflow` instead.

1) Write the 4-line frame before probing:
   - `mode`
   - `question`
   - `decision` (what this unlocks)
   - `next_probe`

2) Select the next probe with this ordinal decision tree, in order:
   1. If a probe under one hour can falsify at least one live hypothesis, do it first.
   2. If re-analysis of existing artifacts can falsify without new implementation, that outranks everything.
   3. Deprioritize experiments whose result is predicted identically by every live hypothesis.
   4. Never run an experiment whose outcome changes no next decision.
   5. For multi-day experiments, first seek a small proxy or upper-bound probe.
   6. For physically risky experiments, first check simulation/replay/HIL substitutes.

3) Any evidence-bearing experiment goes through `$experiment-loop`. Unregistered exploration is allowed for reconnaissance but is never citable as evidence until it is re-registered through `$experiment-loop` with a fresh confirmation.

4) Periodically, or whenever more than 5 results remain unsynthesized, hand this cycle's results to `$research-synthesis`.

5) Code-quality gates (`dev-workflow`, `quality-gate`) are waived for probe code under research-mode paths — disposable implementation is expected. Evidence discipline is **not** waived: every empirical claim still needs a registered experiment. Physical-safety, secrets, and destructive-operation rules never waive, in any mode.

## Hard rules

- No empirical claim without a registered experiment ID. This rule is mode-independent — it attaches to the claim, not to the mode the claim was made in — and is mechanically checked by `scripts/check_research_evidence.py`.
- Disposable code is acceptable; disposable knowledge is not. A probe's script can be thrown away; what was learned or falsified must reach `$research-synthesis`.
- Touching a delivery-mode path from research work triggers promotion: `dev-workflow` and `quality-gate` apply to that path from that point on.

## Output expectation

- The 4-line frame (`mode` / `question` / `decision` / `next_probe`).
- Current live hypotheses, in plain language.
- Probes executed this cycle, each with its experiment ID or exploration ID.
- Handoffs made this cycle (to `$experiment-loop`, `$research-synthesis`, or a promotion into delivery gates), or `none`.
