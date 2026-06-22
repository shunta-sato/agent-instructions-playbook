# Prompt Detail Levels

Prompt detail is a task-brief contract. It controls how much judgment is moved
from the worker into the brief before selecting a concrete model.

## compact

Use for supervisors and reviewers.

- Include background, decision axis, relevant diff, and evidence.
- Do not spell out every implementation step.
- Require unsupported claims and unresolved risks to be named.

## normal

Use for code workers with bounded but real implementation judgment.

- Include goal, target files, constraints, validation commands, and expected artifacts.
- Allow local implementation choices inside the stated scope.
- Require the worker to stop when scope or failure mode changes.

## strict

Use for lightweight or narrow workers.

- Include editable files, forbidden files, expected assertion or behavior, validation command, and stop conditions.
- Do not delegate architecture, API, or broad design judgment.
- Treat missing target functions, conflicting expected values, or extra file edits as stop-and-report conditions.
