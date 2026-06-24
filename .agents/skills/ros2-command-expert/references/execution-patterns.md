# ROS 2 `ros2` Execution Patterns

Use these recipes after checking `command-map.md` for exact options.

## Fresh Graph Snapshot

Use this when fresh graph state is needed or when comparing live graph changes. Do not stop the daemon as a routine refresh; direct discovery is the safer first fresh check:

```bash
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t --no-daemon --spin-time 2
ros2 service list -t --no-daemon --spin-time 2
```

Notes:

- `action list`, `service type`, `service find`, and `service call` do not expose common daemon options in this Humble source.
- If a command supports only daemon/default path, run it first as-is and verify `ROS_DOMAIN_ID`/`RMW_IMPLEMENTATION`. If stale daemon state is plausible, cross-check with related direct graph commands where available and report the discrepancy. Restart the daemon only for explicit daemon diagnosis/recovery or with user approval.

## Long-Running and Interactive Commands

Before recommending `tmux`, verify it exists once per stable execution context and cache the result:

```bash
command -v tmux >/dev/null 2>&1 && echo "tmux available" || echo "tmux not installed"
```

Use `tmux` when the process must keep running, when the user may attach later, or when multiple panes are useful:

```bash
tmux new-session -d -s ros2-watch 'ros2 topic list -t'
tmux attach -t ros2-watch
tmux kill-session -t ros2-watch
```

For persistent log capture, write output inside the tmux command:

```bash
tmux new-session -d -s ros2-log 'ros2 topic echo /rosout rcl_interfaces/msg/Log --qos-reliability reliable --qos-durability transient_local --qos-depth 1000 --no-lost-messages >rosout.yaml 2>ros2.stderr'
tmux capture-pane -pt ros2-log -S -200
```

Use shell `timeout` instead of `tmux` for bounded automation, but verify it exists once per stable execution context because some robot images do not include GNU/coreutils `timeout`:

```bash
command -v timeout
timeout 15s ros2 topic echo /topic pkg/msg/Type
timeout 10s ros2 service call /trigger std_srvs/srv/Trigger '{}'
timeout 20s ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci '{order: 5}'
```

Commands that commonly need a guard are `topic echo`, `topic hz`, `topic bw`, `topic delay`, `topic pub` without `--once/--times`, `service call -r`, `action send_goal`, `multicast receive`, `doctor hello`, `component standalone`, `bag record`, `bag play --loop`, and `launch`.

If `timeout` is unavailable but `tmux` exists, use tmux for bounded observation before generating Python:

```bash
session="rosout-$(date +%H%M%S)"
tmux new-session -d -s "$session" 'ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >rosout.csv 2>ros2.stderr'
sleep 10
tmux send-keys -t "$session" C-c
```

If the session disappears, first check whether the command inside tmux exited; do not assume tmux cannot persist:

```bash
session="tmux-probe-$(date +%H%M%S)"
tmux new-session -d -s "$session" 'command -v ros2; ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >rosout.csv 2>ros2.stderr; printf "rc=%s\n" "$?" >rosout.rc; sleep 60'
sleep 3
tmux list-sessions
tmux capture-pane -pt "$session" -S -200 >tmux-pane.txt
```

If `tmux new-session -d -s probe 'sleep 60'` persists but the ROS session disappears, the likely issue is command construction, setup inheritance, output path, quoting, or ROS option failure. Inspect `tmux-pane.txt`, `ros2.stderr`, and `rosout.rc` before switching to detached fallback.

If the agent runtime cannot preserve tmux sessions, use an explicit detached process before generating Python. Always write stdout/stderr to files, write a PID file, verify the process is alive, and record a literal numeric stop command for cleanup:

```bash
out="rosout_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$out"
sh -c 'setsid ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >"$1/rosout.csv" 2>"$1/ros2.stderr" & echo $! >"$1/pid"' sh "$out"
pid="$(cat "$out/pid")"
ps -p "$pid" -o pid,stat,comm,args >"$out/process.txt"
# stop later with: kill -INT <literal-pid>
```

Detached capture is operationally significant: do not leave it running indefinitely. Store the command, PID, start time, output paths, and cleanup status with the artifacts.

For a single logger, filter in `ros2 topic echo` and write straight to a file:

```bash
session="rosout-cocoda-$(date +%H%M%S)"
tmux new-session -d -s "$session" 'ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --filter '\''m.name == "cocoda_logger_node"'\'' --no-lost-messages >cocoda_logger.csv 2>ros2.stderr'
sleep 30
tmux send-keys -t "$session" C-c
```

If `tmux` is absent, use bounded `timeout` when it exists. In safety-gated agent shells, avoid dynamic PID-stop recipes such as `pid=$!; ...; kill "$pid"` or `kill "$(cat file.pid)"`; those may be rejected before execution because the shell command does not contain a literal numeric PID. For bounded non-stateful observations such as `/rosout` capture, prefer direct `timeout ... ros2 ... >stdout 2>stderr` over generated Python:

```bash
# bounded observation
timeout 20s ros2 topic echo /topic pkg/msg/Type >topic.yaml 2>ros2.stderr

# bounded /rosout capture without shell kill/PID control
timeout -s INT 10s ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >rosout.csv 2>ros2.stderr
```

When neither GNU `timeout` nor `tmux` is available, use a small Python `subprocess` wrapper for bounded automation. Reuse one wrapper instead of rebuilding a new parser for each command. For stateful recorders, make the wrapper send SIGINT first, then SIGTERM/SIGKILL only if the process refuses to exit:

```bash
python3 - <<'PY'
import signal
import subprocess

cmd = [
    'ros2', 'topic', 'echo', '/rosout', 'rcl_interfaces/msg/Log',
    '--csv',
    '--no-lost-messages',
]
with open('rosout.raw.yaml', 'wb') as out, open('ros2.stderr', 'wb') as err:
    proc = subprocess.Popen(cmd, stdout=out, stderr=err)
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.send_signal(signal.SIGINT)
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.terminate()
            proc.wait(timeout=2)
PY
```

For commands that need graceful shutdown to flush state, send SIGINT explicitly:

```bash
bag="sample_bag_$(date +%Y%m%d_%H%M%S)"
timeout -s INT 30s ros2 bag record -o "$bag" /chatter /rosout
ros2 bag info "$bag"
```

## Hidden Names

Use the correct flag location:

```bash
ros2 node list -a
ros2 node info /_hidden_node --include-hidden
ros2 topic --include-hidden-topics list -t
ros2 topic --include-hidden-topics type /_hidden_topic
ros2 service --include-hidden-services list -t
ros2 param list /_hidden_node --include-hidden-nodes
ros2 lifecycle nodes -a
ros2 lifecycle get --include-hidden-nodes /_hidden_lifecycle_node
```

If completion does not show a hidden name, type the full name manually and use the hidden flag. Several verbs can operate on hidden resources even when completion did not include them.

## Node-Centered Inspection

Start from nodes when you need ownership:

```bash
ros2 node list
ros2 node info /node_name
ros2 node info /node_name --include-hidden
```

Then inspect each resource:

```bash
ros2 topic info -v /topic
ros2 service type /service
ros2 action info -t /action
ros2 param list /node_name --param-type
```

Duplicate-node warning means multiple graph participants share the exact full node name. `node info` reports only one of them; verify process launch/remapping before making conclusions.

## Topic Type to Payload

Discover type:

```bash
ros2 topic list -t
ros2 topic type /topic
ros2 topic type /topic >topic.type.out 2>topic.type.err
type=$(grep -E '^[A-Za-z_][A-Za-z0-9_]*/(msg|srv|action)/[A-Za-z_][A-Za-z0-9_]*$' topic.type.out | head -1)
[ -n "$type" ] && ros2 interface show "$type"
ros2 interface proto pkg/msg/Type --no-quotes
```

Do not pipe raw `ros2 topic type` stdout directly into `interface show`: missing topics can produce empty output, and Fast DDS SHM diagnostics may appear on stdout in some environments. Keep raw files and extract only a valid ROS interface name before using it.

Echo one message:

```bash
timeout 10s ros2 topic echo --once /topic pkg/msg/Type
```

Echo a field:

```bash
timeout 10s ros2 topic echo --once /odom nav_msgs/msg/Odometry --field pose.pose.position
```

Publish once:

```bash
ros2 topic pub -1 -w 1 --keep-alive 2 /chatter std_msgs/msg/String '{data: hello}'
```

Publish finite stream:

```bash
ros2 topic pub --times 5 -r 2 -w 1 /chatter std_msgs/msg/String '{data: hello}'
```

For stamped messages, use implementation-supported placeholders:

```bash
ros2 topic pub -1 /pose geometry_msgs/msg/PoseStamped '{header: auto, pose: {position: {x: 1.0}}}'
ros2 topic pub -1 /clocklike custom_msgs/msg/Stamped '{stamp: now}'
```

## Topic QoS Workflows

Inspect endpoint QoS:

```bash
ros2 topic info -v /topic
```

Let `echo` auto-match existing publishers:

```bash
ros2 topic echo /topic
```

Force reliable transient-local subscription only when publishers offer Transient Local durability:

```bash
ros2 topic echo /topic pkg/msg/Type --qos-reliability reliable --qos-durability transient_local
```

If this waits despite a visible publisher, inspect `ros2 topic info -v /topic` for incompatible offered QoS. A Reliable or Transient Local subscription will not receive from Best Effort or Volatile-only publishers.

Publish latched-style sample for late subscribers:

```bash
ros2 topic pub -1 /topic pkg/msg/Type '{field: value}' --qos-reliability reliable --qos-durability transient_local --qos-depth 1 --keep-alive 5
```

Avoid incompatible QoS by pairing extremes carefully:

- A Reliable subscription may not receive from a Best Effort publisher.
- A Transient Local subscription may not match a Volatile publisher.
- A one-shot publisher exits after its keep-alive period; late subscribers only receive the sample while the publisher is still alive, or from another still-alive Transient Local publisher.
- `echo` without explicit QoS falls back to Best Effort/Volatile when publishers disagree so it can connect to all compatible endpoints.

## ROS Log Collection Through `/rosout`

Humble `ros2cli` has no dedicated `ros2 log` command. Use `ros2 topic echo /rosout rcl_interfaces/msg/Log`.

Start by discovering logger names:

```bash
timeout 10s ros2 topic echo /rosout rcl_interfaces/msg/Log --field name --qos-reliability reliable --qos-durability transient_local --qos-depth 1000 --no-lost-messages
```

Capture all logs with `/rosout` QoS:

```bash
ros2 topic echo /rosout rcl_interfaces/msg/Log --qos-reliability reliable --qos-durability transient_local --qos-depth 1000 --no-lost-messages
```

Filter by severity:

```bash
ros2 topic echo /rosout rcl_interfaces/msg/Log --filter 'm.level >= 30' --no-lost-messages
ros2 topic echo /rosout rcl_interfaces/msg/Log --filter 'm.level >= 40' --no-lost-messages
```

Filter by logger and message content:

```bash
ros2 topic echo /rosout rcl_interfaces/msg/Log --filter 'm.name == "talker"' --no-lost-messages
ros2 topic echo /rosout rcl_interfaces/msg/Log --filter 'm.name.endswith("talker") and "timeout" in m.msg.lower()' --no-lost-messages
```

Output only one field:

```bash
ros2 topic echo /rosout rcl_interfaces/msg/Log --field msg --no-lost-messages
ros2 topic echo /rosout rcl_interfaces/msg/Log --field msg --filter '"timeout" in m.lower()' --no-lost-messages
ros2 topic echo /rosout rcl_interfaces/msg/Log --field level --filter 'm >= 30' --no-lost-messages
```

Machine-oriented capture:

```bash
ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages
ros2 topic echo /rosout rcl_interfaces/msg/Log --no-arr --truncate-length 512 --no-lost-messages
```

Separate ROS log data from middleware stderr:

```bash
ros2 topic echo /rosout rcl_interfaces/msg/Log --qos-reliability reliable --qos-durability transient_local --qos-depth 1000 --no-lost-messages >rosout.yaml 2>ros2.stderr
```

If `ros2.stderr` or raw stdout contains `RTPS_TRANSPORT_SHM Error`, use the `fastdds-shm-triage` skill before treating it as a CLI failure. Some Fast DDS builds emit SHM diagnostics on stdout and may colorize them with ANSI escapes, so keep the raw capture, strip ANSI, and filter those lines before machine parsing:

```bash
ros2 topic echo /rosout rcl_interfaces/msg/Log --no-lost-messages >rosout.raw.yaml 2>ros2.stderr
python3 -c 'import re,sys; ansi=re.compile(r"\x1b\[[0-9;]*[A-Za-z]"); [sys.stdout.write(s) for line in sys.stdin if "RTPS_TRANSPORT_SHM" not in (s:=ansi.sub("", line)) and "Failed init_port fastrtps_port" not in s]' <rosout.raw.yaml >rosout.yaml
```

Always add `--no-lost-messages` for machine-oriented `/rosout` capture. If it was omitted and stdout contains `A message was lost!!!`, rerun the capture with `--no-lost-messages` instead of trying to parse that stream as pure YAML/CSV.

Use `fastdds shm clean` directly only after `command -v fastdds` succeeds and the user explicitly asks for SHM cleanup. Preserve raw stdout/stderr before cleanup, run `fastdds shm clean` once, then run it a second time to confirm the result. Report the exact cleanup output from both runs. If SHM errors continue after two clean runs, investigate live processes, permissions, container IPC settings, or transport selection; do not blindly delete `/dev/shm/fastrtps*`.

Persistent capture with tmux, only after `command -v tmux` succeeds:

```bash
tmux new-session -d -s rosout-warn 'ros2 topic echo /rosout rcl_interfaces/msg/Log --qos-reliability reliable --qos-durability transient_local --qos-depth 1000 --filter "m.level >= 30" --no-lost-messages >rosout.warn.yaml 2>ros2.stderr'
tmux capture-pane -pt rosout-warn -S -100
tmux kill-session -t rosout-warn
```

Important constraints:

- `Log.level` values are `DEBUG=10`, `INFO=20`, `WARN=30`, `ERROR=40`, `FATAL=50`.
- `Log.name` is the logger name, so inspect it before assuming it equals `/node_name`.
- `--filter` is Python `eval` with variable `m`; do not run untrusted expressions.
- With `--field`, `m` is the selected field value.
- Humble `topic echo` has no arbitrary `--format` template. Use YAML, `--csv`, a single `--field`, or post-process externally.

## Rate, Bandwidth, and Delay

Rate:

```bash
timeout 15s ros2 topic hz /topic
timeout 15s ros2 topic hz /topic --window 50 --wall-time
```

Bandwidth:

```bash
timeout 15s ros2 topic bw /topic --window 50
```

Header delay:

```bash
timeout 15s ros2 topic delay /stamped_topic
```

Notes:

- These commands block until a publisher exists and can still print "does not appear to be published yet" or wait forever when discovery or QoS prevents their sensor-data subscription from matching.
- They subscribe with `qos_profile_sensor_data`; this can differ from `topic echo` and may miss Reliable/Transient Local-only scenarios.
- `delay` requires `header.stamp`.
- `hz` default clock is ROS time; use `--wall-time` if `/clock` is absent or paused.
- Always wrap these in outer `timeout` for automation; validate with `topic list -t` and `topic info -v` before concluding the publisher is absent.

## Services

Discover and inspect:

```bash
ros2 service list -t
ros2 service find example_interfaces/srv/AddTwoInts
ros2 service type /add_two_ints
ros2 service type /add_two_ints >service.type.out 2>service.type.err
type=$(grep -E '^[A-Za-z_][A-Za-z0-9_]*/(msg|srv|action)/[A-Za-z_][A-Za-z0-9_]*$' service.type.out | head -1)
[ -n "$type" ] && ros2 interface show "$type"
ros2 interface proto example_interfaces/srv/AddTwoInts --no-quotes
```

Call once:

```bash
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts '{a: 1, b: 2}'
```

Call repeatedly:

```bash
timeout 10s ros2 service call /trigger std_srvs/srv/Trigger '{}' -r 1
```

Notes:

- `service call` waits indefinitely for service availability. Use shell `timeout` for automation.
- The response is printed with Python `repr`, not YAML.
- Check `service list -t` or `service type` before calling; an unavailable service can look like a hung CLI rather than an immediate error.

## Actions

Discover:

```bash
ros2 action list -t
ros2 action info -t /fibonacci
ros2 interface proto example_interfaces/action/Fibonacci --no-quotes
```

Send goal and wait:

```bash
timeout 20s ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci '{order: 5}'
```

Send goal with feedback:

```bash
timeout 20s ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci '{order: 5}' --feedback
```

Fire-and-return after goal send is version-sensitive. Confirm installed support before using the internal timeout option:

```bash
ros2 action send_goal -h | grep -E -- '(-t, --timeout|--timeout)'
```

If help lists it, the inspected source syntax is `-t N` or `--timeout N`; otherwise do not use it.

SIGINT attempts to cancel an accepted or executing goal. The inspected Humble source has `--timeout`, but a validated Humble environment rejected it, so prefer shell `timeout` unless `ros2 action send_goal -h` confirms the option.

## Parameters

Inventory:

```bash
ros2 param list
ros2 param list /node --param-type
ros2 param describe /node parameter_name
ros2 param get /node parameter_name
```

Set with explicit YAML typing:

```bash
ros2 param set /node enabled true
ros2 param set /node count 3
ros2 param set /node gain 1.25
ros2 param set /node label '!!str off'
ros2 param set /node values '[1, 2, 3]'
```

Dump and reload:

```bash
timeout 20s ros2 param dump /node > node.params.yaml
timeout 20s ros2 param load /node node.params.yaml
ros2 param get /node some_parameter
```

Wildcard file:

```yaml
/**:
  ros__parameters:
    use_sim_time: false
/node:
  ros__parameters:
    use_sim_time: true
```

Default `param load` applies `/**`; add `--no-use-wildcard` to require an exact node entry.

Parameter verbs are graph-dependent. If `get`, `describe`, `dump`, or `load` reports `Node not found` while `set` appeared to work amid SHM stderr, re-check the node with `node list --no-daemon --spin-time N` and do not classify SHM stderr alone as the parameter result.

## Lifecycle

Find lifecycle nodes:

```bash
ros2 lifecycle nodes
ros2 lifecycle get
```

Inspect transitions:

```bash
ros2 lifecycle list /lifecycle_node
ros2 lifecycle list /lifecycle_node --all
```

Transition by label or id:

```bash
ros2 lifecycle set /lifecycle_node configure
ros2 lifecycle set /lifecycle_node 1
ros2 lifecycle get /lifecycle_node
```

Use `--include-hidden-nodes` or `lifecycle nodes -a` for hidden lifecycle nodes.

## Components

List registered component types:

```bash
ros2 component types
ros2 component types composition
```

List running containers:

```bash
ros2 component list --containers-only
ros2 component list /ComponentManager
```

Load:

```bash
ros2 component load /ComponentManager pkg_name plugin_name -n node_name --node-namespace /ns -p use_sim_time:=true -r old:=new
```

Unload:

```bash
ros2 component unload /ComponentManager 1
```

Standalone:

```bash
ros2 component standalone pkg_name plugin_name -c my_container
```

After load/unload, verify with `ros2 component list` and `ros2 node list`.

## Packages and Executables

Find packages and executables:

```bash
ros2 pkg list
ros2 pkg prefix demo_nodes_cpp
ros2 pkg prefix demo_nodes_cpp --share
ros2 pkg executables demo_nodes_cpp
ros2 pkg executables demo_nodes_cpp --full-path
```

Run:

```bash
ros2 run demo_nodes_cpp talker --ros-args -r __node:=talker1
ros2 run --prefix 'gdb -ex run --args' demo_nodes_cpp talker
```

Create package:

```bash
pkg="my_pkg_$(date +%Y%m%d_%H%M%S)"
ros2 pkg create "$pkg" --build-type ament_python --node-name talker --dependencies rclpy std_msgs
cpp_pkg="my_cpp_pkg_$(date +%Y%m%d_%H%M%S)"
ros2 pkg create "$cpp_pkg" --build-type ament_cmake --node-name talker --dependencies rclcpp std_msgs
```

`pkg create` writes files and aborts if the package directory already exists. Ensure the destination is intended and use a fresh package name or destination directory.

## Interfaces

List:

```bash
ros2 interface packages
ros2 interface packages --only-msgs
ros2 interface list --only-srvs
ros2 interface package example_interfaces
```

Show and prototype:

```bash
ros2 interface show example_interfaces/msg/String
ros2 interface show --no-comments example_interfaces/msg/String
ros2 interface proto example_interfaces/msg/String --no-quotes
ros2 topic type /chatter >topic.type.out 2>topic.type.err
type=$(grep -E '^[A-Za-z_][A-Za-z0-9_]*/(msg|srv|action)/[A-Za-z_][A-Za-z0-9_]*$' topic.type.out | head -1)
[ -n "$type" ] && ros2 interface show "$type"
```

Use `proto` for shell payload scaffolding, but remove outer quotes or use `--no-quotes` before embedding into commands.

## Bags

Inspect installed storage and compression support:

```bash
ros2 bag list storage --verbose
ros2 bag list compressor --verbose
ros2 bag list decompressor --verbose
```

Record selected topics with bounded automation:

```bash
bag="sample_bag_$(date +%Y%m%d_%H%M%S)"
timeout -s INT 30s ros2 bag record -o "$bag" /chatter /rosout
ros2 bag info "$bag"
```

Record all visible topics persistently only after `tmux` is available:

```bash
bag="run_bag_$(date +%Y%m%d_%H%M%S)"
tmux new-session -d -s bag-record "ros2 bag record -a -o '$bag' >bag.stdout 2>bag.stderr"
tmux capture-pane -pt bag-record -S -100
tmux send-keys -t bag-record C-c
```

Record hidden topics, or topics discovered later:

```bash
ros2 bag record -a --include-hidden-topics
ros2 bag record --regex '/camera/.*' --include-unpublished-topics
```

Use QoS overrides when recorder auto-adaptation is not enough:

```yaml
/camera/image:
  reliability: best_effort
  durability: volatile
  history: keep_last
  depth: 10
```

```bash
ros2 bag record /camera/image --qos-profile-overrides-path qos.yaml
```

Play deterministically:

```bash
ros2 bag play sample_bag --start-paused --disable-keyboard-controls
ros2 service call /rosbag2_player/play_next rosbag2_interfaces/srv/PlayNext '{}'
ros2 service call /rosbag2_player/burst rosbag2_interfaces/srv/Burst '{num_messages: 10}'
```

Play with clock and remap:

```bash
ros2 bag play sample_bag --clock 40 --remap /old:=/new
```

Repair metadata:

```bash
ros2 bag reindex sample_bag
ros2 bag info sample_bag
```

Notes:

- `bag record` and `bag play --loop` are long-running; use `tmux` or shell `timeout` after verifying the tool exists, or use Python timeout control.
- Stop `bag record` with SIGINT (`timeout -s INT`, `tmux send-keys C-c`, or Python `Popen.send_signal(signal.SIGINT)`) so metadata is written. Hard termination or a too-short timeout can leave no `metadata.yaml`, causing later `bag info`, `bag play`, `reindex`, or `convert` to fail.
- Use a unique output directory for every recording. An existing `-o` directory is rejected, and a stale directory without `metadata.yaml` will cause later `bag info`, `bag play`, `reindex`, or `convert` failures that are not playback bugs.
- `record --use-sim-time` waits for `/clock` and is incompatible with `--no-discovery`.
- `record --snapshot-mode` exposes recorder service `~/snapshot`; call it to flush buffered data.
- `play --wait-for-all-acked 0` waits forever and only matters with Reliable publisher QoS.
- `mcap` does not support `--compression-mode message` in this Humble source; use MCAP storage config for chunk compression.
- For sqlite3 crash-resistance, prefer `--storage-preset-profile resilient`; storage config can override preset settings.

## Launch

Inspect arguments without launching:

```bash
ros2 launch pkg_name file.launch.py --show-args
ros2 launch pkg_name file.launch.py --print
```

Run with launch arguments:

```bash
ros2 launch pkg_name file.launch.py use_sim_time:=true robot_ns:=/robot1
```

Run a launch file by path:

```bash
ros2 launch ./file.launch.py use_sim_time:=true
```

Run persistently only after `tmux` is available:

```bash
tmux new-session -d -s ros2-launch 'ros2 launch pkg_name file.launch.py >launch.stdout 2>launch.stderr'
tmux capture-pane -pt ros2-launch -S -100
```

Debug subprocesses:

```bash
ros2 launch --debug pkg_name file.launch.py
ros2 launch --show-all-subprocesses-output pkg_name file.launch.py
ros2 launch --launch-prefix 'gdb -ex run --args' --launch-prefix-filter 'talker' pkg_name file.launch.py
```

Notes:

- Launch arguments must be `name:=value`; duplicates are last-one-wins.
- If the first positional is an existing file, single-file mode is used. In that mode the optional `launch_file_name` positional becomes the first launch argument.
- `--show-args` and `--print` still load the launch file; Python launch files run import-time code and call `generate_launch_description()`.
- XML/YAML launch files require installed `launch_xml` / `launch_yaml` parser packages.
- `--launch-prefix-filter` is invalid without `--launch-prefix`.

## Security

Create a keystore and enclave:

```bash
keystore="keystore_$(date +%Y%m%d_%H%M%S)"
ros2 security create_keystore "$keystore"
ros2 security create_enclave "$keystore" /robot1/talker
ros2 security list_enclaves "$keystore"
```

Generate artifacts from a policy:

```bash
ros2 security generate_artifacts -k keystore -p policy.xml
ros2 security create_permission keystore /robot1/talker policy.xml
```

Generate a draft policy from the live graph:

```bash
ros2 security generate_policy policy.xml --no-daemon --spin-time 2
```

Run with security environment:

```bash
export ROS_SECURITY_ENABLE=true
export ROS_SECURITY_STRATEGY=Enforce
export ROS_SECURITY_KEYSTORE=keystore
ros2 run demo_nodes_cpp talker --ros-args --enclave /robot1/talker
```

Notes:

- `create_key` and `list_keys` are deprecated aliases; prefer `create_enclave` and `list_enclaves`.
- `create_keystore` fails when the target already exists as a valid keystore; use a fresh path for tests or automation.
- `generate_artifacts` uses `ROS_SECURITY_KEYSTORE` if `--keystore-root-path` is omitted.
- `create_permission` requires the policy file to contain a matching `<enclave path="...">`; a keystore enclave created by `generate_artifacts -e` is not enough.
- `generate_policy` excludes hidden nodes in this Humble source.
- Security commands create or rewrite files; verify the target keystore and policy file before running.

## Diagnosis and Networking

Basic checks:

```bash
ros2 doctor
ros2 doctor --include-warnings
ros2 doctor --report
ros2 doctor --report-failed
```

Multi-host connectivity:

```bash
tmux new-session -d -s multicast-receive 'ros2 multicast receive >multicast.receive 2>multicast.stderr'
ros2 multicast send --ttl 1
cat multicast.receive
timeout 10s ros2 doctor hello --once
timeout 30s ros2 doctor hello --topic /canyouhearme
```

For cross-host issues, verify on every host:

```bash
echo "$ROS_DOMAIN_ID"
echo "$RMW_IMPLEMENTATION"
ros2 multicast receive
ros2 multicast send
```

`multicast receive` receives a single UDP datagram and exits. Start receive before send, redirect its output to a file, and avoid relying only on `tmux capture-pane` after send because the session may already have exited.

## Scripting Rules

- In every fresh shell wrapper, subagent command, or `bash -lc` execution, first verify `command -v ros2`. If it is missing, source the active setup file in the same shell, e.g. `. "/opt/ros/$ROS_DISTRO/setup.bash"` only after checking `ROS_DISTRO` and file existence.
- Use `tmux` for persistent long-running processes only after `command -v tmux` succeeds.
- Use `timeout` for bounded automation only after `command -v timeout` succeeds; otherwise use tmux or a small Python wrapper. Avoid dynamic shell `kill "$pid"` recipes in safety-gated agent shells. Use SIGINT for `bag record` so metadata is flushed.
- In bash validation scripts that pipe `ros2` output to `sed`, `head`, `grep`, or similar, enable `set -o pipefail` or capture stdout/stderr to files first and inspect the `ros2` exit code. Otherwise a downstream filter can hide an upstream `ros2` failure or traceback.
- Prefer `--count-*` options when scripts only need existence/counts.
- Use `--hide-type` for `param get` when a script needs only value.
- Guard `topic type` or `service type` pipelines so `interface show` is not fed empty input or SHM diagnostic text; extract a valid `pkg/(msg|srv|action)/Name` line first.
- Use `--no-daemon --spin-time N` and compare with the default daemon-backed graph before making absence claims; do not restart the daemon merely to refresh the graph.
- Capture stderr as well as stdout; duplicate node warnings and some deprecation warnings are on stderr.
- For log collection, write `/rosout` stdout and middleware stderr to separate files; `RTPS_TRANSPORT_SHM Error` is Fast DDS transport output, not a `/rosout` log record, and may need ANSI stripping plus filtering from raw stdout before parsing.
- If `RTPS_TRANSPORT_SHM Error` appears, use `fastdds-shm-triage` before marking the `ros2` command failed.
- Use unique output paths for `bag record`, `pkg create`, security keystores/artifacts, and other filesystem-mutating commands; existing outputs commonly cause intentional CLI errors.
- Treat a returned string from command implementation as an error under console entry point behavior; `sys.exit("message")` prints to stderr and exits nonzero.

## Safe Absence Claim Template

Before saying a node/topic/service/action is absent:

```bash
ros2 node list
ros2 topic list -t
ros2 service list -t
ros2 action list -t
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t --no-daemon --spin-time 2
ros2 service list -t --no-daemon --spin-time 2
```

Then state the environment: `ROS_DOMAIN_ID`, `RMW_IMPLEMENTATION`, host, command timestamps, whether hidden names were included, and which commands were default daemon-backed versus direct discovery. For command groups without direct discovery options, state that limitation instead of restarting the daemon.
