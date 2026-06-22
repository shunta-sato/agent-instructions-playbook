# Subagent Execution

Use this reference when an ExecPlan delegates a bounded piece of work to a
subagent, worker model, generated custom agent, or similar delegated executor.

Delegation is an execution mode of an ExecPlan. It is not a substitute for
planning, supervision, validation, or final quality gate review.

## Required Lifecycle

1. Confirm the work is independently delegatable.
   - It has a narrow goal.
   - It has explicit allowed files and commands.
   - It has objective validation.
   - It does not require broad architecture, API, security, concurrency, or
     product judgment from the worker.
2. Classify the task class and route metadata.
   - Use `references/model-routing.md` when model choice matters.
   - Put task class, capability profile, prompt detail, risk gate, and
     escalation profile in the task brief.
3. Write the task brief before invocation.
   - Start from `templates/subagent-task-brief.md`.
   - Include all allowed files, allowed commands, expected artifacts,
     validation commands, stop conditions, and report format.
4. Invoke the worker with only the task-local context it needs.
   - Do not include hidden intended fixes unless the brief requires them.
   - Do not let the worker discover scope by editing first.
5. Require a report.
   - Start from `templates/subagent-report.md`.
   - The report must list changed files, commands run, results, scope
     compliance, unresolved concerns, and escalation notes.
6. Review the output before accepting it.
   - Use `templates/supervisor-review-request.md` when asking a reviewer or
     supervisor agent to check the delegated output.
   - Compare changed files and commands against the brief.
   - Re-run or independently verify required validation when needed.
7. Update the ExecPlan.
   - Record brief path, worker report path or summary, verification result,
     accepted/rejected decision, and follow-ups.

## Task Brief Minimum Fields

Every delegated task brief must include:

- task name and task class
- capability profile and prompt detail level
- goal
- allowed read files
- allowed edit files
- forbidden files or areas
- allowed commands
- required validation commands
- expected artifacts
- stop and escalate conditions
- report format

For `strict` prompt detail, also require:

- exact editable file list
- exact behavior, assertion, or output expected
- exact validation command
- explicit "do not edit production code" or equivalent when applicable
- explicit stop conditions for missing targets, conflicting evidence, or scope
  expansion

## Acceptance Rules

Do not accept delegated output as complete when:

- the worker changed files outside `allowed edit files`
- the worker ran unapproved destructive commands
- required validation was skipped without a stated blocker
- the report omits changed files or validation results
- the worker claims correctness from self-assessment only
- the worker made broad design decisions not listed in the brief

Token telemetry is not required for this PR. If token data is unavailable, write
`not_collected` or leave telemetry for the later run-ledger workflow.

## Escalation Rules

Escalate to the supervisor instead of continuing delegation when:

- the worker needs more files than allowed
- production code appears wrong while the task allowed tests only
- expected behavior conflicts with tests or documentation
- validation fails for a reason outside the worker scope
- task class, capability profile, or model route is missing or stale
- the worker output would require a new ExecPlan milestone

## Forbidden Patterns

- Do not ask a subagent to "fix this generally" without a brief.
- Do not let a subagent infer allowed files from repository search results.
- Do not select the latest/newest plan, catalog, lockfile, or report by mtime.
- Do not treat raw file co-presence as proof that a brief, report, and
  validation came from the same run.
- Do not accept "tests should pass" as validation evidence.
