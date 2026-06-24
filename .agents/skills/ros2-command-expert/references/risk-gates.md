# ROS 2 CLI Risk Gates

Use this reference before proposing or executing `ros2` commands. Classify the highest applicable risk; a command with multiple effects inherits the strictest class.

## Risk Classes

### read_only

Examples:

- `ros2 node list`
- `ros2 topic list -t`
- `ros2 service list -t`
- `ros2 interface show`
- `ros2 bag info`
- `ros2 doctor --report-failed`

Allowed:

- Execute after environment preflight.
- No user confirmation required unless the target context is production-sensitive.

Required evidence:

- command
- exit code
- key output or artifact path
- caveat when graph/discovery/daemon freshness affects interpretation

### bounded_observation

Examples:

- `timeout 10s ros2 topic echo ...`
- `ros2 topic echo --once ...`
- bounded `/rosout` capture
- `ros2 topic hz` with external timeout
- tmux capture with explicit stop/cleanup command

Allowed:

- Execute only with an explicit bound, finite option, or controlled session cleanup path.
- Prefer `timeout` when verified; use tmux or Python fallback only when the environment requires it.

Required evidence:

- bound method
- stdout/stderr artifact path
- stop/cleanup method
- observation window
- exit code and whether timeout was expected

### mutating_graph_or_node_state

Examples:

- `ros2 topic pub`
- `ros2 service call`
- `ros2 action send_goal`
- `ros2 param set`, `delete`, or `load`
- `ros2 lifecycle set`
- `ros2 component load` or `unload`

Allowed:

- Propose a command plan first unless the user explicitly requested execution.
- Require exact target names copied from the task or discovered evidence.
- Require a validation command that observes the resulting state.
- Require stop/rollback conditions when the command can continue or be reversed.

Required evidence:

- command plan
- expected effect
- validation command
- approval status when execution was requested
- rollback or stop condition when applicable

### robot_affecting_or_runtime_control

Examples:

- action goals that can move hardware
- lifecycle transitions on production nodes
- launch of robot-affecting stacks
- bag play into a live graph
- parameter changes affecting actuators, safety, clocks, or controllers
- long-running `ros2 run`, `ros2 launch`, or control-stack operation

Allowed:

- Require explicit user approval before execution.
- Prefer dry-run, help inspection, `--show-args`, `--print`, or isolated simulation unless the user confirms the target.
- Do not infer safety from CLI syntax alone.

Required evidence:

- target context
- approval text or workflow rule
- abort/stop condition
- validation and observation path
- claim boundary separating CLI execution from robot safety or production readiness

### destructive_filesystem_or_security

Examples:

- `ros2 security create_keystore`
- `ros2 security generate_artifacts`
- `ros2 bag reindex`
- `ros2 bag convert`
- `ros2 pkg create`
- deleting, replacing, or overwriting bag, keystore, artifact, package, or policy directories

Allowed:

- Never delete or overwrite existing user artifacts unless explicitly authorized.
- Use fresh output paths by default.
- Check path existence before execution.
- Record cleanup/defer decision.

Required evidence:

- path existence check
- chosen output path
- command plan
- validation command
- cleanup/defer decision

## Decision Rules

- If the task only asks for a command recommendation, do not execute it.
- If a mutating command lacks a validation command, stop and ask for the missing validation target or propose only.
- If a command can block, add a finite option, outer timeout, tmux cleanup path, or explicit stop command before execution.
- If `ROS_DISTRO` is non-Humble or unknown and exact option support matters, verify installed help before claiming the option exists.
- If stderr/stdout contains Fast DDS SHM diagnostics, preserve raw artifacts and classify the diagnostics separately from the `ros2` CLI exit result.
- If an empty `/rosout` window is observed, report the time window and checked publishers; do not conclude that a node is not logging.
