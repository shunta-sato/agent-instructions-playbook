# AGENTS.md Template

Use this template when proposing root or nested `AGENTS.md` changes. Keep the file compact and stable; move long explanations to human docs or `.agent/ctx` maps.

```markdown
# AGENTS.md

## Agent Context

Use these compact maps before broad search:

- General index: `.agent/ctx/index.md`
- Path map: `.agent/maps/paths.md`
- Skill map: `.agent/maps/skills.md`
- Test routing: `.agent/ctx/test.md`

## Hard Rules

- Do not edit generated clients or generated code directly.
- Do not log secrets, credentials, tokens, cookies, authorization headers, or private keys.
- Do not change public API shapes without explicit approval.
- Do not add production dependencies without approval.
- Do not run migrations, deploys, or destructive commands without explicit approval.
- Use targeted tests before broad suites.

## Work Routing

| Task | First map | First files | Skills | Targeted tests |
| --- | --- | --- | --- | --- |
| `<task phrase>` | `.agent/ctx/<area>.md` | `<entry points>` | `$<skill>` | `<command>` |

## Skill Routing

- `$<skill-name>`: `<trigger terms and boundary>`.

## Common Commands

- Build:
- Format:
- Lint:
- Static analysis:
- Targeted tests:
- Full verify:
```

## Nested AGENTS.md

Use nested files for area-specific constraints:

```text
services/auth/AGENTS.md
apps/web/AGENTS.md
packages/api-client/AGENTS.md
```

Nested files should state only local invariants, local entry points, local test commands, and local generated-file or API boundaries.

## Do Not Include

- Full design docs, API specs, past discussions, or issue logs.
- Skill bodies; link to skill names instead.
- Timestamps, request IDs, run logs, grep output, or temporary plans.
- User-specific data or secret values.
- Style rules that formatters or linters enforce.
