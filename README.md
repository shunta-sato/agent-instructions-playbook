# AI Agent Instructions Playbook

This repository is a reusable playbook for software-development agents.
It keeps always-on rules thin and operational detail in on-demand skill docs.

## What this repo is

A shared instruction baseline for agent-driven development workflows:

- repo-level policy and defaults (`AGENTS.md`)
- canonical verification commands (`COMMANDS.md`)
- planning/traceability conventions (`PLANS.md`, `plans/`)
- skill and prompt packages for tool-specific runtimes (`.agents/skills`, `.github/skills`, `.github/prompts`)

## Core files

- `AGENTS.md`
- `COMMANDS.md`
- `PLANS.md`
- `plans/README.md`
- `REFERENCES.md`
- `.agents/skills/`
- `.github/skills/`
- `.github/prompts/`
- `.github/instructions/`

## Core runtime skills (short list)

- `dev-workflow`
- `quality-gate`
- `execution-plans`
- `requirements-to-design`
- `observability`

## Minimal bootstrap

1. Read `AGENTS.md` for always-on rules and mandatory workflow.
2. Read `COMMANDS.md` for canonical verify/build/lint/test commands.
3. Start changes with `dev-workflow`; finish with `quality-gate`.
