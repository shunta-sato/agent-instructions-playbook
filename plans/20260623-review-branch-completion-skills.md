# Review and Branch Completion Skills - ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Complete PR7 of the Superpowers improvement sequence by adding repo-local skills for review request packaging, review feedback handling, and branch/PR lifecycle completion.
- Make the review loop explicit without moving submit readiness out of `quality-gate`.

## Scope

### In scope
- Add `.agents/skills/requesting-code-review/SKILL.md`.
- Add `.agents/skills/receiving-code-review/SKILL.md`.
- Add `.agents/skills/branch-completion/SKILL.md`.
- Add trigger eval seeds for the new review lifecycle skills.
- Update generated Agent Index and README skill catalog.
- Add workflow-contract review evidence for the new Agent-facing workflow surfaces.

### Out of scope / non-goals
- No GitHub API wrapper or review automation script in this PR.
- No change to `quality-gate` submit criteria.
- No change to model routing, run ledger, or behavior eval validators.

## Constraints / Quality targets

- Latency / throughput / resource budgets: not applicable; docs/eval seed change only.
- Safety/security/privacy: branch completion must preserve unrelated local changes and avoid destructive cleanup without explicit authorization.
- Compatibility / rollout constraints: new skills must validate with existing skill metadata, trigger eval, inventory, and generated index checks.
- Operability: review and completion records must include PR URL, verification, and git state evidence.

## Context & Orientation

- Key paths:
  - `.agents/skills/*/SKILL.md`
  - `evals/skill-triggers/*.json`
  - `scripts/generate_agent_index.py`
  - `reports/workflow-contract-review/`
- Existing behavior:
  - `quality-gate` owns final submit/no-submit decisions.
  - `dev-workflow` routes implementation work before edits.
  - Agent Index and README catalog are generated from `.agents/skills`.
- Conventions to follow:
  - Keep descriptions trigger-focused and under the recommended length.
  - Keep `SKILL.md` bodies concise.
  - Use generated index tooling rather than hand-editing generated blocks.
- Unknowns:
  - None blocking; no runtime API behavior is introduced.

## Design

### Boundary sketch

- `requesting-code-review`: packages PR/diff scope, verification, reviewer focus, and known risks. It does not decide readiness.
- `receiving-code-review`: reads review comments/reviews/threads and assigns dispositions: accept, refute, defer, clarify, or acknowledge. It does not blindly apply suggestions.
- `branch-completion`: checks git/review/CI state and chooses merge, publish PR, keep, discard, or cleanup. It preserves unrelated local changes.

### Responsibility Map

| Unit | Name | Responsibility sentence | Reason to change | Dependency direction |
| --- | --- | --- | --- | --- |
| Skill | `requesting-code-review` | Prepare focused review requests from an existing PR or diff and verification evidence. | Review-request packaging expectations change. | Depends on `quality-gate` output as evidence; no reverse dependency. |
| Skill | `receiving-code-review` | Process received review feedback with explicit dispositions and evidence. | Review feedback handling policy changes. | May hand off approvals to `branch-completion`; does not depend on its implementation. |
| Skill | `branch-completion` | Finish branch or PR lifecycle decisions after verification/review. | Merge, publish, discard, or cleanup policy changes. | Depends on git/PR/check state; consumes approval evidence from review handling. |
| Eval seed | `review-branch-completion.json` | Capture trigger boundaries for the three new skills. | Trigger expectations change. | Consumed by `validate_skill_trigger_evals.py`. |

Layout decision: keep three separate skills because request packaging, feedback judgment, and branch lifecycle have different reasons to change. Rejected alternatives: one combined review skill would blur readiness, feedback disposition, and merge cleanup; adding scripts would add indirection without deterministic behavior to automate in this PR.

### Complexity Budget

- Changed files target: 8 files plus generated catalog/index updates.
- New classes/modules target: 3 skill modules and 1 eval seed file.
- New helpers/wrappers/adapters target: 0.
- New indirection layers target: 0.
- Rough production/test line budget: docs/eval only; no executable production code.

### Observability

- Not applicable; no runtime behavior changes.

### Testing strategy

- Unit tests: no repository-local unit tests configured.
- Integration tests: run skill metadata, trigger eval, behavior eval, model routing, inventory, generated index, and diff whitespace checks through `make verify`.
- Manual verification: inspect generated Agent Index and README catalog diffs for the new skills.

## Milestones (high-level plan)

1. Read existing skill/eval conventions and route required workflow branches.
2. Add the three new skills with strict responsibility boundaries.
3. Add trigger eval seeds that prove positive and negative routing cases.
4. Regenerate Agent Index and README skill catalog.
5. Run validators, workflow-contract review, quality gate, and publish PR.

## Progress (WBS)

- [x] (P0) Route implementation work - deliverable: dev-workflow/design-balance/implementation-economy route - verify: plan records route.
- [x] (P1) Create new skill skeletons - deliverable: three skill folders initialized - verify: `init_skill.py` succeeded.
- [x] (P2) Author skill bodies - deliverable: three concise `SKILL.md` files - verify: `validate_skills.py`.
- [x] (P3) Add trigger eval seed - deliverable: `evals/skill-triggers/review-branch-completion.json` - verify: `validate_skill_trigger_evals.py`.
- [x] (P4) Regenerate indexes - deliverable: updated `AGENTS.md` and `README.md` generated blocks - verify: `generate_agent_index.py --check`.
- [x] (P5) Final verification - deliverable: green canonical checks - verify: `make verify`.
- [x] (P6) PR publication - deliverable: PR URL and review request - verify: GitHub PR created at https://github.com/shunta-sato/agent-instructions-playbook/pull/67; reviewer request pending in ATLAS.

## Surprises & Discoveries

- 2026-06-23: Existing repo-local skills do not include `agents/openai.yaml`; generated product metadata from `init_skill.py` was removed to keep repo convention unchanged.

## Decision log

- 2026-06-23: Keep `requesting-code-review`, `receiving-code-review`, and `branch-completion` as separate skills.
  - Options considered: one combined review lifecycle skill, two skills split at review/branch boundary, three skills.
  - Chosen: three skills.
  - Consequences: clearer trigger boundaries and less overlap with `quality-gate`; slightly more catalog entries.
- 2026-06-23: Do not add helper scripts.
  - Options considered: markdown-only skills, GitHub CLI helper scripts.
  - Chosen: markdown-only skills.
  - Consequences: keeps PR7 scoped to workflow contracts; GitHub automation remains client/tool specific.

## Handoff (update at every stop)

- Current branch / commit: `codex/review-branch-completion-skills`, uncommitted PR publication update.
- What is done: skill skeletons created; skill content, trigger eval, ExecPlan, workflow-contract report, generated index/catalog, canonical verification, and draft PR publication.
- What is not done: ATLAS review request.
- How to run: `make verify`.
- How to test: `python3 scripts/validate_skills.py`, `python3 scripts/validate_skill_trigger_evals.py`, `python3 scripts/generate_agent_index.py --check`.
- Known risks / open questions: `quick_validate.py` from the system skill could not run under default `python3` because `yaml` is missing; repo validators cover the submitted skill metadata.
- Next 1-3 steps: commit and push this PR URL update; request review through ATLAS; monitor GitHub review comments.
- Pointers: `.agents/skills/requesting-code-review/SKILL.md`, `.agents/skills/receiving-code-review/SKILL.md`, `.agents/skills/branch-completion/SKILL.md`, `evals/skill-triggers/review-branch-completion.json`.

## Validation & Acceptance

- AC1: `quality-gate` and `requesting-code-review` responsibilities do not overlap.
  - Verification: skill body boundary section and trigger eval negative case.
- AC2: `receiving-code-review` does not blindly accept review comments.
  - Verification: dispositions include accept/refute/defer/clarify/acknowledge and trigger eval covers disputed feedback.
- AC3: `branch-completion` checks git state and protects unrelated changes before merge/discard/cleanup.
  - Verification: skill preconditions and trigger eval cases.
- AC4: Generated catalogs and validators remain current.
  - Verification: `make verify`.

## Outcomes & Retrospective

- What shipped / merged: draft PR created at https://github.com/shunta-sato/agent-instructions-playbook/pull/67; merge pending review.
- What went well: new skill descriptions validate without description style flags; trigger evals reference all three new skills.
- What went wrong: system `quick_validate.py` depends on `yaml`, which is not installed in the default Python environment.
- Follow-ups / tech debt tickets: none for this PR.
