---
name: infrastructure-operations-template
description: "Template skill for infrastructure operations runbooks. Use when teams need reusable guardrailed procedures with dry-run, blast-radius controls, explicit approvals, soak windows, cleanup, and auditable execution reports."
metadata:
  short-description: Infrastructure operations runbook template
---

## Purpose

Use this template to standardize day-2 infrastructure operations (maintenance, config rollout, access changes, cleanup jobs, migrations) with strong safety rails.

It defines one reusable execution path:

pre-check → dry-run → approval/confirm → apply → verify → soak/cleanup → report.

The template is platform-agnostic and repository-safe (all env/resource values remain placeholders).

## When to use

Use this skill when:

- You are creating or revising runbooks for routine infrastructure operations.
- A task may impact production reliability, security posture, or shared resources.
- Any step can be destructive (delete, revoke, overwrite, restart, force-apply, bulk mutation).
- You need auditable evidence of who approved what, when, and with what outcome.

## How to use

1) Duplicate this template into a concrete ops skill/runbook if needed.

2) Fill placeholders in:

- `references/infrastructure-operations-checklist.md`
- `templates/infrastructure-operations-report-template.md`

Minimum placeholders to resolve:

- `${RUNBOOK_NAME}`
- `${TARGET_SYSTEM}`
- `${TARGET_ENVIRONMENT}`
- `${CHANGE_REQUEST_ID}`
- `${OPERATOR}`
- `${APPROVER}`
- `${BLAST_RADIUS_SCOPE}`
- `${SOAK_PERIOD}`
- `${AUDIT_LOG_URI}`

3) Execute **pre-check** (no changes yet).

- Confirm target identity and environment (avoid wrong-target execution).
- Confirm dependencies, maintenance window, and rollback/restore path.
- Confirm monitoring and alerting are healthy before changes.
- Classify blast radius (single resource, subset, all tenants/regions).
- Mark whether the run contains destructive actions.

4) Execute **dry-run** first.

- Use `--dry-run` / `plan` / `diff` mode where supported.
- Record expected adds/updates/deletes and affected resource count.
- Compare output against declared blast radius and stop on mismatch.
- If tool lacks native dry-run, run a read-only simulation and peer-review predicted impact.

5) Execute **approval/confirm** gate.

- Require explicit human approval before apply, especially for destructive steps.
- Use two-person rule for destructive operations whenever policy allows.
- Reconfirm scope, target, and rollback readiness immediately before apply.
- Capture ticket/approval evidence in the report.

6) Execute **apply** in controlled phases.

- Prefer smallest blast radius first (canary/subset before broad rollout).
- Timestamp each action and keep immutable command history.
- Pause at defined hold points for quick validation.
- Abort immediately if guardrail thresholds are breached.

7) Execute **verify** after each phase and after final apply.

- Validate service health, correctness checks, and critical user/system flows.
- Compare key signals against pre-change baseline.
- Confirm no unexpected resources were modified.
- Document pass/fail with evidence links.

8) Execute **soak/cleanup**.

- Observe the system for `${SOAK_PERIOD}` before declaring completion.
- Complete deferred cleanup (temp rules, feature flags, staged artifacts, access exceptions).
- Ensure cleanup itself has dry-run/approval if destructive.
- Capture post-change audit entries and residual risk notes.

9) Publish **report**.

- Fill `templates/infrastructure-operations-report-template.md`.
- Include scope, approvals, execution timeline, verification evidence, soak result, cleanup result, and remaining tasks.

## Destructive action policy (mandatory)

Treat any delete/revoke/overwrite/restart/force/bulk mutation as destructive.

Mandatory controls:

- **Dry-run evidence is required before destructive apply.**
- **Explicit approval is required at the exact destructive checkpoint (no blanket approval).**
- **Two-person confirmation (operator + approver) is required for broad blast radius.**
- **Rollback/restore procedure must be tested or rehearsed before execution.**
- **Stop-the-line rule:** if observed scope exceeds `${BLAST_RADIUS_SCOPE}`, abort and escalate.

## Guardrails (mandatory)

- **No apply without pre-check completion and target confirmation.**
- **No destructive action without dry-run evidence and approval evidence.**
- **No wide rollout without phased apply and verification holds.**
- **No completion without soak outcome, cleanup status, and audit-log links.**
- **No secrets in repository artifacts; placeholders/environment injection only.**

## Gotchas

- **ありがち:** dry-run を省略して apply を先に実行する。  
  **代わりに:** 先に `references/infrastructure-operations-checklist.md` の dry-run 項目を完了し、影響件数を report に固定する。
- **ありがち:** destructive step を通常変更と同じ承認で流す。  
  **代わりに:** destructive checkpoint ごとに明示 approval を取り、operator/approver を記録する。
- **ありがち:** apply 後すぐ完了扱いにして遅延障害を見逃す。  
  **代わりに:** soak period を必須化し、cleanup と監査ログ確認まで完了してから close する。

## Output expectation

When instantiated in another repository, include:

- Completed pre-check and dry-run evidence
- Blast-radius declaration and approval record
- Phase-by-phase apply and verify timeline
- Soak/cleanup outcomes and audit-log references
- Completed operations report with residual tasks and ownership
