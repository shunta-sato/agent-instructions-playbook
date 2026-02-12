# PLANS.md — Execution Plans (ExecPlans)

This file defines what an **ExecPlan** is and how to use it.

An ExecPlan is a **living, self-contained** design + execution document for work that is large enough to:
- span multiple milestones or sessions, or
- require handoff to another person/agent, or
- benefit from explicit decision tracking (trade-offs, experiments, rollouts).

For small, single-session changes, the normal workflow (`$dev-workflow`) is enough. Do not create a plan just to create a plan.

## When an ExecPlan is required

Create (or update) an ExecPlan when **any** of the following is true:

- The change is expected to take more than ~2 hours of focused work, or it will likely span multiple commits/PRs.
- The change crosses boundaries (layers/modules/services), introduces a new module, or changes data flow.
- The request has non-trivial unknowns (API design, data model, concurrency, performance targets, rollout).
- You expect to stop/resume later, or you want a handoff-ready state at any moment.

If in doubt, create an ExecPlan. The time you spend writing it should be recovered by fewer wrong turns.

## Where plans live

Store each ExecPlan as a single Markdown file under:

- `plans/<slug>.md`

Recommended naming:

- `plans/YYYYMMDD-<short-slug>.md` (sorted by time, easy to scan)

Start from:

- `plans/_template_execplan.md`

## Non-negotiable requirements

An ExecPlan must be:

1) **Self-contained**  
A newcomer can continue the work from only: the ExecPlan + the current working tree.

2) **Outcome-focused**  
Define observable behavior, and how to verify it (commands + expected results).

3) **A living document**  
Update it as you learn. Do not treat it as a one-time artifact.

4) **Evidence-based**  
When something is uncertain, capture experiments, measurements, logs, or failing test output that justify decisions.

5) **Handoff-ready**  
Every stopping point must update the **Handoff** section (what’s done, what’s next, how to run, where you left off).

## Required sections

An ExecPlan must contain these sections (exact headings can differ, but content must exist):

- Purpose / Big Picture
- Scope (in / out)
- Constraints / quality targets
- Context & orientation (paths, key concepts)
- Design (interfaces, boundaries, error handling, observability, test strategy)
- Validation & acceptance (how to prove success)
- Progress (WBS) (checkbox list)
- Surprises & discoveries
- Decision log
- Handoff
- Outcomes & retrospective

## Workflow

Use the **Explore → Plan → Code → Commit** loop:

1) Explore  
Read relevant files and tests. Capture facts (paths, conventions, constraints) in the plan.

2) Plan  
Fill the template. For risky/irreversible changes, ask a human for approval before implementing.

3) Code  
Implement milestone-by-milestone. Keep **Progress**, **Decision log**, **Surprises**, and **Handoff** up to date.

4) Commit  
Commit code + plan updates together so history tells a coherent story.

## Status updates (human-facing)

When reporting progress (PR description, issue comment, chat), use:

- Summary (1–2 sentences)
- Done (max 3 bullets)
- Next (max 3 bullets)
- Risks/Blocks (max 3 bullets)
- Links (plan path + key commits/tests)

## Notes

- An ExecPlan is not a full architecture paper. It is an **executable specification**: it should tell you what to change and how to verify it.
- If a plan grows too large, split into phases (Phase 1/2) as separate plan files. Keep each file self-contained.
