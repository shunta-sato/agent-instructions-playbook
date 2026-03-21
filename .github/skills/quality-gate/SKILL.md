---
name: quality-gate
description: "MANDATORY final gate before submission: validate exit criteria (checks, required artifacts, and required branch evidence) and return submit/no-submit with findings."
metadata:
  short-description: Final quality gate
---

## Purpose

Use this skill as the final submit gate.

It answers one question: **is this change ready to submit now?**

## When to use

Invoke this skill **before every submission**. It is mandatory.

## How to use

0) Open `references/quality-gate.md` and run the checklist.

1) Verify canonical commands are green at the required depth (build / format / static analysis / tests).
   - If something cannot run, record reason + reproducible procedure.

2) Validate required artifacts/evidence from triggered branches exist.
   - Examples: Bug Report, UI Visual Verification Report, staged-lowering log, concurrency verification evidence, ExecPlan updates.

3) Run concise exit-criteria review only.
   - Do not duplicate deep taxonomy here.
   - If a finding needs deep analysis, route to the dedicated skill (readability/modularity/boundaries/error-handling/etc.) and return after fixes.

4) Output `submit` or `no-submit` with findings.
   - `submit` is allowed only when checklist is fully satisfied and findings are 0.

## Gotchas

- **Common pitfall:** repeating deep-review taxonomy in quality-gate and making it verbose.  
  **Instead:** limit gate to exit-criteria decisions and delegate deep dives to dedicated skills.
- **Common pitfall:** approving as mostly OK while required artifacts are missing.  
  **Instead:** keep `no-submit` until required evidence for triggered branches is complete.
- **Common pitfall:** marking `submit` with vague records of unrun commands.  
  **Instead:** for unrun commands, always record reason + reproduction steps and reflect that in submission decision.

## Output expectation

- Start with: `Gate decision: submit` or `Gate decision: no-submit`.
- If `no-submit`, list each finding with: location, missing/failed criterion, required fix.
- Only output `0 findings` when all exit criteria are satisfied.
