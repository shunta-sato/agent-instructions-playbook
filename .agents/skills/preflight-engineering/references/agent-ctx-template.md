# Agent Context Template

Create `.agent/ctx/*.md` and `.agent/maps/*.md` as compact work maps. They should help an agent start in the right place without rereading long human documentation.

```markdown
# <Area> Context

Status: confirmed | inferred | unknown

## Read First

- Human overview: `docs/<area>/<topic>.md`
- Compatibility notes: `docs/<area>/<compatibility>.md`
- Local instructions: `<path>/AGENTS.md`

## Entry Points

- Primary implementation: `<path>`
- Boundary adapter: `<path>`
- Error mapping: `<path>`
- Tests: `<path>`

## Invariants

- `<SECURITY-ID>`: `<security or secret-handling invariant>`.
- `<API-ID>`: `<public API compatibility invariant>`.
- `<GEN-ID>`: `<generated file boundary>`.
- `<TEST-ID>`: `<required targeted test>`.

## Work Routing

| Task phrase | Start here | Also inspect | Skills | Targeted tests |
| --- | --- | --- | --- | --- |
| `<phrase>` | `<path>` | `<path>` | `$<skill>` | `<command>` |

## Human Docs

- `<doc>`: `<what it explains>`

## Open Questions

- `<unknown>` — owner: `<human/team>` — blocks: `<what>`
```

## Rules

- Keep paths short but readable.
- Link to long docs instead of copying them.
- Mark every inferred fact as `inferred` until confirmed.
- Do not include secret values, logs, or run-specific findings.
- Do not compress safety rules into opaque codes that humans cannot audit.
