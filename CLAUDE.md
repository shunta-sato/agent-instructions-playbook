# CLAUDE.md — Claude Code entry point

`AGENTS.md` is the canonical repository contract. Read it first. This file maps
that contract to Claude Code and does not redefine delivery or quality policy.

## Claude Code mapping

- **Skills:** `.claude/skills/<name>` links to `.agents/skills/<name>`. Explicit
  skill requests use `/<skill>`. Apply the four-tier load contract from
  `AGENTS.md`.
- **Feature delivery:** the root agent owns `user-value-delivery`, Delivery
  Control, route lock, and candidate identity. Workers receive a read-only task
  brief and focused validation. The assigned owner performs the final
  `quality-gate` once per candidate.
- **Delegation:** use `.claude/agents/playbook-worker.md`,
  `playbook-explorer.md`, and `playbook-reviewer.md` rather than ad-hoc prompts.
  Do not ask each role to repeat the full workflow.
- **Model routing:** use `.agents/model-routing/task-classes.yml`, catalog, and
  route lockfile only after confirming `harness: claude-code`. Do not export
  concrete model IDs to another harness.
- **Run evidence:** record delegated and supervision runs with
  `python3 scripts/agent_run.py record --harness claude-code ...`; verify by
  explicit run_id, never by newest-file inference.
- **Verification:** canonical commands are in `COMMANDS.md`; `make verify` is the
  full repository chain. Use focused checks during implementation and the full
  chain on the identified final candidate.
