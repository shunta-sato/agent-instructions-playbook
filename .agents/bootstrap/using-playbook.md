# Using This Playbook

This directory is a helper documentation area referenced by `AGENTS.md`.
Do not assume `.agents/bootstrap` is a special harness auto-load location.
Rules that must always apply belong in `AGENTS.md`; this file explains how to apply those rules.

## Bootstrap Flow

1. Inspect the Agent Index in `AGENTS.md`.
2. Decide which skills apply before starting software-development work.
3. If the user explicitly names a skill, read that skill before responding or editing.
4. For code or test changes, enter through `dev-workflow` and finish through `quality-gate`.
5. For complex or long-running work, create or update an ExecPlan under `plans/`.

## Skill Selection

Skill descriptions should answer only: "when should this skill be used?"
Do not treat a description as a substitute for reading the `SKILL.md` body.
Procedures, required artifacts, references, handoff details, and output formats belong in the body, references, or templates.

## Subagent Briefs

Before invoking a subagent for multi-step or delegated work, create a task brief that states:

- task name and goal
- task class or skill route when known
- files the subagent may read
- files the subagent may edit
- commands the subagent may run
- expected artifacts
- validation method
- stop and escalation conditions

Do not delegate broad architectural judgment through an implicit natural-language handoff.
When the task is narrow or assigned to a lightweight worker, make the brief stricter: fewer writable files, explicit validation commands, and clearer stop conditions.

## Model And Telemetry Boundaries

Do not hard-code concrete model IDs in skill bodies or bootstrap rules.
Resolve models through task class, capability profile, current catalog, policy, and lockfile once those artifacts exist.

Do not make token counts part of task correctness.
Validation results, changed-file scope, required reports, and `quality-gate` decide acceptance.
Token telemetry may be recorded when a harness-native JSONL or equivalent log is available, but missing token telemetry is not a task failure by itself.
