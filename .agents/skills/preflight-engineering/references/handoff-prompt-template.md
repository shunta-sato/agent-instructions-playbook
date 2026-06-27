# Development Commander Handoff Prompt Template

Use this at the end of preflight. Keep shared, stable context near the top and task-specific or worker-specific context later.

```markdown
You are the development commander for `<TASK_ID>`.

Goal:
<clear implementation goal>

Repository readiness:
- Follow root `AGENTS.md`.
- Follow nested `AGENTS.md` in relevant directories:
  - `<path>`
- Read compact Agent maps before broad search:
  - `.agent/ctx/index.md`
  - `.agent/maps/paths.md`
  - `.agent/maps/skills.md`
  - `.agent/ctx/<area>.md`

Hard constraints:
- Preserve public API compatibility unless explicitly approved.
- Do not edit generated files directly.
- Do not log secrets, credentials, tokens, cookies, authorization headers, or private keys.
- Do not add production dependencies without approval.
- Do not run migrations, deploys, or destructive commands without explicit approval.
- Keep the diff minimal.

Task-stable shared context:
- These lines must be identical in every subagent prompt for this task.
- GOAL:
- Acceptance criteria:
- Shared constraints:
- Shared output format:

Required skills:
- `$<skill>` for `<reason>`.

Subagent phase 1: read-only investigation
Spawn read-only subagents only after shared context and output format are fixed. Wait for all reports before implementation.

1. `<subagent name>`
   - Shared task context: reuse the section above verbatim.
   - Worker-specific suffix:
     - Scope:
     - Skills:
     - Must not edit:
     - Output:

Main implementation phase:
- Synthesize subagent findings in the main thread.
- Implement the smallest coherent patch.
- Run targeted tests before broad suites.

Subagent phase 2: read-only post-patch review
- `<reviewer>`: `<scope>`

Targeted test plan:
- `<command>` — `<surface verified>`

Final verification:
- `<canonical command>` — `<expected result>`

Final response format:
- Change brief
- Changed files
- Verification
- Remaining risks
```
