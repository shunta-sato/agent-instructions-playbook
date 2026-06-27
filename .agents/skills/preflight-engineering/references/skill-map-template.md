# Skill Map Template

Use this template for `.agent/maps/skills.md` or the `Skill routing` section in `AGENTS.md`.

```markdown
# Skill Map

## Existing Skills

| Skill | Trigger terms | Use when | Do not use when | First docs |
| --- | --- | --- | --- | --- |
| `$<skill>` | `<terms>` | `<scope>` | `<boundary>` | `<path>` |

## Missing Skill Candidates

| Candidate skill | Trigger gap | Example task | Expected output | Priority |
| --- | --- | --- | --- | --- |
| `<name>` | `<gap>` | `<request>` | `<artifact>` | low / medium / high |

## Routing Notes

- Prefer existing repo skills before creating new ones.
- Keep skill bodies out of `AGENTS.md`; route by name, trigger, and first docs.
- If a skill is missing, describe the gap and continue with the best existing workflow.
- Use targeted tests and review skills for high-risk areas such as auth, billing, security, public API, DB migration, generated clients, and production config.
```
