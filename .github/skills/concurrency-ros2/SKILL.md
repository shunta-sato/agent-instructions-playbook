---
name: concurrency-ros2
description: "ROS 2 (rclcpp/rclpy) concurrency guidance: executors, callback groups, services/actions/timers, and deadlock-safe patterns. Use when modifying ROS nodes or callbacks."
metadata:
  short-description: ROS 2 concurrency patterns
---

## Purpose

Make ROS callbacks safe, non-blocking where needed, and deadlock-resistant.

## When to use

Use this skill when touching:
- rclcpp/rclpy nodes or executors
- callback groups
- services, actions, or timers

## How to use

0) Open `references/concurrency-ros2.md`.
1) Choose executor strategy (SingleThreaded vs MultiThreaded) and justify.
2) Choose callback group layout; explicitly separate blocking/synchronous paths.
3) Identify synchronous service/client calls inside callbacks; apply deadlock rules.
4) Move heavy work off callback threads when needed (worker thread / queue).
5) Add observability hooks for callbacks and queues (length, latency).
6) Define verification (stress + race tooling if multi-threaded).

## Output expectation

- Add a **ROS2 Concurrency Notes** section to the Concurrency Plan.
