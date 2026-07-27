# Repo Inspection Output Template

Use this template to summarize read-only helper output before `preflight-engineering`
turns it into proposals. The scripts collect candidates only; the skill or human
operator owns every decision.

## Commands

```sh
python3 .agents/skills/preflight-engineering/scripts/inspect_repo.py --root . --markdown
python3 .agents/skills/preflight-engineering/scripts/estimate_context_size.py --root .
python3 .agents/skills/preflight-engineering/scripts/check_agent_docs.py --root .
```

## Collector Boundary

- Confirmed facts are paths, files, and command surfaces actually present in the repository.
- Inferred facts are candidates derived from structure, naming, or package-manager files.
- Unknowns require human or maintainer confirmation before they become instructions.
- Secret-like paths may be listed as paths only. Secret values must not be opened, copied, summarized, or embedded in context docs.

## Repo Inspection Summary

### Confirmed

- Instruction files:
- Agent context:
- LLM Wiki index (`.agent/wiki/index.md`, if present):
- Skill files:
- Docs:
- Commands:
- Risk-surface paths:
- Generated paths:
- Migration paths:
- Secret-like paths (path only):

### Inferred

- Package manager candidates:
- Test command candidates:
- Domain preflight candidates:
- Nested `AGENTS.md` candidates:

### Unknown

- Missing docs or unclear ownership:
- Test routing gaps:
- Approval/reviewer gaps:
- Context-size risks:

## Human Decisions Required

- Decide whether the root `AGENTS.md` should change.
- Decide which nested `AGENTS.md` proposals are worth creating.
- Confirm domain skills to run after risk classification.
- Confirm targeted test commands before implementation starts.

## Integration Notes

- Merge confirmed facts into AGENTS/context proposals only after review.
- Keep root `AGENTS.md` compact and stable.
- Move area-specific rules into nested `AGENTS.md` files.
- Keep `.agent/ctx/<domain>.md` maps short, readable, and auditable.

## LLM Wiki Inventory

- If `.agent/wiki/index.md` exists, inventory it as the project-knowledge entry point.
- Read only the entries whose scope matches the task's paths or components — never load the whole wiki.
- Reference relevant entries from `.agent/ctx` maps or the work-routing map; do not restate their content there.
- Never copy Wiki entry bodies into `AGENTS.md`.
