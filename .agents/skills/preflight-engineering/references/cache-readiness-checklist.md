# Cache Readiness Checklist

Use this checklist before handing off a long-running or multi-agent task.

```markdown
## Cache Readiness

- [ ] Root `AGENTS.md` contains stable guidance only.
- [ ] Nested `AGENTS.md` files contain area-specific stable guidance only.
- [ ] Long human docs are referenced, not pasted.
- [ ] Skill bodies are not pasted into `AGENTS.md`.
- [ ] `.agent/ctx` and `.agent/maps` paths are short, stable, and readable.
- [ ] Shared subagent prompt context appears before worker-specific context.
- [ ] Output schemas, tool lists, and order-sensitive lists are deterministic where relevant.
- [ ] User-specific or run-specific data is suffix-only.
- [ ] No timestamp, issue-specific log, request ID, grep output, test output, file snippet, or temporary plan appears in the stable prefix.
- [ ] Safety invariants, public API rules, generated-file boundaries, approval requirements, and test commands remain explicit.
```

## Failure Patterns

- `AGENTS.md` includes the current issue log or a temporary plan.
- Subagent prompts begin with different worker-specific context before shared constraints.
- Long docs are copied into Agent maps instead of linked.
- Safety rules are compressed into codes that only one person understands.
