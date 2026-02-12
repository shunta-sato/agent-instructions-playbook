# execution-plans

Use this prompt when the task is large enough to benefit from an **ExecPlan** (planning + WBS + progress + handoff).

## What to do

1. Read `PLANS.md`.
2. Create or update an ExecPlan file under `plans/` using `plans/_template_execplan.md`.
3. Fill Purpose/Scope/Constraints/Design first, then add a **Progress (WBS)** list.
4. Before any risky or irreversible changes, ask for human approval.

## Output

Return:

- The plan path (e.g., `plans/YYYYMMDD-<slug>.md`)
- A short status update (Summary / Done / Next / Risks / Links)
