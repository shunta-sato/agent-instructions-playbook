# ROS 2 Command Plan

## User task

<original task summary>

## Extracted concrete arguments

| Kind | Value | Source |
| --- | --- | --- |
| topic |  |  |
| message type |  |  |
| payload |  |  |
| service |  |  |
| action |  |  |
| node |  |  |
| parameter |  |  |
| bag path |  |  |
| package |  |  |
| executable |  |  |
| output path |  |  |

## Risk class

read_only | bounded_observation | mutating_graph_or_node_state | robot_affecting_or_runtime_control | destructive_filesystem_or_security

## Approval status

not_required | proposed_only | requested | approved | blocked

## Proposed command

```bash
<command>
```

## Expected effect

- <what should change or be observed>

## Validation command

```bash
<command or not applicable>
```

## Stop conditions

- missing concrete target
- ambiguous command target
- command would mutate state without approval
- command can block without a finite bound or cleanup path
- existing output path would be overwritten
- installed help does not support required option
- validation cannot be defined

## Claim boundary

- <what the command can prove and what remains outside CLI evidence>
