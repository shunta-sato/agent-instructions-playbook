---
name: execution-plans
description: "Use when work is complex, long-running, multi-step, cross-boundary, likely to span multiple PRs/sessions, or needs handoff-ready planning under plans/."
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

2.5) Run a **Design→WBS coverage check**: every module, file, or deliverable
   named in the Design section must map to at least one WBS item, or be listed
   as explicitly deferred with a reason. Re-run this check whenever the Design
   section changes.

2.6) If the plan will use a subagent, worker, delegated model, or generated
   custom agent, open `references/subagent-execution.md` before invoking it.
   If model choice matters, also open `references/model-routing.md`. Create the
   task brief first from `templates/subagent-task-brief.md`; require the worker
   report format in `templates/subagent-report.md`; use
   `templates/supervisor-review-request.md` when asking another agent to review
   delegated output.

3) Keep the plan up to date while you work:
- update **Progress (WBS)** as items complete
- record **Surprises & discoveries** as you learn new constraints
- record **Decision log** entries for trade-offs
- record summaries of `implementation-economy` budgets and `design-balance` responsibility maps when those branches are triggered
- **Target re-forecast**: at every phase/milestone boundary, re-forecast each
  quantitative target using current measurements. If the forecast misses a
  declared target by more than ~20%, append a Decision log entry choosing one
  of: re-scope (add work), re-baseline (change the target), or accept-miss
  (with rationale). Do not defer this decision to the final measurement.
- **Surprise escalation**: when a Surprises entry invalidates an assumption
  behind a quantitative target (e.g., "this file cannot be deleted"), the same
  commit must update the target forecast.
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
- **Common pitfall:** the Design section names deliverables (modules, files)
  that never receive a WBS item, so they are silently never built.
  **Instead:** run the Design→WBS coverage check and mark uncovered
  deliverables as deferred-with-reason in the plan.

## Output expectation

When this skill is used, produce:

- An updated ExecPlan file in `plans/…`
- A short status update in the standard format (see the reference)
- Clear “what’s next” items if work is not finished
