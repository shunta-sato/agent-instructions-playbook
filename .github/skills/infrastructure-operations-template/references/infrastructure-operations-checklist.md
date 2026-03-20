# Infrastructure Operations Checklist (Template)

Use this checklist as an operator-facing runbook gate.
Replace placeholders with environment-specific values.

## 1) Pre-check (must pass before dry-run/apply)

- [ ] Change scope documented (`${CHANGE_REQUEST_ID}`) and runbook name fixed (`${RUNBOOK_NAME}`).
- [ ] Target system/environment confirmed (`${TARGET_SYSTEM}`, `${TARGET_ENVIRONMENT}`).
- [ ] Maintenance window and stakeholder notice confirmed (`${MAINTENANCE_WINDOW}`).
- [ ] Rollback/restore path available (`${ROLLBACK_RUNBOOK_URL}`, `${BACKUP_SNAPSHOT_ID}`).
- [ ] Monitoring/alerts healthy pre-change (`${DASHBOARD_URL}`, `${ALERT_STATUS}`).
- [ ] Blast radius declared (`${BLAST_RADIUS_SCOPE}`) and owner acknowledged.
- [ ] Destructive action present?: `yes/no` (`${DESTRUCTIVE_ACTION_FLAG}`).

## 2) Dry-run / Impact simulation (required)

- [ ] Dry-run command/plan executed (`${DRY_RUN_COMMAND}`).
- [ ] Expected adds/updates/deletes recorded (`${DRY_RUN_DIFF_SUMMARY}`).
- [ ] Affected resource count recorded (`${AFFECTED_RESOURCE_COUNT}`).
- [ ] Output scope matches declared blast radius (`${BLAST_RADIUS_SCOPE}`).
- [ ] If no native dry-run, read-only simulation and peer review completed.

## 3) Approval / Confirm gate

- [ ] Operator assigned (`${OPERATOR}`).
- [ ] Approver assigned (`${APPROVER}`).
- [ ] Approval ticket/link captured (`${APPROVAL_RECORD}`).
- [ ] Final target confirmation performed immediately before apply.
- [ ] Two-person confirmation done for destructive/broad-scope steps.

## 4) Apply execution (phased)

- [ ] Apply phase 1 scope defined (`${APPLY_PHASE_1}`).
- [ ] Apply phase 2 scope defined (`${APPLY_PHASE_2}`).
- [ ] Hold points defined (`${HOLD_POINT_1}`, `${HOLD_POINT_2}`).
- [ ] Command history and timestamps captured (`${EXECUTION_LOG_URI}`).
- [ ] Abort condition/owner confirmed (`${ABORT_CONDITION}`, `${INCIDENT_OWNER}`).

## 5) Verify

- [ ] Health and readiness checks pass (`${VERIFY_HEALTH_COMMAND}`).
- [ ] Critical flow check passes (`${VERIFY_CRITICAL_FLOW_COMMAND}`).
- [ ] Config/state consistency check passes (`${VERIFY_STATE_COMMAND}`).
- [ ] No out-of-scope resources changed.
- [ ] Verification evidence links captured.

## 6) Soak / Cleanup

- [ ] Soak observation window completed (`${SOAK_PERIOD}`).
- [ ] Delayed alerts/incidents checked (`${SOAK_ALERT_CHECK}`).
- [ ] Temporary controls/artifacts cleaned (`${CLEANUP_ITEMS}`).
- [ ] Elevated permissions/exception access revoked.
- [ ] Cleanup verification evidence captured.

## 7) Audit log / Report completion

- [ ] Audit log location captured (`${AUDIT_LOG_URI}`).
- [ ] Report template completed (`templates/infrastructure-operations-report-template.md`).
- [ ] Remaining tasks and owners documented (`${REMAINING_TASKS}`).
- [ ] Final sign-off captured (`${FINAL_SIGNOFF}`).
