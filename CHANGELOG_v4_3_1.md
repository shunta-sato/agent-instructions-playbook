# CHANGELOG v4.3.1

## Highlights
- Migrated Codex skills path from `.codex/skills` to `.agents/skills` as the repository source of truth.
- Added `scripts/sync_agent_skills.py` to sync `.agents/skills` into `.github/skills` (write/check modes).
- Updated CI to enforce skills sync before AGENTS index checks.
- Updated AGENTS/README/Copilot instructions and regenerated the AGENTS index for the new layout.
