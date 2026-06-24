# Source Provenance and Claim Boundaries

Use this manifest when an answer depends on bundled source evidence, exact ROS 2 Humble option support, or a claim that might differ in an installed target environment.

## Evidence Priority

When sources disagree, use this priority order:

1. Observed command execution in the target shell, with command, stdout, stderr, exit code, and environment recorded.
2. Installed CLI help from the target shell, such as `ros2 <command> -h` and `ros2 <command> <verb> -h`.
3. Bundled ROS 2 Humble source evidence in this skill.
4. General examples or memory.

If `ROS_DISTRO` is unset or not `humble`, do not treat bundled Humble source as exact installed option evidence until installed help confirms the option.

## Authoritative Bundled Source Set

| Area | Repository / package scope | Branch | Commit / version | Covers |
| --- | --- | --- | --- | --- |
| Core `ros2` CLI | `ros2cli` repository package family | `humble` | commit `30d4600fa0b74aaf0fccd6a855a56b902dd79b47`; `ros2cli` package version `0.18.18` | top-level command loading, graph options, daemon behavior, `action`, `component`, `doctor`, `interface`, `lifecycle`, `multicast`, `node`, `param`, `pkg`, `service`, and `topic` verbs |
| Bag CLI | `rosbag2` repository | `humble` | commit `089b8f0ae229079626a8477086ea095b6a48fca8` | `ros2 bag` entry points, record/play/info/list/convert/reindex options, storage and QoS behavior |
| Launch CLI | `launch_ros` repository | `humble` | commit `39517491468facd0d57ed3c3592c092baeff8afd` | `ros2 launch` command entry point and ROS launch integration |
| Launch loading | `launch` repository | `humble` | commit `fbe7d984f109fe212ba4af9279e0da55844b78f9` | launch file loading utilities and Python launch side-effect boundary |
| Security CLI | `sros2` repository | `humble` | commit `7c8f9869f4ae0b5db644dd6a05c2c0da007cc091` | `ros2 security` verbs, keystore/enclave/key/policy command behavior |

Related Humble facts named in command references, such as `rclpy.qos.*.short_keys()`, `rcl_interfaces/msg/Log`, and `rcl/include/rcl/logging_rosout.h`, are claim-site anchors rather than a blanket source scope. If a task hinges on those details in a target image, verify the installed package/help/source before making an exact claim.

## Reference Ownership

- `command-map.md` owns command groups, verbs, option placement, common graph options, and source-backed return behavior for the core `ros2cli` package family.
- `bag-launch-security.md` owns `ros2 bag`, `ros2 launch`, and `ros2 security` option surfaces and artifact-safety constraints.
- `implementation-notes.md` owns source-level behavior notes that are not obvious from help output.
- `task-index.md` and `execution-patterns.md` own recipes. Recipes must not broaden source claims beyond this manifest.
- `answer-contract.md` owns how to report observed evidence, installed-help checks, caveats, and blocked claims.

## Reporting Rules

When source provenance matters, include a compact line in the answer or execution record:

```text
Source basis: bundled Humble source manifest; installed help verified: <command or not checked>; observed run: <yes/no>.
```

Do not assume a local source checkout path. Source paths in references are repository-relative evidence anchors only.

## Blocked Claims

Bundled source evidence alone cannot prove:

- the active target image has identical options or plugin availability
- non-Humble distro option support
- Fast DDS or DDS transport root cause
- real-time, zero-copy, performance, production readiness, or robot safety
- that an empty `/rosout` observation window means a node is not logging elsewhere
