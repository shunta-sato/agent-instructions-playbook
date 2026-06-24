# ROS 2 Command Answer Contract

Use this reference when returning a command recommendation, command plan, or executed-command result.

## Recommendation Format

````markdown
Task:
- <what the user asked>

Risk:
- read_only | bounded_observation | mutating_graph_or_node_state | robot_affecting_or_runtime_control | destructive_filesystem_or_security

Command:
```bash
<exact command>
```

Why:
- <one sentence grounded in command semantics>

Validation:
```bash
<second command, or "not applicable" with reason>
```

Caveats:
- <distro/help verification, daemon/discovery, QoS, blocking, artifact safety, or none>
````

## Executed Command Format

````markdown
Environment:
- ROS_DISTRO:
- ROS_DOMAIN_ID:
- RMW_IMPLEMENTATION:
- ros2 path:
- daemon status:

Execution:
- intent:
- risk class:
- command:
- run status: proposed_only | executed
- exit code:
- stdout artifact:
- stderr artifact:
- stop/cleanup status:

Validation:
- command:
- result:

Decision:
- success | inconclusive | failed | blocked

Claim boundary:
- <what can and cannot be concluded>
````

## Contract Rules

- Include exact concrete names from the task or discovered evidence.
- Include validation for every mutating command, or explicitly mark the command as proposed only.
- Include artifact paths when command output was captured.
- Treat bounded timeout exit codes as evidence to interpret, not automatic failure.
- Do not treat missing token telemetry as a correctness failure when command scope and validation evidence are present.
- Do not claim real-time, zero-copy, transport reliability, robot safety, or production readiness from CLI source or CLI success alone.
