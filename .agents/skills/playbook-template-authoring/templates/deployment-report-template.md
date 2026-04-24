# Deployment Report — ${SERVICE_NAME} (${ENVIRONMENT})

## 0. Summary

- Change request: `${CHANGE_REQUEST_ID}`
- Deploy owner: `${DEPLOY_OWNER}`
- Approver: `${DEPLOY_APPROVER}`
- Start time (UTC): `${DEPLOY_START_UTC}`
- End time (UTC): `${DEPLOY_END_UTC}`
- Status: `success | partial | rolled_back | aborted`

## 1. Preflight

- Change window: `${CHANGE_WINDOW}`
- Freeze policy check: `pass | fail`
- On-call readiness: `${ONCALL_PRIMARY}`
- Rollback runbook: `${ROLLBACK_RUNBOOK_URL}`
- Approval evidence: `${APPROVAL_LINK_OR_TICKET}`

## 2. Artifact / Build

- Commit SHA: `${GIT_SHA}`
- Build ID/URL: `${BUILD_URL}`
- Artifact URI: `${ARTIFACT_URI}`
- Artifact digest: `${ARTIFACT_DIGEST}`
- Provenance/signature check: `pass | fail | n/a`

## 3. Smoke Test Results

| Check | Command/Probe | Result | Evidence |
|---|---|---|---|
| health | `${SMOKE_HEALTH_COMMAND}` | `pass/fail` | `${SMOKE_HEALTH_EVIDENCE}` |
| readiness | `${SMOKE_READINESS_COMMAND}` | `pass/fail` | `${SMOKE_READINESS_EVIDENCE}` |
| critical flow | `${SMOKE_CRITICAL_FLOW_COMMAND}` | `pass/fail` | `${SMOKE_CRITICAL_FLOW_EVIDENCE}` |

## 4. Rollout Timeline

| Time (UTC) | Phase | Traffic/Scope | Hold window | Decision |
|---|---|---|---|---|
| `${T1}` | canary | `${ROLLOUT_PHASE_1}` | `${HOLD_WINDOW_1}` | `proceed/rollback/abort` |
| `${T2}` | partial | `${ROLLOUT_PHASE_2}` | `${HOLD_WINDOW_2}` | `proceed/rollback/abort` |
| `${T3}` | full | `${ROLLOUT_PHASE_3}` | `${HOLD_WINDOW_3}` | `complete/rollback` |

## 5. Verification (post-phase / post-deploy)

- Error rate trend vs threshold `${SLO_ERROR_RATE_THRESHOLD}`: `${ERROR_RATE_RESULT}`
- P95 latency trend vs threshold `${SLO_LATENCY_THRESHOLD}`: `${LATENCY_RESULT}`
- Resource saturation (CPU/memory/queue/thread): `${RESOURCE_RESULT}`
- Critical business flow metrics: `${BUSINESS_FLOW_RESULT}`
- Dashboard link(s): `${DASHBOARD_URL}`

## 6. Rollback Decision

- Rollback triggered?: `yes | no`
- Trigger(s): `${ROLLBACK_TRIGGER_LIST}`
- Trigger timestamp(s): `${ROLLBACK_TRIGGER_TIME}`
- Action taken: `${ROLLBACK_ACTION}`
- Recovery outcome: `${RECOVERY_OUTCOME}`

## 7. Incidents / Deviations

- Incident link: `${INCIDENT_LINK}`
- Notable deviations from plan: `${DEPLOY_DEVIATIONS}`
- Follow-up tasks: `${FOLLOWUP_ITEMS}`

## 8. Final Sign-off

- Deploy owner sign-off: `${DEPLOY_OWNER_SIGNOFF}`
- Reviewer sign-off: `${REVIEWER_SIGNOFF}`
- Ops/SRE acknowledgment (if required): `${OPS_ACK}`
