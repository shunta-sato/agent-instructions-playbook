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
- observability branch → logs/metrics/traces plan or implementation evidence
- staged-lowering branch → staged plan + per-pass verification log
- legacy branch → characterization/safety-net evidence + seam/refactor notes
- structural scan branch → smells/anti-patterns result (new/worsened handled)
- function-boundary-governor branch → function-boundary decision record
- destructive-refactor branch → convergence record (replaced|no-op|rollback), migrated call-sites evidence, red-state usage record
- function-design ledger-needed cases → ledger entry present (replaced abstraction / intentional duplication / staged adapter)
- C++ header branch → Doxygen completeness evidence
- ExecPlan required case → `plans/<slug>.md` is current (WBS/decisions/surprises/handoff)

## 3) Minimum exit criteria review (always)

- Path-specific instructions were identified and followed.
- Requirements/acceptance changes (if any) are reflected in docs/tests.
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
