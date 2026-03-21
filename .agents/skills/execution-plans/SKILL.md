---
name: execution-plans
description: "MANDATORY for complex/long-running work: create and maintain an ExecPlan in plans/<slug>.md (WBS/progress, design notes, decisions, surprises, and handoff). Always open PLANS.md and references/execution-plans.md."
metadata:
  short-description: "ExecPlan: plan/WBS/progress + handoff"
---

## Purpose

Use this skill to create (or update) an **ExecPlan**: a living, self-contained plan that makes long work measurable, reviewable, and handoff-ready.

This addresses three recurring failure modes in agentic coding:

- work starts without a shared plan, so scope drifts
- progress is not tracked, so “where are we?” is unclear
- context handoff is weak, so long tasks regress or stall

## When to use

This skill is **mandatory** when any ExecPlan trigger is true (see `PLANS.md`), including:

- multi-step / multi-session tasks
- cross-boundary refactors or new modules
- tasks with meaningful unknowns (API choices, rollout, concurrency, performance)

It is also a good default when you are unsure.

## How to use

1) Open `PLANS.md` and `references/execution-plans.md`.

2) Create or update a plan file under `plans/` using `plans/_template_execplan.md`.
   - Quick start helper: `python scripts/init_artifact.py --kind execplan --slug <ticket-or-topic>`

3) Keep the plan up to date while you work:
- update **Progress (WBS)** as items complete
- record **Surprises & discoveries** as you learn new constraints
- record **Decision log** entries for trade-offs
- update **Handoff** whenever you pause or finish a milestone

4) If a human is present and the change is risky/irreversible, ask for approval after drafting the plan and before large edits.

## Gotchas

- **Common pitfall:** creating the plan first but not updating Progress (WBS).  
  **Instead:** update status for each completed task and keep todo/in-progress/done current.
- **Common pitfall:** handling major direction changes verbally and not recording a Decision log.  
  **Instead:** append reason, alternatives, and adoption decision to the plan Decision log.
- **Common pitfall:** leaving stale handoff notes at session end, forcing the next person to re-investigate.  
  **Instead:** always update Handoff with current status / next step / blocker / commands run before stopping.
- **Common pitfall:** moving ahead ad-hoc on complex work without creating an ExecPlan.  
  **Instead:** if any PLANS.md trigger applies, create `plans/<slug>.md` before starting.

## Output expectation

When this skill is used, produce:

- An updated ExecPlan file in `plans/…`
- A short status update in the standard format (see the reference)
- Clear “what’s next” items if work is not finished
