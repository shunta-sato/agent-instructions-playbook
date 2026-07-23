---
name: quality-gate
description: "Use before every delivery-mode submission to decide whether required checks, artifacts, and branch evidence are complete enough to submit."
metadata:
  short-description: Final quality gate
  requires:
    - references/quality-gate.md
---

## Purpose

Use this skill as the final submit gate.

It answers one question: **is this change ready to submit now?**

## When to use

Invoke this skill **before every delivery-mode submission**. It is mandatory in delivery mode. Research probes are gated by `scripts/check_research_evidence.py` instead; promotion into delivery paths re-enters this gate in full.

## How to use

0) Open `references/quality-gate.md` and run the checklist as one complete sweep — never stop at the first failed item: `references/quality-gate.md` §sweep rule.

1) Verify canonical commands are green at the required depth — full command-status checklist: `references/quality-gate.md` §1.

1b) Run the structural exit check: `python scripts/check_structure.py <touched source files>` — full rule (finding types, entrypoint scope, no-waiver-no-submit): `references/quality-gate.md` §1b.

1c) Run the boundary gate with the declared mode: `python3 scripts/check_research_evidence.py --working-tree --policy .agents/project-policy.yml --mode delivery` — `safety-review-required` findings are `no-submit` in every mode: `references/quality-gate.md` §3.

2) Validate required artifacts/evidence from every triggered branch — full per-branch evidence list: `references/quality-gate.md` §2.

3) Run concise exit-criteria review only; route anything needing deep analysis to its dedicated skill and return — full list: `references/quality-gate.md` §3.

4) Output `submit` or `no-submit` with findings — format and the zero-findings rule: `references/quality-gate.md` §4.

## Output expectation

- Start with: `Gate decision: submit` or `Gate decision: no-submit`.
- If `no-submit`, list each finding with: location, missing/failed criterion, required fix.
- Only output `0 findings` when all exit criteria are satisfied.
