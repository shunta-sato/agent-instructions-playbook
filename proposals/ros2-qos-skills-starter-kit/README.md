# ROS 2 QoS Skills Starter Kit

This proposal packages a ROS 2 / Fast DDS QoS investigation workflow without activating it in `.agents/skills` yet.

The active skill path `.agents/skills/<name>/SKILL.md` should be used after review. Until then, copy the proposed skill directory from this package into `.agents/skills/ros2-qos-investigation/`, copy the eval file into `evals/skill-triggers/`, then run the normal skill validation and index generation commands.

## Proposed active skill

- `ros2-qos-investigation` — source-based ROS 2 QoS implementation investigation, with Reliability QoS as the first-class case.

## Existing skills this kit routes to

| Situation | Route |
| --- | --- |
| Vague reliability or delivery expectations | `requirements-engineering` |
| Reliable vs Best Effort, DataSharing vs network RTPS, or other architecture choices | `architecture-decision-analysis` |
| Observed drop, hang, flake, crash, or regression | `bug-investigation-and-rca` |
| Missing logs, metrics, traces, packet-capture plan, or correlation fields | `observability` |
| Executor, callback group, service/action/timer, or callback starvation concern | `concurrency-ros2` |
| Robot-local, zero-copy, target resource, latency, jitter, or observer-overhead concern | `embedded-system-familiarization`, then specific embedded NFR skills |
| Fast DDS hot path, repeated serialization, allocation, queue, or blocking syscall concern | `embedded-hot-path-review` |
| Low-level implementation changes in RMW/Fast DDS paths | `staged-lowering`, `function-boundary-governor`, then `quality-gate` |

## Files

- `skills/ros2-qos-investigation/SKILL.md`
- `skills/ros2-qos-investigation/references/ros2-qos-investigation.md`
- `skills/ros2-qos-investigation/templates/investigation-report.md`
- `skills/ros2-qos-investigation/templates/source-trace-map.md`
- `skills/ros2-qos-investigation/templates/experiment-plan.md`
- `evals/ros2-qos-investigation.json`
- `activation-notes.md`

## Intended first use

Use this kit for a Reliability QoS investigation that follows the path from ROS 2 QoS API to RMW QoS profile, Fast DDS DDS Entity QoS, RTPS writer/reader state, history/cache state, and application delivery boundary.

The report should make claims only where the source trace or runtime evidence supports them. Open questions and unverified transport paths should stay explicit.
