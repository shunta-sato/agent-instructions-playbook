# ROS 2 Command Execution Record

## Environment

| Field | Value |
| --- | --- |
| ROS_DISTRO |  |
| ROS_DOMAIN_ID |  |
| RMW_IMPLEMENTATION |  |
| ros2 path |  |
| daemon status |  |
| target/session |  |

## Command intent

- <why the command was run>

## Risk class

read_only | bounded_observation | mutating_graph_or_node_state | robot_affecting_or_runtime_control | destructive_filesystem_or_security

## Approval

- not_required | approved | blocked | not_applicable
- evidence: <user text, workflow rule, or reason>

## Execution

| Field | Value |
| --- | --- |
| command |  |
| run status | proposed_only | executed |
| exit code |  |
| stdout artifact |  |
| stderr artifact |  |
| bound/cleanup method |  |
| cleanup status |  |

## Validation

| Field | Value |
| --- | --- |
| validation command |  |
| validation exit code |  |
| validation artifact |  |
| validation result | success | inconclusive | failed | blocked |

## Decision

success | inconclusive | failed | blocked

## Claim boundary

- <what can and cannot be concluded from this execution>
