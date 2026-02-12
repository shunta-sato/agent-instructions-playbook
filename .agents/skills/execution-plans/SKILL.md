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

3) Keep the plan up to date while you work:
- update **Progress (WBS)** as items complete
- record **Surprises & discoveries** as you learn new constraints
- record **Decision log** entries for trade-offs
- update **Handoff** whenever you pause or finish a milestone

4) If a human is present and the change is risky/irreversible, ask for approval after drafting the plan and before large edits.

## Output expectation

When this skill is used, produce:

- An updated ExecPlan file in `plans/…`
- A short status update in the standard format (see the reference)
- Clear “what’s next” items if work is not finished
