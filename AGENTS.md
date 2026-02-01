# AGENTS.md — AI agent core instructions

This repository is a reusable playbook for software-development agents.

Keep this file short. Put detailed guidance in the on-demand playbooks under:
- `.codex/skills/<name>/SKILL.md` (Codex skills)
- `.github/skills/<name>/SKILL.md` (Agent Skills)
- `.github/prompts/<name>.prompt.md` (VS Code prompt files)

## Goals
- Make changes easy to understand (readability).
- Keep changes localized (cohesion / coupling / boundaries).
- Keep requirements verifiable after the fact (docs + tests).

## Always-on principles
- Prefer the smallest change that satisfies the requirement.
- No large cleanups. Leave touched code slightly easier to read than before.
- If runtime behavior changes, add observability (logs/metrics/traces) so failures are diagnosable.

## Mandatory workflow for code/test changes
1) Apply the `dev-workflow` playbook end-to-end before editing.
2) Before finishing, apply the `quality-gate` playbook and address findings.

### How to run a playbook (depends on your tool)
- OpenAI Codex: invoke a skill with `$<skill-name>` (for example `$dev-workflow`, `$quality-gate`, `$observability`). You can also use `/skills` to browse skills.
- VS Code prompt files: type `/` then the prompt name (for example `/dev-workflow`, `/quality-gate`).
- Agent Skills (VS Code / compatible agents): skills in `.github/skills/` load on demand when relevant.

## Language/path-specific rules
- Follow `.github/instructions/*.instructions.md` when present.
- C++: `.github/instructions/cpp.instructions.md` is mandatory for `**/*.{h,hpp,hh,hxx,cpp,cc,cxx}`.

## Verification commands
Use the canonical commands in `COMMANDS.md` (build, format/lint, tests).
If you cannot run a command, state why and provide a reproducible procedure.

## Required final response format
Return, in this order:
1) Change Brief (what/why, scope, assumptions, risks)
2) What changed (files + intent)
3) Verification (commands + results; or what you could not run)
4) Follow-ups (optional)
