# Strict ROS 2 Command Task Brief

Use this brief when delegating a narrow `ros2-command-expert` subtask through model routing. Do not include concrete model IDs in the brief.

## Routing

- task_class: `<ros2_command_lookup | ros2_readonly_diagnosis | ros2_mutating_operation_plan>`
- capability_profile: `<resolved by model-routing>`
- prompt_detail: `<resolved by model-routing>`
- escalation_profile: `<resolved by model-routing or supervisor>`

## Task

- user_request:
- concrete ROS names copied from request/evidence:
- target distro/environment facts known:
- required references:
- forbidden assumptions:

## Execution Boundary

- `ros2_command_lookup`: do not execute target commands; return exact command form, option placement, validation idea, and source/help caveat.
- `ros2_readonly_diagnosis`: use only read-only or bounded observation commands; record environment, command, stdout path, stderr path, exit code, stop method, and claim boundary.
- `ros2_mutating_operation_plan`: produce a command plan only; do not execute without explicit user approval. Include risk class, approval boundary, validation command, rollback/cleanup notes where applicable, and output path checks.

## Required Output

- task_class:
- risk_class:
- exact command or command plan:
- validation command:
- evidence/source basis:
- caveats and blocked claims:
- stop/escalate condition:
