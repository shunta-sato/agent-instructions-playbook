# plans/

This folder stores **ExecPlans** for long-running or complex work.

See:
- `PLANS.md` for the rules.
- `plans/_template_execplan.md` for the canonical template.

## Naming

Recommended:

- `YYYYMMDD-<short-slug>.md`

Examples:
- `20260212-observability-rollout.md`
- `20260212-refactor-upload-worker.md`

## Rule of thumb

If you expect to stop and resume later, or if the change crosses boundaries (modules/layers/services), create an ExecPlan and keep it updated.
