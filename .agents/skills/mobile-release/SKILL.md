---
name: mobile-release
description: "Prepare or coordinate mobile signing, build distribution, store rollout, or cross-platform release compatibility."
---

# Mobile release

Separate a release proposal from signing, upload, publication and staged rollout.
Establish intended versions, supported platform/OS combinations, native dependency
changes, backend/API compatibility, data migration and rollback/forward recovery.

Use the project's real release checks, signing ownership and store/environment
approvals. A successful debug build or simulator test is not signed release evidence.
Coordinate Android/iOS semantics where needed without assuming simultaneous store
approval. Preserve version and build provenance through distribution.

Continue approved preparation and verification; stop only the unapproved external
action. Never infer publication permission from access to a signing key, account,
CI secret or an agent-generated release plan. Report the exact build, completed
checks, remaining approval and supported rollback/rollout limits.
