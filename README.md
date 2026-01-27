# AI Agent Instructions Playbook (Codex + GitHub Copilot)

A reusable instruction set that works with:

- **OpenAI Codex** (`AGENTS.md` + `.codex/skills/…`)
- **GitHub Copilot (VS Code)** (`.github/copilot-instructions.md`, `.github/prompts/…`, and optional `.github/skills/…`)

This repo is designed around **thin always-on rules** and **thick on-demand playbooks** (progressive disclosure).  
Codex skills are only loaded in full when invoked; at startup, only `name`/`description` are visible.  
That keeps day-to-day context small while preserving detailed guidance when needed.

## Repository layout

Recommended layout (self-contained):

```
AGENTS.md
.codex/skills/...
.github/
  copilot-instructions.md
  instructions/
  prompts/
  skills/        # optional (VS Code agent skills)
REFERENCES.md
```

If you want to use this repo as a “template”, keep the files at the root as above so both Codex and Copilot can discover them automatically.

## Quick start

### Codex
- Use `$dev-workflow` for any change.
- Finish with `$quality-gate`.

### Copilot (VS Code)
- Copilot always reads `.github/copilot-instructions.md`.
- Use prompt files:
  - `/dev-workflow`
  - `/quality-gate`
  - `/review-readability`
  - `/review-modularity`
  - `/write-requirements`

## Included Codex skills

- `architecture-boundaries`
- `code-readability`
- `dev-workflow`
- `error-handling`
- `modularity`
- `nfr-iso25010`
- `observability`
- `quality-gate`
- `requirements-documentation`
- `requirements-to-design`
- `test-driven-development`
- `working-with-legacy-code`

## Versioning

This repository follows Semantic Versioning (SemVer).  
Skill renames are treated as breaking changes.

Generated: 2026-01-25
