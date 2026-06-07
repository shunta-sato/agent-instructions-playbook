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

2) Validate required artifacts/evidence from triggered branches exist, including function-design evidence when triggered.
   - Examples: Bug Report, UI Visual Verification Report, staged-lowering log, concurrency verification evidence, ExecPlan updates.
   - If `architecture-decision-analysis` was triggered, verify an Architecture Decision Analysis Record exists and includes decision, quality drivers, tradeoffs, and verification tasks.
   - If `observability` was triggered, verify the Observability Plan includes signal purpose, actionability, counter-metric where relevant, and artifact paths.
   - If feature-level embedded NFR work was triggered, verify `reports/resource/nfr-gate-report.md` exists and records `submit`, `no-submit`, or `experimental-only`; accept submit only when the embedded NFR gate is `submit` or the feature is explicitly experimental with production claims removed.
   - If production-ready, low-overhead, battery-safe, flash-safe, thermally-safe, or always-on claims depend on embedded NFRs, verify target characterization exists or the claim is explicitly provisional, budget provenance exists, calibration report exists when numeric budgets are claimed, calibration revisit conditions are not triggered, and the NFR gate report references these artifacts.
   - If only `embedded-project-constitution` was triggered, verify constitution artifacts exist. Do not require a feature-level NFR gate report unless feature runtime changes or production-readiness claims are introduced.
   - If any study-note workflow was triggered, verify the relevant Study Pack Report exists.
   - If publish/sync readiness was required, verify `textbook-quality-gate` produced a gate decision.
   - If narrative or technical essay workflow was used, verify its semantic review report exists before accepting shared-mechanical-only checks.

3) Run concise exit-criteria review only.
   - Do not duplicate deep taxonomy here.
   - If a finding needs deep analysis, route to the dedicated skill (readability/maintainability/error-handling/etc.) and return after fixes.

4) Output `submit` or `no-submit` with findings.
   - `submit` is allowed only when checklist is fully satisfied and findings are 0.



Function-design evidence requirements when triggered:
- function-boundary-governor → function decision record (`keep|rename|split|merge|replace|inline|no-op`) + rationale
- destructive-refactor → convergence record (`replaced|no-op|rollback`), call-site migration evidence, and red-state usage record
- when no-op or rollback is chosen → explicit reasoning
- ledger-required cases (replaced abstractions, intentional duplication, staged adapters) → ledger entry present at `.agents/design-ledger/function-boundaries.md`

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


- Verify ledger by checking canonical path `.agents/design-ledger/function-boundaries.md`, not only final-response text.
- Verify embedded NFR evidence by checking the report artifact path, not only final-response text.
- Verify constitution-only evidence by checking the generated project artifacts, not only final-response text.
