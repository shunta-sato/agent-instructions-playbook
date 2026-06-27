# API Compatibility Preflight Reference

## First Docs

- API compatibility policy.
- Versioning policy.
- Generated client regeneration docs.
- Public error-shape docs.
- Consumer contract test docs.

## First Files

- `openapi.yaml`, `openapi.json`, `swagger.yaml`, `swagger.json`
- `schema.graphql`, `*.graphql`
- `proto/**`, `*.proto`, `idl/**`
- `packages/*client*/**`, `clients/**`, `generated/**`
- `tests/**/contract*`, `tests/**/consumer*`, `tests/**/api*`

## Example Domain Invariants

- `API-SHAPE: Do not change public response shapes without explicit approval.`
- `API-ERROR: Preserve documented public error code and payload compatibility.`
- `API-SCHEMA: Run the documented schema compatibility check before submit.`
- `GENERATED-CLIENT: Do not manually edit generated clients.`
- `CLIENT-REGEN: Record the client regeneration command and owner before implementation.`

## Example Output Fragments

### `.agent/ctx/api.md` Proposal

```markdown
## Domain

- Public API compatibility.

## Invariants

- API-SHAPE: Public response shapes require explicit compatibility approval before changing.
- GENERATED-CLIENT: Regenerate clients through the documented path.

## First Docs

- `<compat policy>` — compatibility and versioning rules.

## Test Routing

- `<schema compatibility command>` — schema diff/compatibility check.
- `<consumer test command>` — consumer contract coverage.
```

### Nested `AGENTS.md` Proposal

```markdown
# API Compatibility Agent Notes

- API-SHAPE: Preserve public response shapes unless approval is recorded.
- API-ERROR: Preserve error code and payload compatibility.
- GENERATED-CLIENT: Do not hand-edit generated clients.
```

### Handoff Fragment

```markdown
## Domain: public API compatibility

- Preserve API shape, error payload, versioning, and generated-client invariants.
- Start with `<schema files>`, `<compat docs>`, and `<client generation docs>`.
- Run `<schema compatibility>` and `<consumer tests>` or mark commands unknown.
```
