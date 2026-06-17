---
name: ros2-qos-investigation
description: "Use when investigating ROS 2 QoS behavior or implementation across rclcpp/rcl/rmw/rmw_fastrtps/Fast DDS, especially Reliability QoS, and a source-based report or discussion packet is needed. Do not use for ordinary ROS node concurrency fixes with no QoS question, generic DDS docs summaries, or final submit gating."
metadata:
  short-description: ROS 2 QoS implementation investigation
---

## Purpose

Use this skill to run a source-based ROS 2 QoS investigation that can survive follow-up discussion.

It answers one question:

**What does the implementation actually do for this QoS behavior, what evidence supports that claim, and what remains unverified?**

## When to use

Use this skill when:

- investigating ROS 2 QoS behavior, especially Reliability QoS, History, Durability, Deadline, Liveliness, or compatibility behavior
- tracing a QoS policy across `rclcpp`, `rcl`, `rmw`, `rmw_fastrtps`, Fast DDS DDS entities, and Fast DDS RTPS internals
- comparing expected QoS semantics with source code, runtime traces, tests, packet captures, or issue evidence
- preparing a report that will be discussed, reviewed, or used to choose follow-up experiments
- checking whether zero-copy, intra-process, Fast DDS DataSharing, or network RTPS paths affect a QoS claim

Do not use it for ordinary ROS executor work with no QoS question, generic DDS summaries with no source trace, already-scoped bug RCA, or final submit readiness.

## How to use

0. Open `references/ros2-qos-investigation.md` and the needed templates.
1. Define the investigation scope: distro/ref, Fast DDS ref, QoS policies, communication path, and investigation type.
2. Create or update `reports/ros2-qos/<topic>-investigation.md` from `templates/investigation-report.md`.
3. Build a source trace map using `templates/source-trace-map.md`.
4. Separate facts from assumptions. Behavior claims need source, test, trace, log, packet capture, or cited document evidence.
5. Route neighboring work only when triggered: requirements, architecture decisions, bug RCA, observability, ROS 2 concurrency, embedded NFRs, hot-path review, staged lowering, or function-boundary review.
6. Plan experiments only after the source trace identifies the claim to test.
7. Produce a discussion packet with confirmed claims, contradicted claims, unresolved questions, next probes, and reviewer decisions requested.

## Outputs

Produce or update:

- `reports/ros2-qos/<topic>-investigation.md`
- `reports/ros2-qos/<topic>-source-trace.md`
- `reports/ros2-qos/<topic>-experiment-plan.md` when experiments are needed

## Rules

- Keep ROS API QoS, DDS Entity QoS, RTPS protocol behavior, and application callback delivery as separate layers.
- Trace intra-process, local delivery, DataSharing, and network RTPS paths separately when a claim depends on the transport path.
- Record distro/ref, QoS profile source, XML/profile/environment overrides, and transport path when they can affect the claim.
- A report may end with `unknown` or `needs experiment`; do not fill gaps with plausible protocol behavior.
