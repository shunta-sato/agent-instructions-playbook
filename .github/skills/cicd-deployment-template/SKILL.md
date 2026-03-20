---
name: cicd-deployment-template
description: "Template skill for CI/CD deployment playbooks. Use when teams need a reusable deploy workflow with preflight checks, artifact build integrity, smoke tests, staged rollout, rollback triggers, and reviewable deployment reports."
metadata:
  short-description: CI/CD & deployment template
---

## Purpose

Use this template to standardize deployment execution as a reusable playbook:

preflight → artifact/build → smoke test → staged rollout → verification → rollback decision → report.

The template is environment-agnostic and safe for repository reuse (all infra values are placeholders).

## When to use

Use this skill when:

- You are adding or revising CI/CD deployment procedures.
- Teams need explicit approval/guardrails for production or destructive operations.
- You need deterministic deployment evidence (what changed, what was verified, and rollback readiness).

## How to use

1) Duplicate this template to a concrete deployment skill name if needed.

2) Fill placeholders in `templates/deployment-report-template.md` and `references/deployment-checklist.md`:

- `${SERVICE_NAME}`
- `${ENVIRONMENT}`
- `${ARTIFACT_URI}`
- `${CHANGE_REQUEST_ID}`
- `${DEPLOY_APPROVER}`
- `${ROLLBACK_RUNBOOK_URL}`
- `${SLO_ERROR_RATE_THRESHOLD}`
- `${SLO_LATENCY_THRESHOLD}`

3) Run **preflight** first (no deploy yet).

- Confirm change window, release freeze status, and on-call availability.
- Confirm rollback artifacts exist and are restorable.
- Confirm monitoring dashboards + alerts are healthy before rollout.
- Confirm approval point for production/destructive steps is explicitly captured.

4) Build and validate deploy artifacts.

- Build immutable artifact and record digest/checksum.
- Verify provenance/signature policy if your org requires it.
- Attach artifact metadata to the report (version, commit SHA, build URL).

5) Run smoke tests in target-like environment.

- Execute mandatory smoke suite (`health`, `readiness`, critical-path API/job).
- Record pass/fail and links to logs.
- If smoke fails, stop rollout and execute rollback/abort criteria.

6) Execute staged rollout.

- Use phases (e.g., canary 1–5% → partial 25–50% → full 100%).
- Keep hold points between phases with explicit observation windows.
- Require re-approval before crossing into production/full rollout when policy requires.

7) Verify after each phase and after full deployment.

- Compare key SLO/SLI signals vs baseline (error rate, latency, saturation, queue lag).
- Verify business-critical user journeys.
- Confirm no regression in logs/alerts.

8) Evaluate rollback triggers continuously.

- Trigger rollback if any hard threshold breach occurs or safety signal persists beyond hold window.
- If rollback is triggered, document exact trigger, time, and operator action.

9) Publish deployment report.

- Fill `templates/deployment-report-template.md` with evidence links.
- Include approval records, rollout timeline, verification outcomes, and rollback readiness status.

## Guardrails (mandatory)

- **No production or destructive operation without an explicit approval point.**
- **No direct secret values in repo artifacts; placeholders/environment injection only.**
- **No full rollout if smoke test or canary verification is incomplete.**
- **Rollback path must be validated before starting rollout.**

## Rollback triggers (minimum set)

Document concrete values per environment, then enforce at runtime:

- Error-rate breach: `error_rate > ${SLO_ERROR_RATE_THRESHOLD}` for `${ERROR_BREACH_DURATION}`.
- Latency breach: `p95_latency_ms > ${SLO_LATENCY_THRESHOLD}` for `${LATENCY_BREACH_DURATION}`.
- Critical path failure: smoke/business-critical check fails in current phase.
- Safety alert: paging alert (`${CRITICAL_ALERT_NAME}`) remains unresolved through hold window.
- Operator judgment: incident commander / deploy owner invokes manual rollback.

## Deploy-after verification focus

At minimum, verify and report:

- Service health/readiness and dependency connectivity.
- User-facing critical flow success metrics.
- Error budget burn-rate trend.
- Resource saturation regression (CPU/memory/thread/queue).
- Data correctness guard checks (if migrations/async pipelines are involved).

## Gotchas

- **ありがち:** preflight を飛ばして本番 deploy を始める。  
  **代わりに:** 先に `references/deployment-checklist.md` の preflight を完了し、承認者と rollback runbook を report に固定する。
- **ありがち:** canary 成功前に一気に 100% rollout する。  
  **代わりに:** 段階 rollout + hold window を守り、phase ごとに SLI を確認してから次に進む。
- **ありがち:** rollback 条件が曖昧で障害時に判断が遅れる。  
  **代わりに:** しきい値・継続時間・責任者を事前定義し、違反時は自動/手動 rollback を即時実行する。

## Output expectation

When instantiated in another repository, include:

- Completed preflight + approval evidence
- Artifact identity and smoke test results
- Phase-by-phase rollout and verification timeline
- Explicit rollback trigger table and final rollback readiness
- Completed deployment report with links to logs/dashboards/incidents
