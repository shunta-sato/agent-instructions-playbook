# Subagent Task Brief

## Task Identity

- Task name:
- Task class:
- Capability profile:
- Prompt detail:
- Risk gate:
- Escalation profile:
- ExecPlan path:
- Brief path:

## Goal

Describe the one bounded outcome the worker must produce.

## Allowed Context

You may read:
- `<path>`

You may edit only:
- `<path>`

Do not edit:
- `<path or area>`

## Required Behavior

- Input or scenario:
- Expected output or assertion:
- API, function, command, or artifact to use:
- Nearby pattern to follow:

## Constraints

- Do not broaden architecture, API, security, concurrency, or product decisions.
- Do not add files outside the allowed edit list.
- Do not change validation commands without reporting why.
- Do not use concrete model IDs unless supplied by the supervisor from the current route.

## Allowed Commands

- `<command>`

## Required Validation

Run:
- `<command>`

If validation cannot run, report the exact blocker and do not claim success.

## Stop And Escalate Instead Of Guessing When

- the target file, function, command, or artifact does not exist
- the expected behavior conflicts with existing tests or documentation
- production code appears wrong but the brief allows tests only
- more files must be edited than allowed
- validation fails for a reason outside this task scope
- model route, task class, or capability profile is missing or stale

## Expected Artifacts

- Changed files:
- Report format: use `subagent-report.md`

## Output Required

Return:
- changed file paths
- commands run
- validation results
- scope compliance result
- unresolved concerns
- escalation notes
