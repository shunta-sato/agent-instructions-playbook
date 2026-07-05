# Skill contract infrastructure (Phase 2, WS7+WS8) — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Close the remaining Phase 2 gaps from `reports/skillset-review-20260705.md` (GAP G5): partial-loading risk (skills read without their references) and missing output contracts, both silent quality losses for mid-tier models.
- WS8: a `metadata.requires` manifest in every SKILL.md frontmatter lists all files under the skill's `references/`, `templates/`, `scripts/` — generated and freshness-checked like the Agent Index. AGENTS.md bootstrap makes loading them mandatory.
- WS7: every skill must declare `## Output expectation`; enforced by `validate_skills.py` as an error.

## Scope

### In scope
- `scripts/update_skill_requires.py` (--write/--check, stdlib only) + unit tests + Makefile wiring (lint, test-integration).
- Generated `requires` manifests (45 skills with subdirectories).
- AGENTS.md bootstrap rule: listed files must be loaded before executing a skill; unreadable listed file is an error.
- `## Output expectation` sections added to the 11 skills lacking one (Sonnet 5 worker) + validator enforcement.

### Out of scope / non-goals
- Deep output-contract schemas (exact per-skill field validation) — possible later hardening.
- Phase 3 (`.claude/` wiring, model catalog/lockfile), Phase 4 (portfolio rebalance).

## Progress (WBS)

- [x] (P0) update_skill_requires.py + 6 unit tests — verify: unittest green, --check idempotent
- [x] (P0) 45 manifests generated; validate_skills.py still green
- [x] (P0) AGENTS.md bootstrap rule + Makefile wiring
- [x] (P1) Output expectation sections (11 skills) + validator enforcement — Sonnet 5 worker, diff-reviewed
- [x] (P2) make verify + PR

## Decision log

- 2026-07-05: `requires` is generated, not hand-written — hand-maintained manifests would drift exactly like the Copilot prompt mirror; freshness is CI-checked like the Agent Index.
- 2026-07-05: scope of `requires` = files under `references/`, `templates/`, `scripts/` only; cross-skill dependencies stay in prose (routing is dev-workflow's job, not the manifest's).
- 2026-07-05: `## Output expectation` enforced as exact case-sensitive heading — a checkable contract needs a checkable anchor.

## Surprises & Discoveries

- 2026-07-05: The worker found 15 pre-existing skills whose output sections used divergent headings (`## Outputs`, `## Output`, `## Output expectation (strict format...)`) and **escalated instead of editing outside its allowed-file list** — the delegation contract's scope boundary worked as designed. Supervisor normalized all headings to the canonical `## Output expectation` (vocabulary-consistency policy); `tonemana-catalog`'s second `## Output` section became `## Final response` to avoid a duplicate anchor.

## Handoff (update at every stop)

- Current branch: `skill-contract-infra`
- Next steps: PR review/merge; then Phase 3 (`.claude/` wiring + model catalog/lockfile).

## Validation & Acceptance

- AC1: `make verify` green, including the two new lint gates (requires freshness, output-expectation presence).
- AC2: manifests idempotent (`--write` twice → no diff; unit-tested).
- AC3: worker diff review — insert-only in the 11 skill bodies, no frontmatter touches.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: WS8 (45 generated `requires` manifests + generator/validator + AGENTS.md rule + Makefile gates) and WS7 (11 new output sections by Sonnet 5 worker + 15 heading normalizations by supervisor + validator enforcement). 51/51 skills pass; `make verify` green.
- What went well: worker escalated out-of-scope inconsistencies instead of improvising — second successful delegation under the task-brief pattern.
- What went wrong: nothing blocking; the heading divergence itself is more evidence for the glossary workstream (WS0b).
- Follow-ups / tech debt tickets: Phase 3 (`.claude/` wiring + model catalog/lockfile); WS0b glossary; per-skill output-field schemas (optional hardening).
