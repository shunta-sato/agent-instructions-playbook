# Quality-gate exit checklist

This checklist is for `$quality-gate` only.
Focus on final decision criteria, not broad re-review taxonomy.

## 1) Command status (required)

- Canonical commands are recorded with exact commands + key results.
- If external systems/tools were involved, live-discovery evidence is recorded before static examples were trusted: command/interface source, version or status output, schema/config path, connection state, and artifact/log path.
- Required depth matches routed risk:
  - low risk: canonical minimum for changed surface
  - normal/high risk: full chain (build / format / static analysis / tests)
- Any skipped command includes reason + reproducible procedure.

## 2) Triggered-branch evidence (required when triggered)

Confirm required evidence exists for each triggered branch:

- bugfix branch → Bug Report (repro/evidence/Five Whys/verification/prevention)
- UI branch → UI Visual Verification Report + artifact paths
- concurrency branch → concurrency verification evidence (plan/shutdown-verification/logging)
- architecture-decision-analysis branch → Architecture Decision Analysis Record with decision/no-decision, quality drivers, option tradeoffs, verification tasks, and handoffs
- observability branch → Observability Plan with logs/metrics/traces evidence plus signal purpose, actionability, counter-metric where relevant, and artifact paths
- implementation-economy branch → Complexity Budget plus Post-Implementation Economy Audit, including keep/delete/inline/merge decisions for new abstractions
- design-balance branch → Responsibility Map with unit, name, responsibility sentence, reason to change, and dependency direction
- feature-level embedded NFR branch → `reports/resource/nfr-gate-report.md` with decision, runtime mode classification, artifact check, budget results, claims review, and unknowns/limits
- embedded system familiarization branch → `docs/targets/<target>/system-familiarization.md` with required/created/missing/provisional/deferred artifacts, artifact freshness/revisit conditions, claims blocked by missing evidence, and handoff statuses (`not_needed|required_pending|completed|deferred_with_reason|blocked`)
- embedded target characterization branch → `docs/targets/<target>/target-characterization.md`, `target_profiles/<target>.yaml`, baseline paths, and characterization report when production claims depend on target behavior
- embedded operating envelope branch → `docs/targets/<target>/operating-envelope.md` and scenario reports for normal, degraded, boundary, observer, recovery, or blackout behavior
- embedded NFR calibration branch → `reports/nfr-calibration/<feature>.md` plus budget provenance when numeric production budgets are claimed
- constitution-only embedded branch → constitution artifacts such as project principles, resource discipline, physical budgets, target profiles, resource harness skeleton, and PR-template section. Do not require a feature-level NFR gate report unless runtime changes or production-readiness claims are introduced.
- staged-lowering branch → staged plan + per-pass verification log
- legacy branch → characterization/safety-net evidence + seam/refactor notes
- structural scan branch → smells/anti-patterns result (new/worsened handled)
- function-boundary-governor branch → function-boundary decision record
- destructive-refactor branch → convergence record (replaced|no-op|rollback), migrated call-sites evidence, red-state usage record
- function-design ledger-needed cases → ledger entry present (replaced abstraction / intentional duplication / staged adapter)
- C++ header branch → Doxygen completeness evidence
- ExecPlan required case → `plans/<slug>.md` is current (WBS/decisions/surprises/handoff)
- study-note branch → Study Pack Report with source classification, files created/updated, contracts applied, semantic review decision when applicable, mechanical gate decision when publish/sync was requested

## 3) Minimum exit criteria review (always)

- Path-specific instructions were identified and followed.
- Requirements/acceptance changes (if any) are reflected in docs/tests.
- Default-lane evidence is present for normal/high-risk work, or the low-risk skip reason is explicit.
- If embedded NFR work was triggered, no low-overhead, battery-safe, lightweight, flash-safe, thermally-safe, or production-ready claim remains without measurement evidence or explicit experimental-only limits.
- If embedded NFR claims depend on target behavior, target characterization exists or the claim is explicitly provisional.
- If numeric production budgets are claimed, budget provenance exists, calibration artifacts are referenced, and calibration revisit conditions are not triggered.
- If feature-level embedded NFR work was triggered, target-local background behavior is classified as default, burst, experimental-only, or debug-only.
- Open risks or follow-ups are explicitly documented.

If deeper judgment is needed, invoke dedicated skills rather than expanding this checklist:
- readability → `$code-readability`
- maintainability/modularity/boundaries → `$code-smells-and-antipatterns`
- error handling → `$error-handling`
- concurrency details → `$concurrency-core`, `$thread-safety-tooling`
- observability details → `$observability`

## 4) Gate decision format (required)

```markdown
Gate decision: submit|no-submit

Findings:
- [ID] location — failed/missing criterion — required fix

Checks run:
- <command> — pass|fail|skipped (reason)

Live discovery:
- <external/tool surface> — source/version/status/config/artifact evidence or not applicable

Triggered branch evidence:
- <branch> — present|missing — artifact/path
```

Rule: `submit` only when all required criteria are satisfied and findings are 0.


- Verify ledger by checking canonical path `.agents/design-ledger/function-boundaries.md`, not only final-response text.
- Verify embedded NFR evidence by checking `reports/resource/nfr-gate-report.md`, not only final-response text.
