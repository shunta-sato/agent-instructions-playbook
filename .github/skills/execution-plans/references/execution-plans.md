# Execution Plans (ExecPlans) — reference

This file is the reference template for `$execution-plans`.

## 1) Decide: do we need an ExecPlan?

Open `PLANS.md` and evaluate the triggers.

Record in your response:

- ExecPlan required? yes|no
- Plan path: `plans/<slug>.md`
- Why (one sentence)

If “no”, continue with `$dev-workflow` only.

If “yes”, continue below.

## 2) Create/update the plan file

1) Pick a file name (recommended: `YYYYMMDD-<short-slug>.md`).
2) Copy `plans/_template_execplan.md`.
3) Fill the sections in this order:

- Purpose / scope
- Constraints / quality targets
- Context & orientation (facts, paths, conventions, unknowns)
- Design (boundaries + errors + observability + tests)
- Milestones (3–7 sentences)
- Progress (WBS) (checkbox list)

If you do not know something, write it as an explicit “Unknown” with a plan to learn it.

## 3) Maintain the plan while coding

### Update rules (non-negotiable)

- **Progress (WBS)**: keep it current.
- **Decision log**: log decisions that affect interfaces, rollouts, data models, or concurrency.
- **Surprises & discoveries**: log newly learned constraints (with evidence when possible).
- **Handoff**: update at every stop (even a short pause), so another agent can continue.

### Minimum handoff content

- branch + commit SHA (or “uncommitted changes exist”)
- what is done vs not done
- how to run and how to test (commands)
- known failures / open risks
- next 1–3 concrete steps
- pointers: the 3–5 most relevant files to read first

## 4) Status update format (human-facing)

Use this format (keep bullets ≤ 3 each):

```markdown
## Status update
- Summary:
- Done:
  - ...
- Next:
  - ...
- Risks/Blocks:
  - ...
- Links:
  - Plan: plans/<slug>.md
  - Verification: <commands/results>
```

## 5) Integration points

- If requirements are unclear, invoke `$requirements-to-design` before filling “Design”.
- If runtime behavior changes, invoke `$observability` and record the plan’s signals in the ExecPlan.
- If concurrency is introduced/changed, invoke `$concurrency-core` (+ platform skill) and record the plan in the ExecPlan.
- Before finishing, run `$quality-gate` and ensure the ExecPlan is updated with final outcomes.
