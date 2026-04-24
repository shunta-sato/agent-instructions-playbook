# AI Agent Instructions Playbook

This repository is a template that provides software-development agents with thin always-on rules plus detailed playbooks read only when needed.

## Core files

- `AGENTS.md` — always-loaded core rules and the skill index
- `.agents/skills/*/SKILL.md` — single source of repo-local Agent Skills for Codex and GitHub Copilot
- `.github/prompts/*.prompt.md` — Copilot prompt files for explicit chat workflows
- `COMMANDS.md` — canonical build / lint / test commands
- `PLANS.md` — guide for ExecPlan operations
- `README.md` — repository overview and minimum onboarding
- `REFERENCES.md` — entry point for reference documents

## Core runtime skills（short list）

- `dev-workflow` — route change risk and execute only required branches
- `quality-gate` — final decision before submission
- `execution-plans` — execution planning for complex/long-running tasks
- `requirements-to-design` — convert requirements into implementable design input
- `project-initialization` — initialize the command system

For the full skill list and usage workflow, see `AGENTS.md` and each `SKILL.md`.

## Skill layout

Project skills live only under `.agents/skills`. Do not mirror them into `.github/skills`; current Codex and GitHub Copilot both support `.agents/skills` as a project-skill location.

Use `$skill-name` in Codex and `/skill-name` in GitHub Copilot CLI / agent mode when explicit invocation is needed. Keep short, always-on rules in `AGENTS.md`; move detailed procedures, examples, and templates into skills, `references/`, or `templates/`.

## Validation

Run these after changing skills or the agent index:

- `python scripts/validate_skills.py`
- `python scripts/generate_agent_index.py --check`

## Minimal bootstrap

1. Open `AGENTS.md` and review the `dev-workflow` and `quality-gate` flow.
2. If `COMMANDS.md` is uninitialized (`<fill>`), run `project-initialization`.
3. Before and after changes, verify with canonical commands defined in `COMMANDS.md`.
