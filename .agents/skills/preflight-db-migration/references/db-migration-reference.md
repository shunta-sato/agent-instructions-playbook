# DB Migration Preflight Reference

## First Docs

- Migration policy.
- Rollback or forward-fix docs.
- Data compatibility docs.
- Backfill or background job runbooks.
- Persistence-layer testing docs.

## First Files

- `migrations/**`
- `db/migrate/**`
- `alembic/**`
- `prisma/schema.prisma`
- `schema.sql`
- `models/**`
- `ormconfig*`, `database.yml`
- `seeds/**`
- `jobs/**/backfill*`, `tasks/**/backfill*`
- `tests/**/migration*`, `tests/**/persistence*`

## Example Domain Invariants

- `DB-NO-RUN: Do not execute migrations or backfills during preflight.`
- `DB-ROLLBACK: Every migration needs rollback or forward-fix guidance.`
- `DB-DESTRUCTIVE: Dropping columns, tables, constraints, or data requires explicit approval.`
- `DB-BACKFILL: Backfill execution boundaries must be documented before implementation.`
- `DB-COMPAT: Old and new app versions must be compatible during rollout unless explicitly approved.`

## Example Output Fragments

### `.agent/ctx/db.md` Proposal

```markdown
## Domain

- DB migration and persistence.

## Invariants

- DB-NO-RUN: Do not execute migrations or backfills during preflight.
- DB-DESTRUCTIVE: Destructive schema changes require explicit approval.

## First Files

- `migrations/` — migration history and naming convention.
- `<schema file>` — canonical schema source.

## Test Routing

- `<migration validation command>` — migration lint/schema check.
- `<persistence test command>` — persistence regression coverage.
```

### Nested `AGENTS.md` Proposal

```markdown
# DB Migration Agent Notes

- DB-NO-RUN: Do not run migrations or backfills during preflight.
- DB-ROLLBACK: Record rollback or forward-fix guidance.
- DB-COMPAT: Preserve old-app/new-app compatibility unless approval is recorded.
```

### Handoff Fragment

```markdown
## Domain: DB migration

- Preserve migration execution, rollback, destructive-change, backfill, and compatibility boundaries.
- Start with `<migration dirs>`, `<schema files>`, and `<rollback docs>`.
- Run `<migration validation>` and `<persistence tests>` or mark commands unknown.
```
