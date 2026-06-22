# Model Routing For Delegated Execution

Use this reference when an ExecPlan delegates work to a subagent, worker model,
or generated custom agent and model choice matters.

## Routing Order

1. Classify the delegated task into a task class from
   `.agents/model-routing/task-classes.yml`.
2. Read the task class fields that constrain delegation:
   - `profile`
   - `prompt_detail`
   - `risk_gate`
   - `default_effort`
   - `max_scope`, when present
   - `success_criteria.required`
   - `escalation_profile`, when present
3. Resolve the capability profile through the current resolver policy and
   catalog/lockfile when those artifacts exist.
4. Write the subagent task brief using the resolved route metadata before
   invoking the worker.
5. Record unresolved routing inputs as explicit unknowns; do not guess a model.

## Model Rules

- Do not put concrete production model IDs in skill bodies, task briefs, or
  static routing instructions unless they came from an explicit current
  catalog/lockfile or user instruction.
- Do not select disabled, unavailable, retired, policy-blocked, rumored, or
  watchlist models.
- Do not treat a newly announced model as selectable until the catalog marks it
  selectable and smoke eval evidence exists.
- For smaller or lower-cost models, increase task-brief specificity instead of
  relying on implicit architecture or product judgment.
- In Copilot CLI workflows where task-level custom-agent model fields must be
  respected, do not run the outer session with `auto`; a resolved session model
  can override custom-agent model fields.

## Prompt Detail Contract

Use `.agents/model-routing/prompt-detail-levels.md` as the source of truth.

- `compact`: supervisor/reviewer brief. Include background, decision axis,
  relevant diff, and evidence; do not spell out every implementation step.
- `normal`: bounded code-worker brief. Include goal, files, constraints,
  validation commands, expected artifacts, and stop conditions.
- `strict`: narrow worker brief. Include editable files, forbidden files,
  exact behavior or assertion, validation command, and stop conditions. Do not
  delegate architecture, API, or broad design judgment.

## Stop Conditions

Stop before delegation when:

- task class is unknown or does not match the work
- profile, prompt detail, or risk gate cannot be resolved
- allowed files or validation command are missing
- expected behavior conflicts with existing evidence
- the worker would need to make architecture, API, security, concurrency, or
  broad product decisions outside the brief

Stop after delegation and escalate when:

- changed files exceed the brief
- validation is missing, failed, or not reproducible
- the worker reports unsupported claims
- the worker widened design scope without approval
- the worker could not resolve required model-routing inputs
