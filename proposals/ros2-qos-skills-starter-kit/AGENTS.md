# AGENTS.md — ROS 2 QoS investigation workspace

This file is a starter workspace guide for Codex when one investigation spans multiple ROS 2 and Fast DDS repositories. Copy it to the workspace root used for the investigation.

## Mission

Investigate ROS 2 QoS behavior from source evidence and produce reports that can be reviewed in follow-up discussion. The first-class topic is Reliability QoS across ROS 2, `rmw_fastrtps`, and Fast DDS.

## Workspace shape

Repositories may be siblings or under `src/`:

```text
rclcpp/
rcl/
rmw/
rmw_fastrtps/
rosidl_typesupport_fastrtps/
Fast-DDS/
Fast-CDR/
examples/
demos/
```

If a repository or ref is absent, record it as missing evidence and continue with available sources.

## Investigation flow

1. Record scope: ROS 2 distro or refs, Fast DDS ref, RMW implementation, QoS policy, transport path, and exact claim.
2. Build a source trace across layers: `rclcpp`, `rcl`, `rmw`, `rmw_fastrtps`, type support when payload behavior matters, Fast DDS DDS Entity layer, Fast DDS RTPS layer, history/cache, and ROS application delivery.
3. Label every behavior claim with evidence type: `source-trace`, `test`, `runtime-log`, `packet-capture`, `benchmark`, `external-doc`, `assumption`, or `unknown`.
4. Split transport paths when relevant: network RTPS, same-host shared memory, Fast DDS DataSharing, and ROS intra-process delivery.
5. Plan experiments only after the source trace identifies a precise claim to test.
6. Produce a discussion packet with confirmed claims, weakened claims, open questions, next probes, and reviewer decisions requested.

## Report artifacts

Write outputs under:

```text
reports/ros2-qos/<topic>-investigation.md
reports/ros2-qos/<topic>-source-trace.md
reports/ros2-qos/<topic>-experiment-plan.md
```

For the first Reliability QoS investigation, prefer:

```text
reports/ros2-qos/reliability-qos-fastdds-investigation.md
reports/ros2-qos/reliability-qos-fastdds-source-trace.md
reports/ros2-qos/reliability-qos-fastdds-experiment-plan.md
```

## Quality rules

- Use file paths, symbols, and refs for implementation claims.
- Keep ROS API QoS, DDS Entity QoS, RTPS behavior, and callback delivery as separate layers.
- Record QoS profile source, XML profile usage, environment variables, middleware defaults, and `SYSTEM_DEFAULT` handling when they affect the conclusion.
- Record whether evidence came from source inspection, host runs, target runs, traces, or packet captures.
- Mark production, low-overhead, zero-copy, or real-time claims as unproven unless matching target or measurement evidence exists.

## Neighboring playbooks

| Need | Skill |
| --- | --- |
| Vague delivery, loss, latency, or reliability expectations | `requirements-engineering` |
| QoS or transport option comparison | `architecture-decision-analysis` |
| Observed missing messages, hangs, flakes, crashes, or regressions | `bug-investigation-and-rca` |
| Missing logs, metrics, traces, packet capture, or correlation fields | `observability` |
| Executor, callback group, service/action/timer, or callback starvation effects | `concurrency-ros2` |
| Target-local resource, latency, jitter, wakeup, thermal, or observer-overhead claims | `embedded-system-familiarization`, then specific embedded NFR skills |
| Fast DDS hot path, repeated serialization, allocation, queue, lock, or blocking syscall concern | `embedded-hot-path-review` |
| Low-level implementation edits in RMW or Fast DDS paths | `staged-lowering` and `function-boundary-governor` |
| Final submit readiness for a code/test change | `quality-gate` |

## Read-only commands

```bash
git -C <repo> rev-parse HEAD
git -C <repo> status --short
git -C <repo> grep -n "<symbol-or-term>"
git -C <repo> log --oneline -- <path>
```

Experiment artifacts should be linked from the report, preferably under `reports/ros2-qos/artifacts/`.

## Final response format

Return:

1. Investigation brief: question, scope, repos/refs, transport path.
2. Evidence summary: confirmed, contradicted or weakened, unknown.
3. Artifacts written: report paths and purpose.
4. Commands run: command and result, or reason not run.
5. Discussion prompts: decisions requested and next probes.
