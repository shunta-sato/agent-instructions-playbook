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
- When UI code changes, invoke `$visual-regression-testing` and the matching platform skill (`$visual-regression-ios|android|web`) and produce a UI Visual Verification Report.
- When introducing or changing concurrency/parallelism, invoke `$concurrency-core` and `$thread-safety-tooling` (plus `$concurrency-ros2` or `$concurrency-android` when relevant).
- When fixing bugs/regressions/flakes/crashes/hangs, invoke `$bug-investigation-and-rca` before implementation and produce the Bug Report (RCA).

### Copilot (VS Code)

**Custom instructions**
- Repository-wide: `.github/copilot-instructions.md`
- Path-specific: `.github/instructions/*.instructions.md`

**Prompt files**
- Stored under `.github/prompts/` by default.
- Run them by typing `/` and the prompt name in chat (for example: `/dev-workflow`).
- Use `/bug-report` for bugfix/regression/flaky/incidents to generate the deterministic Bug Report template.

**Agent Skills (optional)**
- Stored under `.github/skills/` (recommended).
- Enable the `chat.useAgentSkills` setting in VS Code (preview) to use them.

## Maintaining the AGENTS.md index

This repo embeds a generated, compressed playbook index into `AGENTS.md` so agents can find the right files without needing to “decide” to load a skill.

After editing any of these:
- `.codex/skills/**`
- `.github/skills/**`
- `.github/prompts/**`
- `.github/instructions/**`

Run:

```bash
python scripts/generate_agent_index.py --write
```

CI will fail if the index is out of date.

## Canonical commands

`COMMANDS.md` is the single place to record how to build / format / lint / test the project.
If you use this repo as a template, replace the `<fill>` placeholders with real commands.

## Smells & anti-patterns triage

Use the `code-smells-and-antipatterns` playbook (Codex: `$code-smells-and-antipatterns`) to detect **new or worsened** design smells in a diff and propose the smallest fix.
It is recommended for structural changes (new modules, boundary changes, or refactors across layers) and is referenced by `dev-workflow` and `quality-gate`.

## UI visual verification contract

When UI changes are in scope, this repository expects one canonical verification interface:

- Make-based contract: `make ui-verify`, `make ui-record`, optional `make ui-artifacts`; or
- Script-based contract: `./tools/ui/verify.sh`, `./tools/ui/record.sh`.

Agents should discover which option the repository exposes, execute it, review visual diffs against requested/design-intent behavior, and update baselines only for intentional changes.

Required output:

```markdown
## UI Visual Verification Report
- Platform: ios|android|web
- Environment: OS + key tool versions
- Command(s) executed:
- Snapshot output path(s):
- Baseline updated?: yes|no
- Review summary:
  - If diff: why accepted or what to fix
  - If cannot run: why + how CI should cover it
```

## Included skills

- `architecture-boundaries`
- `bug-investigation-and-rca`
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
- `visual-regression-android`
- `visual-regression-ios`
- `visual-regression-testing`
- `visual-regression-web`
- `working-with-legacy-code`

## Versioning

This repository follows Semantic Versioning (SemVer).
Skill renames are treated as breaking changes.

Generated: 2026-02-01

## Bugfix mode triggers (required)

Use bugfix mode (via `$dev-workflow` + `$bug-investigation-and-rca`) when tasks mention bug/regression/flaky/crash/hang/incident, when behavior-level test failures are being fixed, or when workaround-only mitigation is considered. Paste the resulting Bug Report (RCA) in the PR description, issue comment, or a tracked docs file.
