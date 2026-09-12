---
name: boundary-migration
description: "Replace or retire public or cross-module contracts, migrate callers, or verify that a superseded API is gone."
---

# Boundary migration

Establish the changed contract and its required callers, including external callers
that repository search cannot enumerate. Separate intentionally parallel concepts
from obsolete implementations. Similar text is not proof of equivalent error
behavior, state ownership, or side effects.

Use the request's compatibility scope. A waiver for playbook names is not permission
to break a consumer product's APIs or persistent data. Under an explicit break-allowed
scope, remove the superseded path rather than keeping aliases, deprecated exports,
or compatibility wrappers. A staged migration needs a real external obligation and
a removal condition, not a default precaution.

Temporary build/test failure during an authorized replacement is acceptable locally;
it is not a releasable result. Migrate the affected callers and converge on the target
contract. Use new evidence to decide the next action. Roll back when recovery and
remaining risk justify it, not because a fixed number of failures occurred.

Use `scripts/check_api_removal.py --symbol OLD_NAME PATH...` for an explicit removed
symbol sweep. Inspect generated clients, dynamic lookup and documented external
surfaces separately where applicable. Missing search inputs are errors, not proof
that nothing survives. Report contract changes, migrated callers and actual proof in
the existing PR; no dedicated function ledger or break-window form is required.
