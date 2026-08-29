---
name: execution-plans
description: "Use when work needs a durable handoff across sessions or owners, has independently trackable milestones, carries a risky irreversible decision that must remain auditable, or the requester explicitly asks for an ExecPlan. Do not use merely because a change is complex, cross-boundary, or estimated above two hours."
metadata:
  short-description: Durable handoff ExecPlan
  requires:
    - references/execution-plans.md
  resources:
    - references/model-routing.md
    - references/subagent-execution.md
  templates:
    - templates/subagent-report.md
    - templates/subagent-task-brief.md
    - templates/supervisor-review-request.md
---

## Purpose

Create a durable, self-contained handoff record only when the work genuinely
needs one. For a single-owner feature that can remain reviewable in one PR,
Delivery Control and the PR description are sufficient.

## When to use

Use when at least one applies:

- work will cross a session or owner boundary;
- independently verifiable milestones need durable state;
- a risky or irreversible decision needs an auditable record;
- the requester asks for an ExecPlan;
- a long monitor/qualification lane needs a stable handoff.

Complexity, a new module, an uncertain design, or a two-hour estimate alone does
not require a plan. Start with the compact route/Delivery Control record and
promote only when a durable handoff need appears.

## How to use

1. Open `PLANS.md` and `references/execution-plans.md`.
2. Reuse an existing plan for the same capability. Otherwise create one under
   `plans/` from `_template_execplan.md`.
3. Keep scope, acceptance, progress, material decisions, validation, and handoff
   current at milestone or ownership boundaries.
4. Record only decisions that affect continuation: contracts, data flow,
   rollout, safety/security, target evidence, or explicit quantitative targets.
5. When delegation is used, open `references/subagent-execution.md`; open
   `references/model-routing.md` only when concrete model choice matters.
6. Stop maintaining the plan after the capability is merged, blocked with
   evidence, or transferred to a monitor lane; complete Outcomes and Handoff.

Do not turn the plan into an architecture paper, duplicate skill templates, or
make artifact completion the critical path.

## Output expectation

Return `ExecPlan required: yes|no`, the concrete durable-handoff trigger, plan
path when used, current milestone, next decisive proof, and handoff state. A
`no` decision produces no plan file.
