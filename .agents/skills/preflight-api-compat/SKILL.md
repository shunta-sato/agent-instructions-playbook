---
name: preflight-api-compat
description: "Preflight public API compatibility, OpenAPI, GraphQL, generated clients, public error shapes, versioning. Use before API-facing changes or generated client updates."
metadata:
  short-description: Public API compatibility preflight
---

# Preflight API Compat

## Purpose

Prepare public API or generated-client work before implementation starts. Extract
compatibility invariants, first docs/files, schema checks, consumer tests,
approvals, reviewers, and a handoff fragment for `preflight-engineering`.

This skill does not implement API changes, edit generated clients, publish
schemas, deploy, or decide compatibility exceptions.

## How to use

1. Confirm the trigger reason.
   - Use for OpenAPI, GraphQL, protobuf/IDL, public error shapes, versioning,
     generated clients, or API-facing compatibility preflight.
   - Skip when AGENTS/context/test routing are already current and the request is
     ordinary implementation.

2. Inspect API compatibility surfaces.
   - OpenAPI or Swagger specs.
   - GraphQL schema.
   - Protobuf, IDL, or RPC contracts.
   - Generated clients and regeneration docs.
   - API compatibility docs and versioning policy.
   - Public error shape definitions.
   - Consumer or contract tests.

3. Extract API invariants.
   - `API-SHAPE: Do not change public response shapes without explicit approval.`
   - `GENERATED-CLIENT: Do not manually edit generated clients.`
   - `API-SCHEMA: Schema changes need the documented compatibility check.`
   - `API-ERROR: Preserve public error code and payload compatibility.`
   - `CLIENT-REGEN: State the client regeneration path before implementation.`

4. Return the common output contract from `preflight-domain-template`.
   - Include `.agent/ctx/api.md` and nested `AGENTS.md` proposals only when useful.
   - Keep schema/versioning unknowns explicit.
   - Route generated-file and public API approvals before implementation starts.

## Reference routing

- Use `references/api-compat-reference.md` for compatibility checklist, output
  examples, and handoff fragment wording.

## Self-review

- Public API shape and error-shape compatibility are preserved or marked for approval.
- Generated-client ownership and regeneration path are confirmed or unknown.
- Consumer/contract test commands are confirmed or unknown.
- No generated client was edited during preflight.
