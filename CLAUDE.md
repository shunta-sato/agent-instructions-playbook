# CLAUDE.md — Claude Code entry point

`AGENTS.md` is the canonical agent contract for this repository and is fully binding in Claude Code. Read it first and follow its Playbook bootstrap and mandatory workflow.

## Claude Code mapping

- **Skills**: `.claude/skills/<name>` are symlinks to `.agents/skills/<name>` (single source of truth; regenerate with `python scripts/sync_claude_skills.py --write`). Wherever playbook prose writes `$<skill>` or `/<skill>`, load `.agents/skills/<name>/SKILL.md` and apply its four-tier load contract: load `metadata.requires` before executing (unreadable ⇒ error); load `metadata.resources` only when its SKILL.md-stated condition matches; execute or cite `metadata.commands` by path, never inline; open `metadata.templates` only when producing that output artifact.
- **Delegation**: subagent task briefs (templates in `.agents/skills/execution-plans/templates/`) map to the Agent tool. Use the playbook-conformant custom agents in `.claude/agents/` (`playbook-worker`, `playbook-explorer`, `playbook-reviewer`) instead of ad-hoc prompts.
- **Model routing**: classify the task with `.agents/model-routing/task-classes.yml`, then use `.agents/model-routing/model-catalog.json` and `.agents/model-routing/route-lockfile.json` only after verifying both carry `harness: claude-code`. Never use their concrete model IDs from Codex, Copilot, or another harness. A missing or mismatched harness leaves the concrete model unresolved and forbids cross-harness fallback. After editing the Claude Code catalog, regenerate with `python scripts/generate_route_lockfile.py --write`.
- **Run evidence**: record every delegated run with `python3 scripts/agent_run.py record --harness claude-code ...`; `quality-gate` verifies delegated work by explicit run ID from `.agents/runs/agent-runs.jsonl`, never by success claims.
- **Verification**: canonical commands are in `COMMANDS.md`; `make verify` is the full chain.
