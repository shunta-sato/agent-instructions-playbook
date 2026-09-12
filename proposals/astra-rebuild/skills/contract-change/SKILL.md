---
name: contract-change
description: "Use when replacing an API or abstraction, changing public contracts, or migrating multiple callers; not for routine local edits."
---

# Contract change

Identify the affected contract and its real consumers: inputs/outputs, errors,
effects, ownership, generated clients, persistent formats and version skew.
Confirm the compatibility scope from the request and product obligations. An
explicit playbook rewrite waiver is not permission to break a consumer's API.

Under an authorized break, converge callers and remove superseded names, aliases,
shims and parallel old/new paths. Keep parallel concepts only when intentionally
required. Under a real staged rollout, identify the adapter consumer and removal
condition. Do not ask again for an already-granted in-scope waiver.

Temporary local build/test failures are acceptable inside an authorized change;
no separate break-window form is required. Preserve unrelated work. Verify the
new contract, supported failure behavior and callers; search for remaining old
entrypoints and generated outputs. Do not publish a partially converged release.

Choose rollback from risk and recoverability, not two failed runs. New evidence can
justify further debugging. Record only durable contract decisions and migration
limits in the existing PR or specification; no function-design ledger is required.
