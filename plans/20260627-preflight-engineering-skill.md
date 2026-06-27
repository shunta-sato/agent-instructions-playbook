# Preflight Engineering Skill — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Add a repository-local `preflight-engineering` skill that prepares Agent-facing context, routing maps, cache-readiness checks, subagent plans, and development commander handoff prompts before long-running work.
- The imported ChatGPT instruction file is the source request. The repo needs a concise, triggerable skill rather than a one-off instruction pasted into `AGENTS.md`.

## Scope

### In scope
- Create `.agents/skills/preflight-engineering/SKILL.md`.
- Create the required reference templates under `.agents/skills/preflight-engineering/references/`.
- Add an OAuth refresh token dry-run example.
- Regenerate the generated Agent index after adding the skill.
- Record workflow-contract and quality-gate evidence.

### Out of scope / non-goals
- No product implementation.
- No new executable helper scripts in the initial version.
- No broad cleanup of unrelated untracked files.
- No changes to generated index blocks by hand.

## Constraints / Quality targets

- Latency / throughput / resource budgets: not applicable; docs-only Skill addition.
- Safety/security/privacy: the skill must explicitly forbid reading or revealing secret values and must keep volatile/user-specific data out of stable prompt prefixes.
- Compatibility / rollout constraints: keep repo skill metadata valid and regenerate index via `scripts/generate_agent_index.py --write`.
- Operability: no runtime observability changes; verification is via repository validators and canonical commands.

## Implementation Economy

Complexity Budget:
- Changed files target: one new Skill directory, one trigger-eval file, generated index/catalog updates, one ExecPlan, one workflow contract report, and the imported request artifact.
- New classes/modules target: 0.
- New helpers/wrappers/adapters target: 0.
- New indirection layers target: 0.
- Rough production/test line budget: docs/templates/eval only; no executable production code.

Post-Implementation Economy Audit:

| New abstraction | Justification | Decision | Evidence |
| --- | --- | --- | --- |
| `preflight-engineering` Skill | Encapsulates a reusable pre-implementation workflow that would otherwise be pasted into prompts or `AGENTS.md` repeatedly. | keep | Valid skill metadata, 3 trigger eval cases, and `make verify` pass |
| Reference templates | Keep `SKILL.md` compact while preserving reusable AGENTS/context/skill-map/cache/handoff examples. | keep | Directly referenced from `SKILL.md`; total Skill body stays 132 lines |

## Context & Orientation

- Key paths / entry points: `.agents/skills/*/SKILL.md`, `.agents/skills/*/references/`, `scripts/validate_skills.py`, `scripts/generate_agent_index.py`, `COMMANDS.md`.
- Existing behavior: repo skills use concise `SKILL.md` files with optional `references/` and generated `AGENTS.md` / README catalogs.
- Conventions to follow: generated index is updated by script; skill body stays under 500 lines; detailed templates live in references.
- Unknowns (explicit): whether external reviewer approval will be granted on the first PR loop.

## Design

### Boundary sketch

- Components involved: new `preflight-engineering` Skill, six reference templates, generated Agent index, workflow contract report.
- Boundary crossings: no runtime UI/HTTP/DB/external service boundary changes.
- DTOs / interfaces: the Skill's output contract is the `# Preflight result` Markdown structure.
- Error handling strategy: validators catch malformed frontmatter, missing required fields, stale generated indexes, and broken command chains.

### Observability

- Logs: not applicable; no runtime behavior.
- Metrics: not applicable.
- Traces: not applicable.

### Testing strategy

- Unit tests: `python3 scripts/validate_skills.py`.
- Integration tests: canonical `make verify`.
- Stress / concurrency tests: not applicable.
- Manual verification: review skill acceptance criteria against the imported request.

## Milestones (high-level plan)

1. Inventory request, repo skill conventions, validators, and required workflow branches.
2. Implement the new Skill and reference templates from the imported request.
3. Regenerate generated indexes and run validation.
4. Publish the feature branch and PR, request external review in the prior ChatGPT thread, and post the review result to the PR.
5. React to approval or requested changes.

## Progress (WBS)

Use a checkbox list. Each item should have a concrete deliverable and verification note.

- [x] (P0) Branch setup and source request import — deliverable: `codex/preflight-engineering-skill` plus `reports/imported-chatgpt/20260627-preflight-engineering-skill-request.md` — verify: `git status --short --branch`.
- [x] (P1) Planning and risk routing — deliverable: this ExecPlan with normal-risk route and implementation-economy budget — verify: plan sections are filled.
- [x] (P2) Skill implementation — deliverable: `preflight-engineering` Skill, references, and trigger evals — verify: acceptance criteria self-review and `python3 scripts/validate_skills.py`.
- [x] (P3) Generated index and validation — deliverable: regenerated index and green canonical checks — verify: `make verify`.
- [ ] (P4) PR and review loop — deliverable: PR to `main`, ChatGPT-thread review request, PR review-result comment — verify: PR URL and posted comment.

## Surprises & Discoveries

Record unexpected constraints, gotchas, and newly learned facts (with evidence when possible).

- 2026-06-27: Existing worktree has unrelated untracked files. Stage only files created or updated for this request.
- 2026-06-27: The system skill scaffold creates `agents/openai.yaml`, but this repo's source skill convention and requested file layout do not include per-skill `agents/` metadata. Remove the scaffolded file and keep repo-local metadata in `SKILL.md`.
- 2026-06-27: Initial verification warned that `preflight-engineering` had no trigger eval coverage. Added `evals/skill-triggers/preflight-engineering.json`, and the warning disappeared on the next `make verify`.

## Decision log

Record decisions and trade-offs (and why).

- 2026-06-27: Keep the first version instruction-only because the imported request explicitly says scripts are optional and the core value is a reusable Agent workflow.
  - Options considered: add helper scripts now; add only `SKILL.md` and references.
  - Chosen: add only `SKILL.md` and references.
  - Consequences: lower implementation risk; future script automation can be added after the workflow stabilizes.
- 2026-06-27: Store detailed examples in references rather than `SKILL.md` because repo skills use progressive disclosure and `SKILL.md` must stay compact.
  - Options considered: paste the full request into `SKILL.md`; split templates into references.
  - Chosen: split templates into references.
  - Consequences: easier triggering and lower context cost.

## Handoff (update at every stop)

- Current branch / commit: `codex/preflight-engineering-skill`, commit pending.
- What is done: branch created, source request imported, Skill files added, trigger evals added, generated index/catalog updated, workflow contract report drafted, `make verify` passed.
- What is not done: commit, push, PR creation, external review loop, merge decision.
- How to run: `python3 scripts/validate_skills.py`; `python3 scripts/generate_agent_index.py --check`; `make verify`.
- How to test: run canonical commands from `COMMANDS.md`.
- Known risks / open questions: external review may request narrower wording or additional examples.
- Next 1–3 steps: run quality gate; commit and push; create PR and request review in the prior ChatGPT thread.
- Pointers (files/dirs to read first): `.agents/skills/preflight-engineering/`, `reports/imported-chatgpt/20260627-preflight-engineering-skill-request.md`, `COMMANDS.md`.

## Validation & Acceptance

List the measurable acceptance criteria and how they are verified.

- AC1: Skill exists with valid `name` and trigger-rich `description`.
  - Verification: `python3 scripts/validate_skills.py`.
- AC2: Skill workflow covers inventory, risk classification, invariant extraction, routing, `AGENTS.md`, Agent context docs, skill routing, cache readiness, subagent plan, and handoff prompt.
  - Verification: self-review against imported request.
- AC3: References include required templates and OAuth refresh token example.
  - Verification: file list and content review.
- AC4: Generated Agent index is current.
  - Verification: `python3 scripts/generate_agent_index.py --check`.
- AC5: Canonical verification passes.
  - Verification: `make verify` passed on 2026-06-27.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: pending.
- What went well: pending.
- What went wrong: pending.
- Follow-ups / tech debt tickets: pending.
