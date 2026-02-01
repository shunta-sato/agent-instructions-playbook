# AI Agent Instructions Playbook (Codex + GitHub Copilot)

A reusable instruction set that works with:

- **OpenAI Codex** (`AGENTS.md` + `.codex/skills/…`)
- **GitHub Copilot (VS Code)** (`AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/…`, `.github/prompts/…`, and optional `.github/skills/…`)

This repo is designed around **thin always-on rules** and **thick on-demand playbooks**.
The on-demand playbooks use a “load details only when needed” mechanism (progressive disclosure):
- Codex loads only each skill’s `name`/`description` at startup; it reads the body only when a skill is invoked.
- VS Code Agent Skills load on demand in a similar way.

## Repository layout

Recommended layout (self-contained):

```

AGENTS.md
COMMANDS.md
.codex/skills/...
.github/
copilot-instructions.md
instructions/
prompts/
skills/        # optional (VS Code Agent Skills)
REFERENCES.md

```

If you want to use this repo as a template, keep the files at the root as above so both Codex and Copilot can discover them automatically.

## Quick start

### Codex
- Use `$dev-workflow` for any change.
- Finish with `$quality-gate`.
- When runtime behavior changes, use `$observability`.
- When introducing or changing concurrency/parallelism, invoke `$concurrency-core` and `$thread-safety-tooling` (plus `$concurrency-ros2` or `$concurrency-android` when relevant).

### Copilot (VS Code)

**Custom instructions**
- Repository-wide: `.github/copilot-instructions.md`
- Path-specific: `.github/instructions/*.instructions.md`

**Prompt files**
- Stored under `.github/prompts/` by default.
- Run them by typing `/` and the prompt name in chat (for example: `/dev-workflow`).

**Agent Skills (optional)**
- Stored under `.github/skills/` (recommended).
- Enable the `chat.useAgentSkills` setting in VS Code (preview) to use them.

## Canonical commands

`COMMANDS.md` is the single place to record how to build / format / lint / test the project.
If you use this repo as a template, replace the `<fill>` placeholders with real commands.

## Smells & anti-patterns triage

Use the `code-smells-and-antipatterns` playbook (Codex: `$code-smells-and-antipatterns`) to detect **new or worsened** design smells in a diff and propose the smallest fix.
It is recommended for structural changes (new modules, boundary changes, or refactors across layers) and is referenced by `dev-workflow` and `quality-gate`.

## Included skills

- `architecture-boundaries`
- `code-readability`
- `code-smells-and-antipatterns`
- `concurrency-android`
- `concurrency-core`
- `concurrency-ros2`
- `dev-workflow`
- `error-handling`
- `modularity`
- `nfr-iso25010`
- `observability`
- `quality-gate`
- `requirements-documentation`
- `requirements-to-design`
- `test-driven-development`
- `thread-safety-tooling`
- `working-with-legacy-code`

## Versioning

This repository follows Semantic Versioning (SemVer).
Skill renames are treated as breaking changes.

Generated: 2026-02-01
