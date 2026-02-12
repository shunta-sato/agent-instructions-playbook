# status-update

Generate a short, human-readable status update for ongoing work.

## Input

Use:

- the current ExecPlan (`plans/<slug>.md`)
- the current diff / changes in the working tree

## Output format

Keep bullets ≤ 3 each:

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
