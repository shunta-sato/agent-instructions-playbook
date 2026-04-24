# Infrastructure Operations Report — ${RUNBOOK_NAME}

## 0. Summary

- Change request: `${CHANGE_REQUEST_ID}`
- Target: `${TARGET_SYSTEM}` (`${TARGET_ENVIRONMENT}`)
- Operator: `${OPERATOR}`
- Approver: `${APPROVER}`
- Start time (UTC): `${START_TIME_UTC}`
- End time (UTC): `${END_TIME_UTC}`
- Status: `success | partial | rolled_back | aborted`

## 1. Scope and Blast Radius

- Objective / target resources: `${TARGET_RESOURCES}`
- Declared blast radius: `${BLAST_RADIUS_SCOPE}`
- Destructive action included?: `${DESTRUCTIVE_ACTION_FLAG}`
- Risk notes: `${RISK_NOTES}`

## 2. Pre-check Evidence

- Maintenance/change window: `${MAINTENANCE_WINDOW}`
- Rollback/restore readiness: `${ROLLBACK_READINESS_EVIDENCE}`
- Baseline dashboards/alerts: `${BASELINE_DASHBOARD_LINK}`
- Assumptions/constraints: `${ASSUMPTIONS_AND_CONSTRAINTS}`

## 3. Dry-run Evidence

- Dry-run command/plan: `${DRY_RUN_COMMAND}`
- Dry-run summary (adds/updates/deletes): `${DRY_RUN_DIFF_SUMMARY}`
- Expected affected resource count: `${AFFECTED_RESOURCE_COUNT}`
- Scope match vs blast radius: `match | mismatch`
- Dry-run artifact/log link: `${DRY_RUN_EVIDENCE_LINK}`

## 4. Approval / Confirmation

- Approval record (ticket/chat/signoff): `${APPROVAL_RECORD}`
- Final pre-apply confirmation time (UTC): `${FINAL_CONFIRM_TIME_UTC}`
- Two-person confirmation (if required): `${TWO_PERSON_CONFIRM_EVIDENCE}`

## 5. Apply Timeline

| Time (UTC) | Phase | Action/Command | Scope | Result | Evidence |
|---|---|---|---|---|---|
| `${T1}` | phase-1 | `${APPLY_CMD_1}` | `${APPLY_PHASE_1}` | `pass/fail` | `${APPLY_EVIDENCE_1}` |
| `${T2}` | phase-2 | `${APPLY_CMD_2}` | `${APPLY_PHASE_2}` | `pass/fail` | `${APPLY_EVIDENCE_2}` |
| `${T3}` | phase-n | `${APPLY_CMD_N}` | `${APPLY_PHASE_N}` | `pass/fail` | `${APPLY_EVIDENCE_N}` |

## 6. Verification Results

| Check | Command/Probe | Result | Evidence |
|---|---|---|---|
| health/readiness | `${VERIFY_HEALTH_COMMAND}` | `pass/fail` | `${VERIFY_HEALTH_EVIDENCE}` |
| critical flow | `${VERIFY_CRITICAL_FLOW_COMMAND}` | `pass/fail` | `${VERIFY_CRITICAL_FLOW_EVIDENCE}` |
| state consistency | `${VERIFY_STATE_COMMAND}` | `pass/fail` | `${VERIFY_STATE_EVIDENCE}` |
| scope integrity | `${VERIFY_SCOPE_CHECK}` | `pass/fail` | `${VERIFY_SCOPE_EVIDENCE}` |

## 7. Soak and Cleanup

- Soak period configured: `${SOAK_PERIOD}`
- Soak outcome: `${SOAK_OUTCOME}`
- Cleanup actions performed: `${CLEANUP_ACTIONS}`
- Cleanup verification: `${CLEANUP_EVIDENCE}`

## 8. Audit Log and Compliance

- Execution log URI: `${EXECUTION_LOG_URI}`
- Audit log URI: `${AUDIT_LOG_URI}`
- Incident/deviation links: `${INCIDENT_OR_DEVIATION_LINKS}`
- Policy exceptions (if any): `${POLICY_EXCEPTIONS}`

## 9. Remaining Tasks

| Task | Owner | Due date (UTC) | Reason |
|---|---|---|---|
| `${REMAINING_TASK_1}` | `${TASK_OWNER_1}` | `${TASK_DUE_1}` | `${TASK_REASON_1}` |
| `${REMAINING_TASK_2}` | `${TASK_OWNER_2}` | `${TASK_DUE_2}` | `${TASK_REASON_2}` |

## 10. Final Sign-off

- Operator sign-off: `${OPERATOR_SIGNOFF}`
- Reviewer/Approver sign-off: `${APPROVER_SIGNOFF}`
- Ops/SRE acknowledgment: `${OPS_ACK}`
