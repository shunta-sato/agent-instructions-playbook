---
name: database-migration
description: "Use when creating or changing a persistent-data migration or reviewing its rollout; not for ordinary queries."
---

# Persistent-data migration

Identify data owners, old/new schemas, supported readers/writers and actual rollout
order. Determine transactionality, locks, duration, storage headroom and recovery
from interruption using the real engine/version and workload.

Preserve data integrity and permissions. An API compatibility waiver does not
authorize destructive production data operations. Practice on authorized disposable
or sanitized fixtures; do not infer production access from a migration file.

Verify restart/idempotency, malformed/edge records and version skew where relevant.
Distinguish rollback from forward repair when data transformations are lossy.
Use staged compatibility only when the product rollout needs it, with a removal
condition. Record executable rollout/recovery commands and remaining gates for the
operator; writing or testing the migration is not approval to deploy it.
