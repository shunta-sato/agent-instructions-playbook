# Quality-gate exit checklist

This checklist is for `$quality-gate` only.
Focus on final decision criteria, not broad re-review taxonomy.

## 1) Command status (required)

- Canonical commands are recorded with exact commands + key results.
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
- C++ header branch → Doxygen completeness evidence
- ExecPlan required case → `plans/<slug>.md` is current (WBS/decisions/surprises/handoff)

## 3) Minimum exit criteria review (always)

- Path-specific instructions were identified and followed.
- Requirements/acceptance changes (if any) are reflected in docs/tests.
- Open risks or follow-ups are explicitly documented.

If deeper judgment is needed, invoke dedicated skills rather than expanding this checklist:
- readability → `$code-readability`
- modularity/boundaries → `$modularity`, `$architecture-boundaries`
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

Triggered branch evidence:
- <branch> — present|missing — artifact/path
```

Rule: `submit` only when all required criteria are satisfied and findings are 0.
