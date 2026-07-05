---
name: quality-gate
description: "Use before every submission to decide whether required checks, artifacts, and branch evidence are complete enough to submit."
metadata:
  short-description: Final quality gate
  requires:
    - references/quality-gate.md
---

## Purpose

Use this skill as the final submit gate.

It answers one question: **is this change ready to submit now?**

## When to use

Invoke this skill **before every submission**. It is mandatory.

## How to use

0) Open `references/quality-gate.md` and run the checklist.
   - Sweep rule: evaluate **every** applicable item before deciding. Never stop at the first failed item — the Findings list must be the complete result of one full pass.

1) Verify canonical commands are green at the required depth (build / format / static analysis / tests).
   - If something cannot run, record reason + reproducible procedure.

1b) Run the structural exit check: `python scripts/check_structure.py <touched source files>`.
   - Any finding is `no-submit` until the split is applied in this submission, or an explicit bounded waiver (for example generated code) is recorded in the change brief.
   - This check is independent of which branches were triggered: a change that never triggered `design-balance` still fails here if a touched file breached the structure budget.

2) Validate required artifacts/evidence from triggered branches exist, including function-design evidence when triggered.
   - Examples: Bug Report, UI Visual Verification Report, staged-lowering log, concurrency verification evidence, ExecPlan updates.
   - If `project-structure` was triggered, verify the layout decisions (file → role) and the structure budget result are recorded.
   - If `architecture-decision-analysis` was triggered, verify an Architecture Decision Analysis Record exists and includes decision, quality drivers, tradeoffs, and verification tasks.
   - If `observability` was triggered, verify the Observability Plan includes signal purpose, actionability, counter-metric where relevant, and artifact paths.
   - If `implementation-economy` was triggered, verify the Complexity Budget and Post-Implementation Economy Audit exist.
   - If `design-balance` was triggered, verify the Responsibility Map exists and records names, responsibilities, reasons to change, and dependency direction.
   - If `performance-review` was triggered, verify the Performance Review records hot path, complexity/I-O counts, decision, evidence, and any no-measurement limits.
   - If a PR modifies Agent-facing workflows, generated instructions, collect plans, executable handoff artifacts, multi-step CLI workflows, or cross-host workflow chains, verify `agent-workflow-contract-review` produced `reports/workflow-contract-review/<slug>.md` with decision `submit`; all findings must be resolved or explicitly accepted with bounded rationale.
   - If a subagent, worker, delegated model, or generated custom agent changed files, verify delegated run evidence from `.agents/runs/agent-runs.jsonl` by explicit run identity. Missing run evidence, missing validation, validation failure, or scope violation is `no-submit`; missing token telemetry alone is not blocking.
   - If the ExecPlan declares quantitative targets, verify the Outcomes section records measured value vs. each target, and every unmet target has a Decision log entry that re-baselines it or explicitly accepts the miss with rationale. A fully-checked WBS with silently unmet declared targets is `no-submit`.
   - If feature-level embedded NFR work was triggered, verify `reports/resource/nfr-gate-report.md` exists and records `submit`, `no-submit`, or `experimental-only`; accept submit only when the embedded NFR gate is `submit` or the feature is explicitly experimental with production claims removed.
   - If production-ready, low-overhead, battery-safe, flash-safe, thermally-safe, or always-on claims depend on embedded NFRs, verify target characterization exists or the claim is explicitly provisional, budget provenance exists, calibration report exists when numeric budgets are claimed, calibration revisit conditions are not triggered, and the NFR gate report references these artifacts.
   - If `embedded-system-familiarization` was triggered, verify `docs/targets/<target>/system-familiarization.md` exists and lists required, created, missing, provisional, and deferred artifacts; artifact freshness/revisit conditions; controlled conditions; uncontrolled confounders; operating point coverage; claim-to-evidence traces with allowed wording; claims blocked by missing evidence; and handoff statuses using `not_needed`, `required_pending`, `completed`, `deferred_with_reason`, or `blocked`.
   - If an architecture, hardware, or embedded NFR claim depends on a hardware operating point, verify `docs/targets/<target>/controlled-operating-points.md` exists and the claim trace shows controlled evidence, adequate coverage, confidence, and allowed wording; otherwise the claim must be marked `blocked`, `provisional`, `experimental-only`, or limited to observed conditions.
   - If a hardware capability claim supports an architecture decision, verify the control surface and cost model are known in `docs/targets/<target>/hardware-control-surface-map.md`, `docs/targets/<target>/hardware-capability-map.md`, or `docs/targets/<target>/capability-cost-model.md`; otherwise the architecture claim must be blocked or explicitly provisional.
   - If only `embedded-project-constitution` was triggered, verify constitution artifacts exist. A feature-level NFR gate report is required only when feature runtime changes or production-readiness claims are introduced; constitution artifacts alone satisfy this branch otherwise.
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

- **Common pitfall:** deciding `no-submit` at the first failed item and skipping the rest of the checklist.
  **Instead:** finish the full sweep first so the submitter can fix everything in one round; then decide.
- **Common pitfall:** repeating deep-review taxonomy in quality-gate and making it verbose.
  **Instead:** limit gate to exit-criteria decisions and delegate deep dives to dedicated skills.
- **Common pitfall:** approving as mostly OK while required artifacts are missing.
  **Instead:** keep `no-submit` until required evidence for triggered branches is complete.
- **Common pitfall:** passing a structurally degraded change because all process artifacts exist (a monolithic entrypoint full of inline tests can satisfy every triggered-branch checklist).
  **Instead:** the structural exit check is its own criterion; findings from `scripts/check_structure.py` block submit even when every artifact is present.
- **Common pitfall:** duplicating the workflow-contract deep checklist inside this final gate.
  **Instead:** verify the report exists and its decision/findings status, then route deep issues back to `agent-workflow-contract-review`.
- **Common pitfall:** marking `submit` with vague records of unrun commands.
  **Instead:** for unrun commands, always record reason + reproduction steps and reflect that in submission decision.
- **Common pitfall:** accepting delegated work from a success claim or latest ledger entry.
  **Instead:** verify the explicitly cited run record and require validation/scope evidence; token absence alone is not a failure.

## Output expectation

- Start with: `Gate decision: submit` or `Gate decision: no-submit`.
- If `no-submit`, list each finding with: location, missing/failed criterion, required fix.
- Only output `0 findings` when all exit criteria are satisfied.


- Verify ledger by checking canonical path `.agents/design-ledger/function-boundaries.md`, not only final-response text.
- Verify delegated run evidence by checking `.agents/runs/agent-runs.jsonl` with an explicit run ID, not by latest/newest record selection.
- Verify embedded NFR evidence by checking the report artifact path, not only final-response text.
- Verify constitution-only evidence by checking the generated project artifacts, not only final-response text.
- Verify controlled operating point claims by checking the pack artifacts, not only final-response text.
