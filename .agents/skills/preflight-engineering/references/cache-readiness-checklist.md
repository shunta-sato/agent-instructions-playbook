# Cache Readiness Checklist

Use this checklist before handing off a long-running or multi-agent task.

```markdown
## Cache Readiness

### Repo-stable prefix

- [ ] Root `AGENTS.md` contains stable guidance only.
- [ ] Nested `AGENTS.md` files contain area-specific stable guidance only.
- [ ] Long human docs are referenced, not pasted.
- [ ] Skill bodies are not pasted into `AGENTS.md`.
- [ ] `.agent/ctx` and `.agent/maps` paths are short, stable, and readable.
- [ ] Output schemas, tool lists, and order-sensitive lists are deterministic where relevant.
- [ ] No timestamp, issue-specific log, request ID, grep output, test output, file snippet, temporary plan, or user-specific data appears in repo-stable docs.
- [ ] Safety invariants, public API rules, generated-file boundaries, approval requirements, and test commands remain explicit.

### Task-stable shared prefix

- [ ] GOAL, acceptance criteria, shared constraints, shared context paths, and common output format are identical across subagent prompts for the same task.
- [ ] Task-stable shared context appears before worker-specific role, scope, file snippets, or findings.
- [ ] User-specific or run-specific data is suffix-only and stays out of repo-stable docs.
```

## Failure Patterns

- `AGENTS.md` includes the current issue log or a temporary plan.
- Subagent prompts begin with different worker-specific context before shared constraints.
- Long docs are copied into Agent maps instead of linked.
- Safety rules are compressed into codes that only one person understands.
- A task-specific shared GOAL is promoted into root `AGENTS.md` instead of staying in the handoff prompt.
