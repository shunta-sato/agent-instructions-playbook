# Execution Plans reference

## 1) Decide whether durable planning is needed

Record:

- ExecPlan required: `yes | no`.
- Durable trigger: session/owner handoff, independent milestones, irreversible
  decision record, explicit request, or monitor lane.
- Existing plan to reuse, if present.

Use the active PR/Delivery Control instead when one owner can keep the feature
reviewable without a durable handoff document.

## 2) Create or update the plan

Use `plans/YYYYMMDD-<slug>.md` and the repository template. Keep the required
sections concise:

- purpose and observable outcome;
- in-scope and non-goals;
- real constraints and explicit targets;
- paths and current context;
- chosen design and material boundaries;
- milestone/progress state;
- validation and acceptance;
- surprises and decisions that affect continuation;
- handoff and outcomes.

Unknowns need a cheapest decisive proof, not an open-ended research section.

## 3) Maintain only durable state

Update at milestone completion, owner/session transfer, material scope change,
or blocker publication. A short pause does not require a document rewrite when
no durable fact changed.

Minimum handoff:

- branch/candidate identity;
- capability now working and remaining gap;
- exact checks and results;
- blocker or risk that changes the next action;
- next one to three steps and key files.

Quantitative targets are recorded only when they are actual acceptance or
operating constraints. Include metric, target, measurement method, and measured
result. Do not invent proxy targets to make a plan appear measurable.

## 4) Delegation

A worker brief names the user journey/DoD, non-goals, allowed files, commands,
focused validation, expected output, and stop conditions. Workers update their
run evidence; the root agent updates the ExecPlan and final candidate state.

## 5) Closeout

At merge, explicit block, abandonment, or monitor transfer, record the outcome,
remaining limitations, and continuation owner. Link a failure retrospective only
when its own trigger applies.
