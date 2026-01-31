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
- When introducing or changing concurrency/parallelism, invoke `$concurrency-core` and `$thread-safety-tooling` (plus `$concurrency-ros2` or `$concurrency-android` when relevant).

### Copilot (VS Code)
- Copilot always reads `.github/copilot-instructions.md`.
- Use prompt files:
  - `/dev-workflow`
  - `/quality-gate`
  - `/review-antipatterns`
  - `/review-readability`
  - `/review-modularity`
  - `/write-requirements`

## Smells & anti-patterns triage

Use `$code-smells-and-antipatterns` to detect **new or worsened** design smells in a diff and propose the smallest fix.  
It is **mandatory for structural changes** (new modules, boundary changes, or refactors across layers) and is recorded in `$dev-workflow` and enforced in `$quality-gate`.

## Included Codex skills

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

Generated: 2026-01-25
