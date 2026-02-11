# CHANGELOG v4.2.2

## Added

- New `bug-investigation-and-rca` skill in both `.codex/skills/` and `.github/skills/`, including:
  - deterministic Bug Report (RCA) output format,
  - anti-cheat evidence-first workflow,
  - references with Five Whys, prevention taxonomy, and tool selection matrix,
  - optional standalone bug report template.
- New Copilot prompt: `.github/prompts/bug-report.prompt.md`.

## Updated

- `dev-workflow` (Codex + GitHub skills): added conditional Bugfix mode enforcement before implementation.
- `quality-gate` (Codex + GitHub skills): added required bugfix evidence/report checklist and workaround-only guardrails.
- Docs updated in `AGENTS.md`, `README.md`, `.github/copilot-instructions.md`, and `REFERENCES.md` for triggers and usage guidance.
