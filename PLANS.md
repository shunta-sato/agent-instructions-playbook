# PLANS.md — Execution Plans

An ExecPlan is a durable, self-contained continuation record. It is useful when
work must survive a session or owner boundary; it is not a complexity tax for
ordinary feature development.

## When an ExecPlan is required

Create or reuse one when at least one condition is true:

- work will cross a session or owner boundary;
- the deliverable has independently verifiable milestones that need durable
  coordination;
- a risky or irreversible decision needs an auditable record;
- the requester explicitly asks for an ExecPlan;
- a long-running monitor or qualification lane needs stable handoff state.

Do not require an ExecPlan solely because work is cross-boundary, introduces a
module, contains unknowns, or is estimated above two hours. Use the active
`user-value-delivery` Delivery Control and PR description first. Promote to an
ExecPlan only when a durable trigger appears.

## Where plans live

Use `plans/YYYYMMDD-<short-slug>.md`, starting from
`plans/_template_execplan.md`. Reuse the active plan for the same capability.

## Required qualities

A plan is:

1. **Outcome-focused:** states the user journey and observable acceptance.
2. **Scoped:** names non-goals and the smallest continuation boundary.
3. **Evidence-based:** unknowns have a cheapest decisive proof.
4. **Handoff-ready:** another owner can continue from the plan and worktree.
5. **Living only when facts change:** update at milestones, ownership/session
   transfer, material scope change, or blocker publication.

Do not duplicate skill checklists, write an architecture paper, or update the
plan for a short pause when no durable fact changed.

## Quantitative targets

Record a target only when it is an acceptance or operating constraint. Include:

- metric and denominator;
- target;
- measurement method;
- measured result or explicit `not measured` limitation.

A secondary proxy such as line count does not replace the primary behavioral
outcome. Do not invent targets merely to make the plan appear rigorous.

## Required sections

- Purpose / Big Picture
- Scope (in / out)
- Constraints / Quality targets
- Context & Orientation
- Design
- Milestones
- Progress (WBS)
- Surprises & Discoveries
- Decision log
- Handoff
- Validation & Acceptance
- Outcomes & Retrospective

Keep sections as short as the durable handoff permits. Empty boilerplate is not
evidence.

## Workflow

1. Frame the capability and decide whether a durable trigger exists.
2. Create or reuse the plan only when required.
3. Implement milestone-by-milestone with focused verification.
4. Update durable state at milestone or transfer boundaries.
5. Close with the candidate/PR identity, verification, limitations, and outcome.

For small, single-owner work, use `dev-workflow` and the PR description without
creating a plan.
