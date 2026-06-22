# Supervisor Review Request

## Review Target

- ExecPlan path:
- Task brief path:
- Subagent report path:
- Changed files:
- Task class:
- Capability profile:
- Prompt detail:

## Review Goal

Check whether the delegated output satisfies the task brief and can be accepted
by the supervisor.

## Required Checks

- Compare changed files against allowed edit files.
- Compare commands run against allowed commands.
- Confirm required validation ran or has a reproducible blocker.
- Confirm the worker did not broaden architecture, API, security, concurrency,
  or product scope.
- Confirm unsupported claims are marked as concerns.
- Confirm follow-ups are explicit and not hidden as completed work.

## Evidence To Inspect

- Brief:
- Report:
- Diff:
- Validation output:
- Related ExecPlan WBS item:

## Decision Format

Return one decision:

- `accept`: brief satisfied and required validation evidence is present.
- `revise`: bounded fixes are needed before acceptance.
- `escalate`: task scope, route, validation, or design judgment exceeds the brief.

Include:

- decision
- blocking findings
- non-blocking notes
- required fixes
- evidence reviewed
