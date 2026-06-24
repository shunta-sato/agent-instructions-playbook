# ROS 2 Command Expert Skill - ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Add the `ros2-command-expert` skill from `ros2-command-expert.zip` on the feature branch `ros2-command-expert`.
- Keep the change out of `main` by committing and pushing only the feature branch.

## Scope

### In scope
- Extract `ros2-command-expert.zip` into `.agents/skills/ros2-command-expert/`.
- Add trigger eval seeds for the new skill.
- Regenerate `AGENTS.md` and `README.md` generated skill catalogs.
- Add workflow-contract review evidence for the new Agent-facing skill surface.
- Verify with repository canonical commands.

### Out of scope / non-goals
- Do not merge to `main`.
- Do not open a pull request unless requested separately.
- Do not change existing ROS 2, embedded, or concurrency skills.
- Do not commit unrelated untracked files already present in the worktree.

## Constraints / Quality targets

- Branching: branch name is exactly `ros2-command-expert` per user request.
- Compatibility: the skill must pass repo skill validation and generated index checks.
- Scope control: `ros2-command-expert.zip`, `.DS_Store`, and pre-existing untracked plan/report files are not in the staged branch scope.
- Operability: no runtime ROS 2 behavior changes; validation is repository metadata and catalog correctness.

## Context & Orientation

- Source archive: `ros2-command-expert.zip`.
- Target skill path: `.agents/skills/ros2-command-expert/`.
- Generated catalog paths: `AGENTS.md`, `README.md`.
- Eval path: `evals/skill-triggers/ros2-command-expert.json`.
- Workflow report path: `reports/workflow-contract-review/20260624-ros2-command-expert.md`.

## Design

### Boundary sketch

- `ros2-command-expert` owns source-backed ROS 2 Humble CLI command guidance for graph inspection, topic/service/action interaction, parameters, lifecycle, components, bag, launch, and security workflows.
- Existing `concurrency-ros2` remains responsible for ROS 2 executor/callback concurrency implementation guidance.
- Existing embedded NFR skills remain responsible for physical-footprint and target behavior claims.

### Complexity Budget

- Changed files target: 11 files plus generated index/catalog updates.
- New skill modules target: 1.
- New helpers/wrappers/adapters target: 0.
- New indirection layers target: 0.
- Production/test line budget: docs and eval seed only; no executable scripts.

### Testing strategy

- Validate skill metadata and trigger eval seeds.
- Validate skill inventory and generated catalogs.
- Run canonical `make verify`.
- Run `git diff --check`.

## Milestones

1. Inspect the zip and current git state without staging unrelated files.
2. Create the `ros2-command-expert` branch from `main`.
3. Extract and normalize the skill metadata for repo catalog use.
4. Add trigger evals and generated catalog updates.
5. Verify, commit, and push the feature branch.

## Progress (WBS)

- [x] (P0) Inspect source archive - deliverable: zip contents reviewed - verify: `unzip -l ros2-command-expert.zip`.
- [x] (P1) Create feature branch - deliverable: branch `ros2-command-expert` - verify: `git branch --show-current`.
- [x] (P2) Add skill files - deliverable: `.agents/skills/ros2-command-expert/` - verify: `find .agents/skills/ros2-command-expert -maxdepth 2 -type f`.
- [x] (P3) Add trigger evals - deliverable: `evals/skill-triggers/ros2-command-expert.json` - verify: `validate_skill_trigger_evals.py`.
- [x] (P4) Regenerate catalogs - deliverable: updated `AGENTS.md` and `README.md` - verify: `generate_agent_index.py --check`.
- [x] (P5) Verify and push - deliverable: verified feature branch ready to push - verify: `make verify`; push occurs after commit.

## Surprises & Discoveries

- 2026-06-24: The zip contains a complete skill package with `SKILL.md`, `agents/openai.yaml`, and five reference files.
- 2026-06-24: The original zip description validated but produced style warnings for length and procedure wording, so the branch shortens frontmatter metadata while preserving the skill body and references.

## Decision log

- 2026-06-24: Add the extracted skill contents rather than committing the zip as the feature artifact.
  - Options considered: commit only the zip, commit zip plus extracted skill, commit extracted skill.
  - Chosen: commit extracted skill.
  - Consequences: repo catalog and validators can discover the skill; the zip remains an untracked input artifact.
- 2026-06-24: Keep `agents/openai.yaml` from the package.
  - Options considered: remove product metadata to match current repo convention, preserve packaged metadata.
  - Chosen: preserve packaged metadata.
  - Consequences: no validator impact, and the skill package remains closer to the supplied archive.

## Handoff

- Current branch / commit: `ros2-command-expert`, uncommitted changes.
- What is done: zip inspected, branch created, skill extracted, trigger eval, plan, workflow-contract report, generated catalogs, and repository verification.
- What is not done: commit and push.
- How to run: `make verify`.
- How to test: `python3 scripts/validate_skills.py`, `python3 scripts/validate_skill_trigger_evals.py`, `python3 scripts/generate_agent_index.py --check`.
- Known risks / open questions: system `quick_validate.py` could not run in this environment because the `yaml` Python module is missing; repo validators cover the branch acceptance criteria.
- Next 1-3 steps: stage in-scope files only; commit; push branch `ros2-command-expert`.
- Pointers: `.agents/skills/ros2-command-expert/SKILL.md`, `.agents/skills/ros2-command-expert/references/`, `evals/skill-triggers/ros2-command-expert.json`.

## Validation & Acceptance

- AC1: Branch `ros2-command-expert` contains the extracted skill and support files.
  - Verification: `git status`, staged file list, pushed branch.
- AC2: `main` is not modified or pushed.
  - Verification: work occurs on branch `ros2-command-expert`; final push targets that branch.
- AC3: Repo validators pass.
  - Verification: `make verify`.
- AC4: New skill trigger boundaries are represented.
  - Verification: `evals/skill-triggers/ros2-command-expert.json` validates.

## Outcomes & Retrospective

- What shipped / merged: pending feature branch push; no merge to `main`.
- What went well: packaged skill contents were complete and repo validators accepted the added trigger evals and generated catalogs.
- What went wrong: system-level `quick_validate.py` depends on `yaml`, which is not installed in the active Python environment.
- Follow-ups / tech debt tickets: none for this branch.
