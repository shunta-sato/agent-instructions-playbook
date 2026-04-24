# CI/CD Deployment Checklist (Template)

Use this checklist as an operator-facing gate before and during deployment.
Replace placeholders with environment-specific values.

## 1) Preflight (must pass before deploy)

- [ ] Change scope documented (`${CHANGE_REQUEST_ID}`) and release notes linked.
- [ ] Target environment confirmed (`${ENVIRONMENT}`) and freeze-window policy checked.
- [ ] On-call / incident channel staffed (`${ONCALL_PRIMARY}`, `${INCIDENT_CHANNEL}`).
- [ ] Rollback runbook exists and verified (`${ROLLBACK_RUNBOOK_URL}`).
- [ ] Last known good artifact identified (`${LAST_KNOWN_GOOD_ARTIFACT}`).
- [ ] Required approval captured (`${DEPLOY_APPROVER}`) for prod/destructive steps.
- [ ] Monitoring dashboards and alerts green before rollout (`${DASHBOARD_URL}`).

## 2) Artifact / Build Integrity

- [ ] Artifact built from pinned commit SHA (`${GIT_SHA}`).
- [ ] Artifact URI recorded (`${ARTIFACT_URI}`).
- [ ] Digest/checksum recorded (`${ARTIFACT_DIGEST}`).
- [ ] Provenance/signature policy check done (if applicable).
- [ ] Config/version compatibility check complete.

## 3) Smoke Test Gate

- [ ] Health endpoint passes (`${SMOKE_HEALTH_COMMAND}`).
- [ ] Readiness endpoint passes (`${SMOKE_READINESS_COMMAND}`).
- [ ] Critical user/API flow passes (`${SMOKE_CRITICAL_FLOW_COMMAND}`).
- [ ] Smoke evidence links added (`${SMOKE_LOG_URL}`).

## 4) Staged Rollout Plan

- [ ] Phase 1 (canary): `${ROLLOUT_PHASE_1}` with hold `${HOLD_WINDOW_1}`.
- [ ] Phase 2 (partial): `${ROLLOUT_PHASE_2}` with hold `${HOLD_WINDOW_2}`.
- [ ] Phase 3 (full): `${ROLLOUT_PHASE_3}` with hold `${HOLD_WINDOW_3}`.
- [ ] Approval point before full rollout completed.

## 5) Rollback Trigger Gate

Rollback if **any** condition is true:

- [ ] `error_rate > ${SLO_ERROR_RATE_THRESHOLD}` for `${ERROR_BREACH_DURATION}`.
- [ ] `p95_latency_ms > ${SLO_LATENCY_THRESHOLD}` for `${LATENCY_BREACH_DURATION}`.
- [ ] Critical smoke/business check failed in current phase.
- [ ] `${CRITICAL_ALERT_NAME}` unresolved beyond hold window.
- [ ] Incident commander/manual operator rollback decision.

## 6) Post-deploy Verification

- [ ] Health/readiness stable for `${POST_DEPLOY_OBSERVE_WINDOW}`.
- [ ] Key business metrics are within acceptable baseline drift.
- [ ] Error budget burn-rate is acceptable.
- [ ] No new sustained critical alerts.
- [ ] Deployment report completed and peer-reviewable.
