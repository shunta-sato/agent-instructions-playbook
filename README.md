# AI Agent Instructions Playbook

This repository is a template that provides software-development agents with thin always-on rules plus detailed playbooks read only when needed.

## Core files

- `AGENTS.md` — always-loaded core rules and the skill index
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

## Minimal bootstrap

1. Open `AGENTS.md` and review the `dev-workflow` and `quality-gate` flow.
2. If `COMMANDS.md` is uninitialized (`<fill>`), run `project-initialization`.
3. Before and after changes, verify with canonical commands defined in `COMMANDS.md`.
