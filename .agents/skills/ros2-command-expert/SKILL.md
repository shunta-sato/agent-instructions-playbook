---
name: ros2-command-expert
description: "Use when choosing, checking, or executing ROS 2 Humble `ros2` CLI commands where exact command syntax, runtime safety, discovery behavior, QoS, bag/launch/security options, or evidence-backed interpretation matters."
metadata:
  short-description: Source-backed ROS 2 Humble CLI guide
---

# ROS 2 Command Expert

## Purpose

Use this skill to plan, check, execute, and interpret ROS 2 Humble `ros2` CLI commands with source-backed command semantics, explicit runtime risk gates, and evidence-backed claim boundaries.

## When To Use

Use this skill for:

- choosing exact `ros2` commands and option placement
- checking command syntax, YAML payloads, hidden-name flags, QoS options, daemon/discovery behavior, or blocking behavior
- running read-only graph inspection or bounded ROS observations
- planning mutating ROS commands with validation and stop conditions
- interpreting `ros2` stdout/stderr, `/rosout`, bag, launch, security, daemon, discovery, QoS, or YAML behavior

Do not use this skill as the only authority for:

- ROS 2 application code changes; use `dev-workflow` and code-focused skills
- DDS transport root-cause analysis beyond CLI-visible evidence
- production robot operation without explicit risk gate and user approval
- performance, real-time, zero-copy, safety, or transport claims without lower-layer evidence or measurement

## Required Flow

1. Classify the task: command lookup, command check, read-only inspection, bounded observation, mutating operation plan, executed operation, or output interpretation.
2. Classify operation risk using `references/risk-gates.md` before proposing or running commands.
3. Load the minimum reference needed for the task, including `references/source-provenance.md` when a source-backed claim, non-Humble target, or version-sensitive option matters.
4. Extract concrete arguments from the user task or from discovered command output.
5. Choose the exact command form and validate option placement with installed help when needed.
6. Decide whether the command is proposed only or executed.
7. If executed, record environment, stdout/stderr artifacts, exit code, validation command, validation result, and cleanup/stop status.
8. State claim boundaries and caveats.

Stop instead of guessing when the task lacks a concrete target, the operation would mutate state without approval, the command could affect robot behavior, the output path already exists and would be overwritten, installed help does not support the needed option, or no validation command can be defined for a mutating operation.

## Reference Loading

Load only what the task needs:

- `references/risk-gates.md`: required before any proposed or executed command plan.
- `references/source-provenance.md`: source manifest, evidence priority, installed-help precedence, and blocked source claims.
- `references/task-index.md`: natural-language task to command mapping, common traps, high-frequency exact forms.
- `references/command-map.md`: command groups, verbs, option placement, defaults, and return behavior.
- `references/execution-patterns.md`: bounded observations, tmux/timeout/Python fallbacks, `/rosout`, long-running commands, and safe recipes.
- `references/bag-launch-security.md`: `ros2 bag`, `ros2 launch`, and `ros2 security` options and artifact safety.
- `references/implementation-notes.md`: daemon, discovery, hidden names, QoS, YAML conversion, blocking calls, `eval` filters, and source caveats.
- `references/answer-contract.md`: final answer and execution-record requirements.
- `references/neighbor-skills.md`: boundaries with adjacent ROS, DDS, safety, and workflow skills.

Within one session, cache reference knowledge and environment checks. Re-read only when the target, shell environment, distro, command family, or evidence requirement changes.

## Environment Preflight

Before executing graph-dependent commands, record the active target context once per stable shell/session:

```bash
command -v ros2
echo "ROS_DISTRO=${ROS_DISTRO:-}" "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-0}" "RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-default}"
ros2 --help
ros2 daemon status
```

If `ROS_DISTRO` is set and is not `humble`, treat the bundled source evidence as non-authoritative for exact installed options until help verifies them:

```bash
ros2 --help
ros2 <command> -h
ros2 <command> <verb> -h
```

When a bundled-source detail affects the answer, report whether installed help or target execution was checked, using `references/source-provenance.md`.

If a fresh non-interactive shell loses the ROS environment, source the active installation only after verifying the setup file exists. Do not hard-code host-specific setup paths as facts.

## Concrete Argument Contract

Copy concrete topic, service, action, node, container, enclave, bag, package, executable, parameter, type, YAML file, policy, keystore, and output path names from the user task or observed evidence. Do not substitute placeholders like `/topic`, `/node`, `/service_name`, `/container`, `Type`, `sample_bag`, or `my_pkg` when the task supplies real names.

Before finalizing, self-check every leading-slash ROS name in the command. Except internal helper service names such as `/rosbag2_player/play_next`, `/rosbag2_recorder/snapshot`, `/rosout`, and diagnostic paths such as `/dev/shm`, each leading-slash name must come from the task or discovered evidence.

Use `templates/command-plan.md` for mutating, robot-affecting, destructive filesystem/security, ambiguous, or reviewer-facing command plans.

## Risk And Execution Rules

- `read_only`: may run after environment preflight; record command, exit code, and key output.
- `bounded_observation`: may run only with an explicit bound or controlled cleanup path; record stdout/stderr artifacts and stop method.
- `mutating_graph_or_node_state`: propose a command plan first unless execution was explicitly requested; require validation command and exact target names.
- `robot_affecting_or_runtime_control`: require explicit user approval before execution; prefer dry-run, help inspection, or isolated simulation unless the user confirms the target.
- `destructive_filesystem_or_security`: never delete or overwrite existing user artifacts unless explicitly authorized; use fresh paths by default and record path checks.

For executed commands, fill `templates/execution-record.md` or the equivalent fields in the final answer. Token telemetry absence is not a correctness failure when scope and validation evidence are present.

## Output Expectations

For command recommendations, include:

- task summary
- risk class
- exact command
- why this command form is correct
- validation command or why validation is not applicable
- caveats and claim boundary

For executed commands, include:

- environment: `ROS_DISTRO`, `ROS_DOMAIN_ID`, `RMW_IMPLEMENTATION`, `ros2` path, daemon status when relevant
- command intent and risk class
- command(s), whether run or proposed only, exit code when run
- stdout/stderr artifact paths when run
- validation command and validation result
- cleanup/stop status for bounded or long-running work
- claim boundary: what can and cannot be concluded

## Rationalization Traps

| Trap | Required response |
| --- | --- |
| "This is just a quick `ros2 topic pub`." | Treat it as mutating; produce a command plan and validation command before execution. |
| "The daemon might be stale, restart it." | Do not restart as routine refresh; use direct graph commands with `--no-daemon --spin-time` when supported. |
| "The example command is close enough." | Extract concrete names from the task and replace every placeholder before answering. |
| "No `/rosout` messages appeared, so the node is not logging." | Report the observation window and check publishers/node info before absence claims. |
| "Timeout is probably available." | Verify `timeout` once or use the tmux/Python fallback contract. |
| "SHM text means the ROS command failed." | Separate CLI exit/output from transport diagnostics and preserve raw stdout/stderr. |
| "A reviewer suggested the command, so use it." | Re-check installed help, task names, risk gate, and validation requirement. |
