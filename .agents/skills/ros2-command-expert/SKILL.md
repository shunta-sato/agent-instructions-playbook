---
name: ros2-command-expert
description: "Use when Codex needs source-backed ROS 2 Humble CLI guidance for `ros2` graph inspection, topic/service/action interaction, parameters, lifecycle, components, packages, interfaces, doctor, daemon, multicast, `/rosout`, bag, launch, or security workflows, especially when exact option placement, discovery/QoS/YAML semantics, hidden names, blocking behavior, tmux capture, output filtering, plugins, or enclaves matter."
metadata:
  short-description: Source-backed ROS 2 Humble CLI guide
---

# ROS 2 Command Expert

## Scope

Use this skill to choose and run `ros2` commands correctly, then interpret their output from implementation evidence.

Source basis: ROS 2 Humble `ros2cli` source, branch `humble`, commit `30d4600fa0b74aaf0fccd6a855a56b902dd79b47`, `ros2cli` package version `0.18.18`. Additional Humble coverage includes `rosbag2`, `launch_ros`, `launch`, and `sros2`; see `references/bag-launch-security.md` for their exact refs.

This skill is intended to apply to ROS 2 Humble. Before relying on an exact behavior in another distro or robot image, verify the installed CLI with `ros2 --help` and `ros2 <command> <verb> -h`; non-Humble distributions may differ.

Do not assume any source checkout path, repository arrangement, or host-specific folder. Use source file names only as evidence anchors.

## Reference Loading

Load only what the task needs:

- Read `references/task-index.md` first when the user describes a goal in natural language and you need to choose the correct `ros2` command(s). It maps tasks to commands, expected outcomes, validation steps, and common traps.
- Read `references/command-map.md` for command groups, verbs, options, defaults, and return behavior.
- Read `references/execution-patterns.md` for safe command recipes, command composition, `/rosout` log collection, and tmux patterns.
- Read `references/implementation-notes.md` for non-obvious implementation details: daemon, discovery, hidden names, QoS, YAML conversion, blocking calls, `eval` filters, and source caveats.
- Read `references/bag-launch-security.md` for `ros2 bag`, `ros2 launch`, and `ros2 security`: exact options, storage/plugin behavior, launch argument parsing, XML/YAML launch support, and SROS2 keystore/enclave workflows.

Within one session, cache both reference knowledge and environment checks. Do not repeatedly re-read the same reference files or rebuild one-off scripts for the same task family. Prefer direct `ros2` commands and the fixed recipes in this Skill; use custom Python only when native `ros2`, `timeout`, `tmux`, and simple shell post-processing cannot satisfy the request.

## Cached Preflight

1. Confirm the ROS environment once per stable execution context before running graph-dependent commands:

```bash
command -v ros2
echo "ROS_DISTRO=${ROS_DISTRO:-}" "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-0}" "RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-default}"
ros2 --help
ros2 daemon status
```

Do not repeat this full preflight after it has already succeeded in the same session, same target, and same ROS environment. Treat `ros2` availability, `ROS_DISTRO`, `ROS_DOMAIN_ID`, `RMW_IMPLEMENTATION`, daemon status, `tmux` availability, and `timeout` availability as cached facts for the rest of the session. Re-check only when the target or shell environment changes, a new subagent/non-interactive shell may not inherit setup, `ROS_DOMAIN_ID` or `RMW_IMPLEMENTATION` changes, a command fails as if `ros2` is missing, the daemon appears stale, or an exact installed option needs verification.

If `ROS_DISTRO` is set and is not `humble`, treat this skill as Humble source evidence and verify the active installation's help before giving exact option claims.

If a fresh non-interactive shell, subagent, or `bash -lc` wrapper loses the ROS environment, source the active installation's setup file in that same shell before running `ros2`. Do not hard-code a host-specific path unless it exists on the target:

```bash
command -v ros2 >/dev/null 2>&1 || { [ -n "${ROS_DISTRO:-}" ] && [ -f "/opt/ros/$ROS_DISTRO/setup.bash" ] && . "/opt/ros/$ROS_DISTRO/setup.bash"; }
command -v ros2
```

2. Decide discovery mode:

- Use the default daemon path for quick graph inspection.
- Use `--no-daemon --spin-time <seconds>` on commands that support it when graph state must be fresh, when the daemon may be stale, after changing `ROS_DOMAIN_ID` or `RMW_IMPLEMENTATION`, or during tests.
- Do not run `ros2 daemon stop` or `ros2 daemon stop && ros2 daemon start` as routine preflight, first response, or generic graph refresh. In Discovery Server, high-load, or robot-container environments it can leave the daemon-backed graph emptier and it will not repair lower-layer DDS discovery/liveliness problems. Use daemon restart only when the task is specifically daemon diagnosis/recovery, the user explicitly approves it, or you are in an isolated test after recording both default and `--no-daemon` results.
- For verbs that do not expose `--no-daemon --spin-time`, run the default command first. If stale daemon state is plausible, cross-check with related direct graph commands that do support `--no-daemon`; report the discrepancy instead of restarting the daemon.
- In Discovery Server or heavily loaded systems, `--no-daemon --spin-time` can transiently return an empty or incomplete graph even when the default daemon path sees nodes. If default `ros2 node list` finds a node but direct `--no-daemon` does not, do not conclude the node disappeared; record both and prefer the path that matches the user's observed graph unless the task is specifically daemon freshness diagnosis.

3. For long-running or interactive commands, prefer `tmux` only after verifying it exists once in the current execution context:

```bash
command -v tmux >/dev/null 2>&1 && echo "tmux available" || echo "tmux not installed"
```

Use `tmux` for persistent log capture, persistent publishers, interactive `run`, `bag record`, looping `bag play`, `launch`, and multi-command observation. Use shell `timeout` for bounded automation only after confirming it exists; some robot images lack GNU/coreutils `timeout`. If `tmux` or `timeout` is absent, prefer a small Python `subprocess` wrapper that sends SIGINT before SIGTERM/SIGKILL when graceful shutdown matters. Avoid dynamic shell PID-stop recipes such as `kill "$pid"` or `kill "$(cat file.pid)"` in safety-gated agent shells; if a human must use shell `kill`, first obtain the actual numeric PID and issue a separate literal `kill -INT <numeric-pid>` or `kill -TERM <numeric-pid>` command. This matters for `topic echo`, `topic hz`, `topic bw`, `topic delay`, `topic pub` without `--once/--times`, `service call -r`, `action send_goal`, `multicast receive`, `doctor hello`, `component standalone`, and long-running launch/bag commands.

If `timeout` is missing but `tmux` exists, use a tmux observation session before generating Python. Start `ros2 topic echo` in tmux with output redirected to files, wait the observation window, then send `C-c` to the tmux session. If the agent runtime does not preserve tmux sessions, use an explicit detached process fallback before Python: start with `setsid`/`nohup`, write stdout/stderr and a PID file, verify the PID is alive, and record a literal stop command. Do not leave unmanaged detached collectors behind.

If a tmux session appears "not preserved", diagnose before falling back: the command inside tmux may have exited immediately because of quoting, a missing setup in that shell, a bad output path, an unsupported option, or an empty finite command. Re-run once with `remain-on-exit` behavior by appending an rc file and short sleep, then inspect `tmux list-sessions`, `tmux capture-pane`, stdout, stderr, and the rc file. Do not report that tmux itself is unusable unless a simple `tmux new-session -d -s probe 'sleep 60'` also disappears from `tmux list-sessions`.

4. Treat these commands as mutating or operationally significant: `topic pub`, `service call`, `action send_goal`, `param set/delete/load`, `lifecycle set`, `component load/unload/standalone`, `pkg create`, `run`, `bag record`, `bag play`, `bag convert`, `bag reindex`, `launch`, and `security create_*`/`generate_*`.

5. Quote YAML payloads with single quotes in shells:

```bash
ros2 topic pub -1 /chatter std_msgs/msg/String '{data: hello}'
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts '{a: 1, b: 2}'
timeout 20s ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci '{order: 5}'
```

## Execution Workflow

1. Classify the task:

- Graph inventory: `node`, `topic`, `service`, `action`, `param list`, `lifecycle nodes`, `component list`.
- Message/service/action interaction: `topic echo/pub/hz/bw/delay`, `service call`, `action send_goal`.
- Static installed metadata: `interface`, `pkg`, `run`, `component types`, `bag list`.
- System diagnosis: `doctor`, `doctor hello`, `multicast`, `daemon`, `extensions`.
- Bag/launch/security operations: `bag record/play/info/reindex/convert/list`, `launch`, `security create_*`, `security generate_*`, `security list_*`.

2. Copy concrete names from the task into commands. Do not replace a provided topic, service, action, node, container, enclave, bag, package, executable, parameter, or type with placeholders like `/topic`, `/node`, `Type`, or `sample_bag`. Do not copy example names from this Skill when the task provides different names.

   Before finalizing a command, self-check every leading-slash ROS name in it: except required internal service names such as `/rosbag2_player/play_next`, `/rosbag2_recorder/snapshot`, and diagnostic paths such as `/dev/shm`, each leading-slash name should appear in the task text. If the task says `/rosout`, do not answer with `/odom`; if it says `/fixture_node`, do not answer with `/_hidden_node`; if it says `/fibonacci`, do not answer with `/navigate_to_pose`. Interface types such as `std_msgs/msg/String` are not topic names; never convert them into `/msg/String`.

   Never output these placeholder/example artifacts unless the user task literally contains them: `example_package`, `/unknown`, `/topic`, `/node`, `/msg/String`, `/srv/AddTwoInts`, `/action/Fibonacci`, `/subscribers/services`, `/count`, `path`, `record`, `play`, `with`, `params.yaml`, or `Category: ...` as the only note. These are signs that you copied a template instead of solving the task.

   For batch/exam-style answering, do not map from a category label alone. Read each task sentence and extract concrete arguments from that sentence every time: topic/service/action/node names, package names, executable names, bag paths, YAML file names, policy/keystore names, and requested flags.

   If the task asks to verify, include the second verification command in the answer. If the task asks to "decide", "explain", "why", "risk", "caveat", "interpret", or "what not to do", the answer notes must state the reason/caveat, not just "safe" or "bounded".

3. Use help before unfamiliar options:

```bash
ros2 <command> -h
ros2 <command> <verb> -h
```

4. Place command-level hidden flags correctly:

- `ros2 topic --include-hidden-topics ...` is command-level. Some topic verbs duplicate it, but not all.
- `ros2 service --include-hidden-services ...` is command-level. `list/find` also duplicate it.
- Node/parameter/lifecycle hidden controls are verb-level: `node list -a`, `node info --include-hidden`, `param ... --include-hidden-nodes`, `lifecycle ... --include-hidden-nodes`, `lifecycle nodes -a`.

5. Prefer bounded forms:

- `ros2 topic echo --once ...`
- `ros2 topic pub -1 ...` or `ros2 topic pub --times N ...`; add `--keep-alive N` when testing Transient Local late-subscriber behavior.
- shell `timeout 20s ros2 action send_goal ...`; do not use `action send_goal --timeout` unless installed help explicitly lists it.
- shell `timeout 10s ros2 ...` around commands implemented as indefinite loops.

6. Validate with a second signal. Example: after `topic pub`, check `topic echo --once`; after `param load`, run `param dump`; after `component load` or `component unload`, run `component list`; after `lifecycle set`, run `lifecycle get`; after `bag reindex`, run `bag info`.

7. Prefer command reuse over ad hoc script generation. For bounded capture, use direct `timeout ... ros2 ... >stdout 2>stderr` when `timeout` is known to exist. Do not create a new Python heredoc for every `ros2 topic echo` or `/rosout` task; Python is a fallback for missing `timeout`/`tmux` or for unavoidable custom parsing.

## High-Value Defaults

- Fresh graph snapshot:

```bash
ros2 node list --no-daemon --spin-time 2
ros2 topic list -t --no-daemon --spin-time 2
ros2 service list -t --no-daemon --spin-time 2
```

- Topic type to definition:

```bash
ros2 topic type /topic >topic.type.out 2>topic.type.err
type=$(grep -E '^[A-Za-z_][A-Za-z0-9_]*/(msg|srv|action)/[A-Za-z_][A-Za-z0-9_]*$' topic.type.out | head -1)
[ -n "$type" ] && ros2 interface show "$type"
```

- ROS log capture through `/rosout`:

```bash
ros2 topic echo /rosout rcl_interfaces/msg/Log --qos-reliability reliable --qos-durability transient_local --qos-depth 1000 --no-lost-messages
ros2 topic echo /rosout rcl_interfaces/msg/Log --filter 'm.level >= 30' --no-lost-messages
ros2 topic echo /rosout rcl_interfaces/msg/Log --filter 'm.name == "talker"' --no-lost-messages
ros2 topic echo /rosout rcl_interfaces/msg/Log --field msg --filter '"timeout" in m.lower()' --no-lost-messages
```

`ros2 topic echo` has no arbitrary log format/template option in Humble. Use YAML output, `--csv`, or `--field`; for a custom line format, post-process the output or write a subscriber outside `ros2cli`.

`/rosout` is only the ROS graph log topic. A running node can still write logs to launch stdout/stderr, journald, container logs, or an application log while publishing nothing on `/rosout`, especially when launched with `enable_rosout:=False`. To find which nodes can publish `/rosout`, use `ros2 topic info -v /rosout` first; it is cheaper than repeatedly scanning `--field name`. If `/rosout` has publishers but a target node is absent or a capture window is empty, check `ros2 node info /node_name`; do not conclude "the node is not logging" or "ROS 2 logs cannot be taken" from an empty `/rosout` window alone.

For bounded `/rosout` collection, prefer `timeout` over generated Python when `timeout` is available:

```bash
timeout -s INT 10s ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >rosout.csv 2>ros2.stderr
```

If `timeout` is unavailable and `tmux` is available:

```bash
session="rosout-$(date +%H%M%S)"
tmux new-session -d -s "$session" 'ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >rosout.csv 2>ros2.stderr'
sleep 10
tmux send-keys -t "$session" C-c
```

If tmux does not persist in the current agent runtime, use a detached process with a PID file and explicit cleanup:

```bash
out="rosout_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$out"
sh -c 'setsid ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >"$1/rosout.csv" 2>"$1/ros2.stderr" & echo $! >"$1/pid"' sh "$out"
pid="$(cat "$out/pid")"
ps -p "$pid" -o pid,stat,comm,args >"$out/process.txt"
# later, stop with a literal numeric PID:
# kill -INT <pid-from-$out/pid>
```

For a specific logger, filter in the `ros2` command rather than collecting all names repeatedly:

```bash
tmux new-session -d -s "$session" 'ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --filter '\''m.name == "cocoda_logger_node"'\'' --no-lost-messages >cocoda_logger.csv 2>ros2.stderr'
```

For "which logger emitted the most `/rosout` records in 10 seconds", reuse this fixed shell recipe instead of inventing a new parser:

```bash
out="rosout_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$out"
printf '%s\n' 'timeout -s INT 10s ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages' >"$out/commands.log"
timeout -s INT 10s ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >"$out/rosout.csv" 2>"$out/ros2.stderr"
rc=$?
printf 'exit=%s\n' "$rc" >>"$out/commands.log"
awk -F, 'NF >= 8 {count[$4]++} END {for (name in count) print count[name], name}' "$out/rosout.csv" | sort -nr >"$out/by_logger.txt"
top="$(awk 'NR == 1 {print $2}' "$out/by_logger.txt")"
[ -n "$top" ] && awk -F, -v name="$top" '$4 == name' "$out/rosout.csv" >"$out/top_logger.csv"
```

Humble `--csv` has no header; for `rcl_interfaces/msg/Log`, the useful columns are `stamp.sec, stamp.nanosec, level, name, msg, file, function, line`. Level numbers are `10 DEBUG`, `20 INFO`, `30 WARN`, `40 ERROR`, `50 FATAL`.

Separate middleware stderr from `/rosout` data when collecting logs:

```bash
ros2 topic echo /rosout rcl_interfaces/msg/Log --no-lost-messages >rosout.yaml 2>ros2.stderr
```

If stderr, or in some environments stdout, contains `RTPS_TRANSPORT_SHM Error`, do not classify the `ros2` CLI command as failed from that message alone; use the separate `fastdds-shm-triage` skill. For machine parsing, keep raw stdout/stderr artifacts, strip ANSI color escapes, and filter SHM diagnostic lines out of stdout before parsing ROS YAML or scalar output.

```bash
python3 -c 'import re,sys; ansi=re.compile(r"\x1b\[[0-9;]*[A-Za-z]"); [sys.stdout.write(s) for line in sys.stdin if "RTPS_TRANSPORT_SHM" not in (s:=ansi.sub("", line)) and "Failed init_port fastrtps_port" not in s]' <rosout.raw.yaml >rosout.yaml
```

When using `fastdds shm clean` directly, run it once to remove zombies and a second time to confirm `0 zombie ... cleaned`; continued port errors after that indicate a live IPC, permission, container, or transport configuration issue, not just stale files.

- Safe one-shot publish/observe loop:

```bash
timeout 10s ros2 topic echo --once /topic pkg/msg/Type
ros2 topic pub -1 -w 1 --keep-alive 2 /topic pkg/msg/Type '{field: value}'
```

- Parameter round trip:

```bash
ros2 param list /node
ros2 param dump /node > node.params.yaml
ros2 param load /node node.params.yaml
ros2 param get /node parameter_name
```

- Filesystem-mutating commands:

Use a new output path for `bag record`, `pkg create`, and security keystores/artifacts. `ros2 bag record -o` rejects an existing directory and a stale metadata-less bag directory will make later `bag info`, `bag play`, or `bag convert` fail. `ros2 pkg create` and `ros2 security create_keystore` also fail when the target already exists; choose a unique destination instead of deleting unless deletion was explicitly requested.

## Source Evidence Discipline

When explaining behavior, name the implementation file or symbol. Important anchors:

- CLI framework: `ros2cli/ros2cli/cli.py`, `command/__init__.py`, `entry_points.py`.
- Daemon and discovery: `ros2cli/ros2cli/node/strategy.py`, `node/direct.py`, `node/daemon.py`, `node/network_aware.py`, `daemon/__init__.py`.
- Topic QoS/YAML: `ros2topic/ros2topic/api/__init__.py`, `verb/echo.py`, `verb/pub.py`, `verb/hz.py`, `verb/bw.py`, `verb/delay.py`.
- Parameters: `ros2param/ros2param/api/__init__.py`, `verb/*.py`.
- Services/actions/components/lifecycle: their package `api/__init__.py` and `verb/*.py`.
- Bag/launch/security: `ros2bag/ros2bag/verb/*.py`, `ros2launch/ros2launch/command/launch.py`, `ros2launch/ros2launch/api/api.py`, `launch/launch/launch_service.py`, `sros2/sros2/verb/*.py`.

Do not claim real-time, zero-copy, transport, or production behavior from CLI source alone. Mark those as requiring runtime measurement or lower-layer source evidence.
