# ROS 2 Command Expert Execution Contract Upgrade — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Upgrade `ros2-command-expert` from a large ROS 2 CLI knowledge pack into an execution-contract skill that classifies command risk, loads only necessary references, preserves exact task names, records evidence, and uses evals to prevent known failure modes.
- Keep the `ros2-command-expert` branch as the base branch for this work; do not merge these changes directly to `main`.

## Scope

### In scope

- Rework `.agents/skills/ros2-command-expert/SKILL.md` into a workflow-focused execution gate.
- Add risk gate, answer/evidence contract, source provenance, neighbor-skill fallback, and command-plan templates across focused PRs.
- Add trigger, behavior, and model-routing eval coverage for ROS 2 command workflows.
- Preserve existing command catalog content in references rather than expanding it.
- Run repository validation for each PR and request review with a direct PR URL.

### Out of scope / non-goals

- Do not add OpenTelemetry, external model APIs, web-search graders, or natural-language graders.
- Do not claim full ROS 2 distro coverage beyond Humble without installed help verification.
- Do not build an automatic mutating-command executor for robots or production environments.
- Do not complete a standalone `fastdds-shm-triage` skill in this upgrade; provide a safe fallback instead.
- Do not stage unrelated local files already present in the worktree.

## Constraints / Quality targets

- Safety/security/privacy: mutating, robot-affecting, filesystem, and security commands require command plans, validation, and approval boundaries.
- Compatibility / rollout constraints: PRs target base branch `ros2-command-expert`; each feature branch must be reviewed before merge.
- Operability: executed-command guidance must record environment, command intent, risk class, stdout/stderr artifacts, exit code, validation, and claim boundary.
- Skill quality: `validate_skills.py` must emit no description-style flags for `ros2-command-expert`.
- Eval quality: trigger and behavior evals must cover concrete-name preservation, daemon restart avoidance, bounded execution, mutating validation, SHM/no-log claim boundaries, and token telemetry non-blocking behavior.

## Context & Orientation

- Skill entry point: `.agents/skills/ros2-command-expert/SKILL.md`.
- Existing references: `.agents/skills/ros2-command-expert/references/`.
- New templates: `.agents/skills/ros2-command-expert/templates/`.
- Existing trigger eval: `evals/skill-triggers/ros2-command-expert.json`.
- New behavior eval: `evals/skill-behavior/ros2-command-expert.json`.
- Later model-routing eval: `evals/model-routing/ros2-command-expert.json`.
- Canonical validation: `make verify`; repo also exposes build/lint/test targets in `COMMANDS.md`.
- Unknowns: GitHub review comments may re-slice the work; keep each PR small enough to update safely.

## Design

### Boundary sketch

- `SKILL.md` owns execution flow: when to use the skill, risk classification, reference routing, concrete-name extraction, propose-vs-run decision, evidence requirements, traps, and output expectations.
- `references/task-index.md` and `references/command-map.md` own command selection and exact command syntax.
- `references/execution-patterns.md` owns safe recipes for bounded observations, tmux/timeout/Python fallbacks, `/rosout`, and long-running commands.
- `references/risk-gates.md` owns the five-class operation risk model.
- `templates/*.md` own reusable command-plan and execution-record formats for humans, agents, and future strict workers.
- Evals own routing and behavior expectations; they do not run ROS 2 or grade model prose automatically.

### Implementation Economy

- Changed files per PR target: 6-12.
- New code modules target: 0.
- New helpers/wrappers/adapters target: 0.
- New indirection layers target: 0.
- Production/test line budget: Markdown and JSON seed changes only; no executable script changes in PR A unless validation schema demands it.

### Testing strategy

- Run skill validators after each PR slice.
- Run trigger and behavior eval validators after eval changes.
- Run model-routing validators only in the model-routing PR.
- Run `python3 scripts/generate_agent_index.py --check` when frontmatter or catalog-affecting metadata changes.
- Run `make verify` before submitting each PR.

## Milestones

1. PR A: Compress `SKILL.md` into an execution gate, add risk gates/templates, and seed trigger/behavior evals for the most dangerous failure modes.
2. PR B: Add answer contract, neighbor-skill fallback, and source provenance claim boundaries if not completed in PR A.
3. PR C: Tighten source-backed command-map and implementation-note provenance without expanding command catalog scope.
4. PR D: Expand behavior evals to at least 10 cases covering hidden flags, `/rosout`, SHM, bounded commands, filesystem/security path protection, and non-Humble verification.
5. PR E: Add strict worker task brief and model-routing task classes/evals for command lookup, readonly diagnosis, and mutating operation planning.
6. Merge each PR only after GitHub review approval and required checks pass, then sync `ros2-command-expert` and continue.

## Progress (WBS)

- [x] (P0) Read GOAL and establish branch policy — deliverable: active goal + base branch rule — verify: current branch created from `origin/ros2-command-expert`.
- [x] (P1) Create PR A feature branch — deliverable: `codex/ros2-command-expert-contract-pr-a` — verify: `git branch --show-current`.
- [x] (P2) Create PR A execution-contract files — deliverable: compressed `SKILL.md`, `risk-gates.md`, command/execution templates — verify: line count and content review.
- [x] (P3) Add PR A eval coverage — deliverable: trigger eval updates and 5+ behavior eval cases — verify: eval validators.
- [x] (P4) Add workflow-contract review report — deliverable: `reports/workflow-contract-review/<slug>.md` with decision `submit` — verify: quality-gate artifact check.
- [x] (P5) Verify PR A — deliverable: green repository validation — verify: `make verify`.
- [ ] (P6) Publish and request review — deliverable: PR URL sent to reviewer channel — verify: GitHub PR exists and review request sent.
- [ ] (P7) Review loop — deliverable: PR A merged into `ros2-command-expert` after approval — verify: merge SHA and synced base branch.

## Surprises & Discoveries

- 2026-06-24: `SKILL.md` is 253 lines and already contains many command recipes that duplicate reference content.
- 2026-06-24: Existing behavior eval schema is seed-only JSON and supports the requested `expected_decision`, `expected_findings`, and `expected_output_contains` fields.
- 2026-06-24: After PR A edits, `SKILL.md` is 129 lines, `ros2-command-expert` has 8 references, 2 templates, and 7 trigger eval references.

## Decision log

- 2026-06-24: Treat this as high-risk agent-facing workflow work.
  - Options considered: low-risk docs edit, normal-risk skill edit, high-risk workflow contract change.
  - Chosen: high-risk workflow contract change.
  - Consequences: require ExecPlan, implementation-economy budget, workflow-contract review report, full verification, and quality gate.
- 2026-06-24: Start with a combined PR A minimum slice.
  - Options considered: pure description cleanup only, PR A from the proposed split, the smaller "first minimum GOAL" package.
  - Chosen: first minimum GOAL package.
  - Consequences: first PR includes description, compressed execution gate, risk gates/templates, trigger eval, and 5 behavior eval cases.

## Post-Implementation Economy Audit

| New abstraction | Justification | Decision | Evidence |
| --- | --- | --- | --- |
| New code abstraction | None added. | keep none | Diff is Markdown/JSON skill, reference, template, and eval seed changes only. |
| `risk-gates.md` reference | Separates execution risk classification from command catalog so future command syntax edits do not weaken safety gates. | keep | `SKILL.md` references it before proposed/executed command planning. |
| `command-plan.md` and `execution-record.md` templates | Make concrete-name extraction, approval, validation, artifacts, and claim boundary reusable for agents and future workers. | keep | Behavior evals check command-plan expectations and validation requirements. |

## Handoff

- Current branch / commit: `codex/ros2-command-expert-contract-pr-a`, uncommitted changes.
- What is done: GOAL read, base branch synced, feature branch created, ExecPlan started, PR A execution-contract files, eval seeds, workflow-contract report, `make build-release`, `make verify`, and quality gate.
- What is not done: commit, PR creation, review request, review loop.
- How to run: `make verify`.
- How to test: `python3 scripts/validate_skills.py`; `python3 scripts/validate_skill_trigger_evals.py`; `python3 scripts/validate_skill_behavior_evals.py`; `python3 scripts/generate_agent_index.py --check`.
- Known risks / open questions: source provenance and model routing may need later PRs to avoid overloading PR A.
- Next 1-3 steps: stage in-scope files; commit/push/open PR; request review.
- Pointers: `.agents/skills/ros2-command-expert/SKILL.md`, `.agents/skills/ros2-command-expert/references/task-index.md`, `evals/skill-triggers/ros2-command-expert.json`.

## Validation & Acceptance

- AC1: `ros2-command-expert` description is trigger-only and under 420 characters.
  - Verification: `python3 scripts/validate_skills.py`; manual description length check.
- AC2: `SKILL.md` is workflow-focused rather than a duplicated command catalog.
  - Verification: line count and review of retained sections.
- AC3: ROS 2 CLI command execution flows through a five-class risk gate before propose/run decisions.
  - Verification: `references/risk-gates.md` plus `SKILL.md` required flow.
- AC4: Command plans and execution records capture concrete names, risk, command, validation, evidence, and stop conditions.
  - Verification: templates exist and are referenced from `SKILL.md`.
- AC5: Trigger and behavior evals cover the first known failure modes.
  - Verification: trigger/behavior eval validators pass.
- AC6: Each PR is reviewed and merged into `ros2-command-expert` before the next PR starts.
  - Verification: GitHub PR approval, merge result, and synced local base branch.

## Outcomes & Retrospective

- What shipped / merged: pending PR A publication.
- What went well: `SKILL.md` was reduced from 253 to 129 lines while keeping command details in references; validators accept the new behavior eval file.
- What went wrong: none observed in PR A implementation.
- Follow-ups / tech debt tickets: later PRs still need source provenance expansion, additional behavior evals, model-routing task classes, and strict worker brief.
