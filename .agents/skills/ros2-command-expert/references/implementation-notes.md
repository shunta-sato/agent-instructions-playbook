# ROS 2 `ros2` Implementation Notes

These notes capture behaviors visible from ROS 2 Humble source, not just command help. The source basis is `ros2cli` branch `humble` at commit `30d4600fa0b74aaf0fccd6a855a56b902dd79b47` plus related Humble `rcl`/interface evidence where explicitly named.

## Source Anchors

- CLI entry and buffering: `ros2cli/ros2cli/cli.py`.
- Lazy command/verb loading: `ros2cli/ros2cli/command/__init__.py`, `entry_points.py`, `plugin_system.py`.
- Daemon strategy: `ros2cli/ros2cli/node/strategy.py`, `node/daemon.py`, `node/direct.py`, `node/network_aware.py`, `daemon/__init__.py`.
- Topic command behavior: `ros2topic/ros2topic/api/__init__.py`, `verb/echo.py`, `verb/pub.py`, `verb/hz.py`, `verb/bw.py`, `verb/delay.py`.
- Parameter behavior: `ros2param/ros2param/api/__init__.py`, `verb/*.py`.
- Service/action YAML calls: `ros2service/ros2service/verb/call.py`, `ros2action/ros2action/verb/send_goal.py`.
- Component services: `ros2component/ros2component/api/__init__.py`.
- Doctor checks: `ros2doctor/ros2doctor/api/*.py`.

## Lazy Loading and Help

`ros2cli.command.add_subparsers_on_demand()` first creates subparsers for entry point names without importing every extension. It then parses known arguments to decide which command/verb was selected and loads only that extension, except when no extension is selected and descriptions are needed.

Implications:

- Broken third-party extensions may not affect unrelated command execution.
- Top-level `ros2 -h` may load more extensions than `ros2 topic list -h`.
- Completion uses `_ARGCOMPLETE`/`COMP_LINE` and may trigger partial parsing.

## Daemon and Discovery

`NodeStrategy(args)` chooses graph access:

1. If `args.no_daemon` is true, use `DirectNode`.
2. Else if daemon is running and reachable, use `DaemonNode`.
3. Else spawn daemon and use `DirectNode` for this invocation.

This means the first default graph command after no daemon can start a daemon but still query through a direct node. Later default graph commands query daemon XMLRPC methods when available.

Daemon details:

- Port is `11511 + int(ROS_DOMAIN_ID or 0)`.
- XMLRPC path is `/ros2cli/`.
- Daemon tags include `ros_domain_id` and current RMW implementation.
- `_ros2_daemon` asserts its command-line `--rmw-implementation` and `--ros-domain-id` match the active runtime.
- Default daemon idle timeout is 2 hours.
- `NetworkAwareNode` prints interface addresses and recreates its direct node if interface addresses change.
- Daemon registers graph functions with `before_invocation(..., pretty_print_call)`, so debug output may show method calls.

Direct node details:

- `DirectNode` calls `rclpy.init(args=args.argv if present else [])`.
- It creates node name `NODE_NAME_PREFIX + node_name_suffix`, default suffix is process id.
- It declares/overrides `use_sim_time` from `-s/--use-sim-time`.
- It spins for `--spin-time`, default `0.5`, before returning so discovery can populate.
- `--spin-time` only applies to commands that add direct/strategy node arguments.

Practical rule: after changing ROS environment, re-run the target command and prefer `--no-daemon --spin-time N` where supported for fresh graph checks. Do not restart the daemon as a routine refresh; reserve `daemon stop/start` for explicit daemon diagnosis or user-approved recovery because it can make daemon-backed graph visibility worse in Discovery Server, high-load, or robot-container environments.

## Hidden Names

Hidden topic/service detection uses `rclpy.topic_or_service_is_hidden()`. Hidden node detection checks whether the node basename starts with `rclpy.node.HIDDEN_NODE_PREFIX`.

Non-obvious differences:

- `ros2 topic info` looks up hidden topics by passing `include_hidden_topics=True`.
- `ros2 topic echo`, `hz`, `bw`, and `delay` also call `get_msg_class(... include_hidden_topics=True)` for type discovery.
- `ros2 topic type`, `list`, and `find` respect `args.include_hidden_topics`.
- `ros2 service type` and `find` respect command-level `args.include_hidden_services` but do not add common daemon options.
- Component container detection intentionally includes hidden service info because container services are under `/_container/...`.
- Action commands have no explicit hidden-action filter in this Humble source.

## QoS Behavior

`ros2 topic pub` default QoS:

- `ReliabilityPolicy.RELIABLE`
- `DurabilityPolicy.TRANSIENT_LOCAL`
- depth `1`
- `--keep-alive` defaults to `0.1` seconds after a finite publish. A `-1/--once` publisher can disappear before later graph inspection or late subscription; use a larger `--keep-alive` or a continuous publisher when testing Transient Local behavior.

`ros2 topic echo` default behavior:

- If any QoS option is supplied, missing `--qos-profile` defaults to `sensor_data`, then explicit short-key overrides are applied.
- If no QoS option is supplied, it starts from `sensor_data` and inspects current publishers.
- If every publisher is Reliable, it requests Reliable; otherwise it requests Best Effort and warns if publishers are mixed.
- If every publisher is Transient Local, it requests Transient Local; otherwise Volatile and warns if publishers are mixed.

`profile_configure_short_keys()` caveat:

- It applies depth only when `if depth and depth >= 0`; `0` is false and therefore not applied as an explicit depth.
- If durability is Transient Local and final depth is `0`, it sets depth to `1`.

Measurement verbs:

- `topic hz`, `bw`, and `delay` use `qos_profile_sensor_data`, not the auto-match logic from `echo`.
- `bw` subscribes with `raw=True` and measures serialized byte length of received `AnyMsg` data.
- `hz` uses ROS time by default and system time only with `--wall-time`.
- `delay` computes `node_clock_now - msg.header.stamp` and requires a `header`.
- Because `get_msg_class(... blocking=True)` waits for type discovery and the subscription QoS is fixed to sensor-data, these verbs can keep waiting or say the topic does not appear published even when another publisher exists. Treat that as a discovery/QoS measurement caveat and use an outer timeout.

## YAML and Message Construction

`topic pub`:

- Uses `yaml.safe_load(values)` and requires the result to be a dict.
- Uses `set_message_fields_expanded()`, which recursively fills ROS message fields.
- Converts Python `array.array` and `numpy.ndarray` fields.
- Converts nested arrays of ROS message values into submessage instances.
- Supports `header: auto` for `std_msgs/msg/Header`, leaving `frame_id` empty and updating `stamp` each publish.
- Supports `stamp: now` or any `builtin_interfaces/msg/Time` field value `now`, updating it each publish.

`service call` and `action send_goal`:

- Use `yaml.safe_load()` followed by `rosidl_runtime_py.set_message_fields()`.
- Service response and action result are printed from message objects/YAML helpers, not as machine-stable JSON.
- The inspected Humble source has `action send_goal -t/--timeout`, but a validated Humble target rejected it. Treat this option as installed-version-sensitive and prefer an outer shell `timeout`.

`param set/load/component -p/-e`:

- Use `ros2param.api.get_parameter_value()`.
- YAML booleans such as `off`, `yes`, `no` may become booleans.
- Use YAML tags such as `!!str off` to force strings.
- Homogeneous arrays become typed arrays; mixed arrays become string values.

## Blocking and Timeouts

Commands that may run indefinitely by design:

- `topic echo` unless `--once`.
- `topic pub` unless `--once` or `--times`.
- `topic hz`, `topic bw`, `topic delay`.
- `service call -r`, and `service call` while waiting for an unavailable service.
- `action send_goal`; use shell `timeout` unless installed help confirms `--timeout`.
- `multicast receive`.
- `doctor hello` unless `--once`.
- `component standalone`, because it waits on the spawned container process.
- `bag record`.
- `bag play --loop`.
- `launch` when launched processes stay alive.

Commands with source-level waits:

- `daemon start/stop`: 10 second wait.
- Direct graph discovery: `--spin-time`, default `0.5`.
- `param` service helper calls: most wait 5 seconds for service.
- `component load/unload`: wait 5 seconds for container service.
- `component list`: internal list call completes or reports no response after about 5 seconds.
- `service call`: `cli.wait_for_service()` has no timeout.
- `topic hz/bw/delay`: `get_msg_class(... blocking=True)` loops until topic type appears.
- `bag play --wait-for-all-acked 0`: waits forever for Reliable subscriber acknowledgments.

For persistent or interactive work, verify `tmux` first with `command -v tmux` and then run the long command in a tmux session. Use shell `timeout` for bounded automation only after `command -v timeout` succeeds; some target images do not install GNU/coreutils `timeout`. If absent, use tmux or a Python `subprocess` wrapper rather than dynamic shell `kill "$pid"` recipes, which may be rejected in safety-gated agent shells. Use SIGINT rather than hard termination for `bag record`; otherwise metadata may not be written before `bag info` or `bag play`.

## `/rosout` Log Collection Details

Humble `ros2cli` does not implement a dedicated `ros2 log` command. Logs are collected through the graph as ordinary messages on `/rosout`:

- `ros2topic` tests identify `/rosout` as type `rcl_interfaces/msg/Log`.
- `ros2doctor/api/topic.py` skips `/rosout` in topic health checks, so `doctor` is not a log collection tool.
- `rcl/src/rcl/logging_rosout.c` creates a publisher on topic name `/rosout` using `rcl_interfaces/msg/Log`.
- `rcl/include/rcl/logging_rosout.h` defines default `/rosout` QoS as Keep Last depth `1000`, Reliable, Transient Local, lifespan `{10, 0}` seconds.

`/rosout` is not equivalent to "all ROS process logs". A node may be alive and actively writing to launch stdout/stderr, journald, container logs, or an application log while publishing nothing to `/rosout`. In ROS launch files this often happens through `enable_rosout:=False`. Use `ros2 topic info -v /rosout` before scanning; it lists `/rosout` publisher nodes and QoS more cheaply than repeated `topic echo --field name` windows. Use `ros2 node info /node_name` to check whether the target node actually has a `/rosout` publisher. If it does not, no amount of `ros2 topic echo /rosout` scanning will retrieve that node's stdout/journal logs; use launch/system/container log collection instead.

`rcl_interfaces/msg/Log` Humble fields:

- Constants: `DEBUG=10`, `INFO=20`, `WARN=30`, `ERROR=40`, `FATAL=50`.
- Fields: `builtin_interfaces/Time stamp`, `uint8 level`, `string name`, `string msg`, `string file`, `string function`, `uint32 line`.

`rcl_logging_rosout_output_handler()` populates:

- `stamp` from the log timestamp.
- `level` from the rcutils severity integer.
- `name` from the logger name used to find the registered rosout publisher.
- `msg` from the formatted log string.
- `file`, `function`, and `line` from `rcutils_log_location_t`.

`topic echo` filter/output behavior for logs:

- `--filter EXPR` creates a Python `eval(EXPR)` closure. The variable `m` is available and may be the full `Log` message or the selected field.
- `--field FIELD` splits on `.` and selects fields before filtering and printing.
- Default output uses `message_to_yaml()` and appends `---`.
- `--csv` uses `message_to_csv()` and does not add a header row in `ros2topic`.
- `--flow-style`, `--no-arr`, `--no-str`, `--truncate-length`, and `--full-length` are serializer controls, not a format-template system.
- `--no-lost-messages` disables message-lost event reporting so `A message was lost!!!` does not mix into capture output.
- There is no Humble `topic echo --format` option. For arbitrary log line formats, post-process `--csv`/YAML output or run a custom subscriber.
- Fast DDS `RTPS_TRANSPORT_SHM Error` lines are transport diagnostics, not `/rosout` records. Capture stderr separately, but keep raw stdout too because some environments emit SHM diagnostics on stdout and may colorize them with ANSI escapes. Strip ANSI and filter those lines before parsing ROS YAML/scalar output, and use `fastdds-shm-triage` before declaring the `ros2` command failed.

For bounded `/rosout` windows, prefer direct `timeout ... ros2 topic echo ... >file 2>file` when `timeout` is available. Generate Python only as a fallback for missing `timeout`/`tmux` or for a deliberately reusable parser. A `timeout` exit code can be expected for an observation window; inspect the captured file before concluding that no records were received.

If `timeout` is missing and `tmux` is available, use tmux as the bounded observation mechanism before Python. This keeps the command mostly `ros2`-native: start `ros2 topic echo` in a named tmux session with stdout/stderr redirected, sleep for the capture window, then send `C-c` to the session. Use `--filter 'm.name == "...logger..."'` in the `ros2 topic echo` command for target logger capture instead of scanning `/rosout` names repeatedly.

Some agent runtimes do not preserve tmux sessions even when `tmux` is installed. In that case, an explicit detached process is the next fallback before Python. Treat detached capture as operationally significant: use `setsid`/`nohup` or the runtime's detached process facility, write stdout/stderr to files, write and verify a PID file, and record a literal numeric stop command. Do not leave unmanaged collectors running after the observation task.

In Discovery Server or high-load systems, direct discovery with `--no-daemon --spin-time` can be incomplete even when the daemon-backed graph contains the node. If `ros2 node list` shows `/cocoda_logger_node` but `ros2 node list --no-daemon --spin-time 2` is empty, treat that as a discovery-mode discrepancy, not as evidence that the node disappeared. Record both paths and avoid switching to a different node name.

## Python `eval` Filters

`topic echo --filter` and `topic hz --filter` use Python `eval(expr)` directly.

Implications:

- Do not run untrusted filter expressions.
- The expression can inspect message `m` for `echo`.
- With `echo --field`, `m` in the filter function receives the selected subfield value, not the original full message.
- With `hz --filter`, raw subscription is disabled so the filter receives typed messages.

## Output and Exit Semantics

`ros2cli.cli.main()` returns:

- `0` for help/no command and normal no-op paths.
- `signal.SIGINT` on KeyboardInterrupt.
- `signal.SIGTERM` on `ExternalShutdownException`.
- String form of `RuntimeError` for runtime errors.

Console script behavior normally turns a returned string into stderr output and nonzero exit. When scripting, capture stderr and exit code.

Some commands return strings instead of printing:

- `topic info`: `"Unknown topic '<name>'"`.
- `node info`: `"Unable to find node '<name>'"`.
- `param` verbs: `"Node not found"` and some validation errors.
- `pkg prefix/xml`: `"Package not found"` or XML-specific strings.

## Parameter Source Caveat

In this Humble source:

- `ros2param/verb/set.py` assigns `Parameter.name = args.parameter_name`.
- `ros2param/verb/delete.py` assigns `Parameter.name = args.parameter_name`.
- `ros2param/api.parse_parameter_dict()` correctly assigns `parameter.name = full_param_name` for `param load`.

If testing this exact Humble source, verify `param set/delete` with `param get/list` or prefer `param load` for deterministic bulk changes. If using an installed ROS distro, inspect the installed source/help because this may be branch-specific.

## Interface Show Details

`interface show` parses each interface line with `rosidl_adapter.parser.parse_message_string()` to identify comments, constants, fields, and nested message types.

Non-obvious behavior:

- `ros2 interface show -` reads one line from stdin and rejects TTY or empty input.
- Nested interface definitions are recursively printed under fields.
- Default shows comments only for the top-level interface; nested comments require `--all-comments`.
- `--no-comments` also removes blank lines.

## `ros2 run` Details

Executable discovery uses package prefix from ament index and scans:

```text
<prefix>/lib/<package>/**
```

It ignores directories starting with `.` and selects executable files by `os.access(path, os.X_OK)`. It does not search `PATH`.

`--prefix` is not shell-evaluated as a single string; it is split with `shlex.split()` and prepended to the executable argv.

## Doctor Details

`doctor` loads checks/reports from entry points:

- `ros2doctor.checks`
- `ros2doctor.report`

Failed check import/instantiation/function call emits a warning and continues.

`doctor` without `--include-warnings` ignores warning counts for failure status. With `--include-warnings`, warnings count as failed checks.

Platform/package reports can depend on rosdistro index access, so network errors can affect `doctor` results.

## Multicast Details

`ros2 multicast` and `doctor hello` use group `225.0.0.1`, port `49150`.

The receive socket:

- Sets `SO_REUSEADDR`.
- Sets `SO_REUSEPORT` where available.
- Binds to `('', port)`.
- Joins the multicast group with `IP_ADD_MEMBERSHIP`.

`doctor hello` uses both ROS topic pub/sub and UDP multicast simultaneously and ignores messages from the same hostname.

## Bag Details

`ros2 bag` is provided by the `ros2bag` package, not core `ros2cli`.

Non-obvious behavior:

- `record` validates topic selection in Python before creating a recorder: use exactly one of explicit topics, `--regex`, or `--all`.
- `record --exclude` is only valid with `--all` or `--regex`, not an explicit topic list.
- `record --use-sim-time` waits for `/clock`; combining it with `--no-discovery` is rejected.
- Recorder QoS adaptation mirrors `topic echo` in spirit: all Reliable means request Reliable, otherwise Best Effort; all Transient Local means request Transient Local, otherwise Volatile.
- `record --snapshot-mode` exposes `~/snapshot`; no data is written until the service triggers a snapshot.
- Stop recording with SIGINT when you need a usable bag; hard timeout or process termination can leave no `metadata.yaml`.
- `play --clock` without a value uses 40 Hz.
- `play --wait-for-all-acked 0` means wait forever and only applies to Reliable publisher QoS.
- `list` reports pluginlib resources from the installed environment, so available storage/compression plugins are target-image facts.

## Launch Details

`ros2 launch` is provided by `ros2launch` in `launch_ros`; the runtime is `launch.LaunchService`.

Non-obvious behavior:

- If the first positional argument is an existing file, package lookup is bypassed and single-file mode is used.
- In single-file mode, the optional second positional is treated as a launch argument.
- Package-file mode recursively searches package share for an exact launch file basename and errors on zero or multiple matches.
- Launch arguments are parsed as `<name>:=<value>` into an ordered mapping; duplicates are last-one-wins.
- `--launch-prefix` and `--launch-prefix-filter` are appended as launch arguments after user arguments, so they override direct duplicates.
- `--show-args` and `--print` still load the launch description. Python launch files are imported and call `generate_launch_description()`.
- `--show-all-subprocesses-output` sets `OVERRIDE_LAUNCH_PROCESS_OUTPUT=both`.
- `LaunchService.run()` must run on the main thread, first SIGINT initiates shutdown, and SIGTERM/SIGQUIT can leave launched child processes orphaned.
- XML/YAML support comes from `launch_xml` and `launch_yaml` parser entry points. Verify those packages are installed before assuming `.launch.xml`, `.launch.yaml`, or `.launch.yml` works.

## Security Details

`ros2 security` is provided by `sros2`.

Non-obvious behavior:

- `create_key` and `list_keys` are deprecated aliases for enclave terminology.
- `generate_artifacts` falls back to `ROS_SECURITY_KEYSTORE` when `--keystore-root-path` is omitted.
- `create_keystore` fails when the target is already a valid keystore, while `generate_artifacts` creates a keystore if the selected path is invalid.
- `create_enclave` validates names as namespaces and creates default broad wildcard permissions before any policy-specific permissions are applied.
- `create_permission` selects the policy `<enclave path="...">` matching the requested enclave and rewrites signed permissions for that enclave.
- `generate_policy` uses `NodeStrategy`, supports `--no-daemon --spin-time`, excludes hidden nodes, and exits `1` if no graph nodes are detected.
- Generated governance and permissions use `ROS_DOMAIN_ID`, defaulting to `0`.

## Claim Boundaries

This CLI source can justify:

- command availability and parser behavior
- graph discovery strategy
- QoS profile chosen by CLI-created publishers/subscribers
- YAML conversion behavior
- blocking and timeout behavior inside the CLI

It cannot by itself justify:

- DDS packet delivery guarantees
- RMW-specific transport behavior
- real-time, zero-copy, or production overhead claims
- whether a remote system should be considered healthy without runtime logs or measurements
