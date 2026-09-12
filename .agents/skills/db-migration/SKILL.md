---
name: db-migration
description: "Add or change a database migration, or review its data transformation and rollout. Not for ordinary queries."
---

# Database migration

Use the actual engine/version, data volume, access pattern and availability contract.
Inspect transformation semantics, lock duration, transaction/DDL behavior, concurrent
readers/writers and old/new application coexistence where rollout requires it.

Rehearse against approved disposable data, including null/duplicate/out-of-range
values and interruption/retry paths. State backup/restore or forward-recovery evidence
appropriate to reversibility. Schema success alone does not prove data integrity.

Compatibility follows the authorized product boundary. A playbook rewrite waiver is
not a database-deletion waiver. Do not run production DDL, delete data, or invent a
rollback story without authority and evidence. Missing production access blocks that
action, not a safe local rehearsal or a completed migration proposal.
