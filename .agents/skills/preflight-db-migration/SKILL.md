---
name: preflight-db-migration
description: "Preflight DB migration, schema change, rollback, backfill, data compatibility, transaction boundary. Use before database or persistence-layer changes."
metadata:
  short-description: DB migration preflight
  resources:
    - references/db-migration-reference.md
---

# Preflight DB Migration

## Purpose

Prepare database, migration, persistence, rollback, backfill, and data
compatibility work before implementation starts. Extract migration safety
invariants, first docs/files, validation commands, approvals, reviewers, and a
handoff fragment for `preflight-engineering`.

This skill does not implement product changes, read or copy secret values, run
migrations, execute backfills, deploy, connect to production databases, edit
generated clients, or approve destructive schema work.

## How to use

1. Confirm the trigger reason.
   - Use for schema changes, migrations, rollback/forward-fix planning,
     backfills, data compatibility, transaction boundaries, or persistence-layer preflight.
   - Skip when AGENTS/context/test routing are already current and the request is
     ordinary implementation.

2. Inspect DB and migration surfaces.
   - Migration directories.
   - Schema files.
   - ORM config.
   - Seed files.
   - Migration test commands.
   - Rollback docs.
   - Data compatibility docs.
   - Background job and backfill paths.

3. Extract DB invariants.
   - `DB-NO-RUN: Do not execute migrations or backfills during preflight.`
   - `DB-ROLLBACK: Record rollback or forward-fix guidance for every migration.`
   - `DB-DESTRUCTIVE: Destructive schema changes require explicit human approval.`
   - `DB-BACKFILL: State the execution boundary for backfills and data migrations.`
   - `DB-COMPAT: Check old-app/new-app compatibility before implementation.`

4. Return the common output contract from `preflight-domain-template`.
   - Propose `.agent/ctx/db.md`, `db/AGENTS.md`, or `migrations/AGENTS.md`
     content only when the repository shape supports it.
   - Keep migration execution and approval unknowns explicit.
   - Route destructive or production data risks to human approval before implementation.

## Reference routing

- Use `references/db-migration-reference.md` for safety checklist, output
  examples, and handoff fragment wording.

## Self-review

- No migration, seed, backfill, deploy, or production DB command was executed.
- No secret value was read or copied, and no generated client was edited.
- Destructive schema or data-risk approvals are explicit.
- Rollback or forward-fix expectations are recorded or unknown.
- Old-app/new-app compatibility and targeted migration validation are recorded or unknown.

## Output expectation

- Return the common output contract from `preflight-domain-template`, filled for the DB/migration domain.
- Include the five DB invariants (`DB-NO-RUN`, `DB-ROLLBACK`, `DB-DESTRUCTIVE`, `DB-BACKFILL`, `DB-COMPAT`) verbatim when applicable, or state why one does not apply.
- Keep migration execution and approval unknowns explicit.
- Route destructive or production data risks to explicit human approval before implementation.
