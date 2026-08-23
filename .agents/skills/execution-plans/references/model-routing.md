# Model Routing For Delegated Execution

Use this reference when an ExecPlan delegates work to a subagent, worker model,
or generated custom agent and model choice matters.

## Routing Order

1. Identify the **active execution harness** from the actual environment or an
   explicit delegator statement. Examples include `claude-code`, `codex`, and
   `copilot`; a model family name is not a harness identity.
2. Classify the delegated task into a task class from
   `.agents/model-routing/task-classes.yml`.
3. Read the task class fields that constrain delegation:
   - `profile`
   - `prompt_detail`
   - `risk_gate`
   - `default_effort`
   - `max_scope`, when present
   - `success_criteria.required`
   - `escalation_profile`, when present
4. Resolve the capability profile through the current resolver policy.
5. Before consuming a concrete model from
   `.agents/model-routing/model-catalog.json` or
   `.agents/model-routing/route-lockfile.json`, require a non-empty top-level
   `harness` equal to the active harness.
6. If the harness is missing, unknown, or mismatched, keep the concrete model
   unresolved. Do not inspect candidates, do not fall back across harnesses, and
   do not describe the selected model as available. Continue in the current
   main session or stop delegation, according to the task's risk and scope.
7. Write the subagent task brief using only route metadata valid for the active
   harness before invoking the worker.

## Model Rules

- Task classes, capability profiles, risk gates, and prompt detail are
  harness-independent. Concrete model availability is harness-dependent.
- Do not put concrete production model IDs in skill bodies, task briefs, or
  static routing instructions unless they came from a current catalog/lockfile
  whose `harness` matches the active harness, or from an explicit user choice
  that is actually invokable there.
- A catalog marked `harness: claude-code` is not execution authority for Codex
  or GitHub Copilot, even when its candidate matches the desired capability
  profile.
- Do not select disabled, unavailable, retired, policy-blocked, rumored, or
  watchlist models.
- Do not treat a newly announced model as selectable until the matching-harness
  catalog marks it selectable and smoke eval evidence exists.
- Profile fallback may choose another capability profile **within the same
  harness only**. It must never become cross-harness fallback.
- For smaller or lower-cost models, increase task-brief specificity instead of
  relying on implicit architecture or product judgment.
- In Copilot CLI workflows where task-level custom-agent model fields must be
  respected, do not run the outer session with `auto`; a resolved session model
  can override custom-agent model fields.

## Resolver Examples

Matching harness:

```sh
python3 scripts/resolve_model_route.py codebase_exploration \
  --catalog .agents/model-routing/model-catalog.json \
  --harness claude-code
```

Mismatched harness, which must return `selected: false`:

```sh
python3 scripts/resolve_model_route.py codebase_exploration \
  --catalog .agents/model-routing/model-catalog.json \
  --harness codex
```

The expected fallback reason is
`catalog_harness_mismatch:claude-code:codex`; the Claude candidate is not a
usable Codex worker and must not be mentioned as though it were invoked.

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

- the active harness cannot be identified
- the catalog or lockfile harness is missing or differs from the active harness
- no matching-harness catalog/lockfile exists and a concrete model is required
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
