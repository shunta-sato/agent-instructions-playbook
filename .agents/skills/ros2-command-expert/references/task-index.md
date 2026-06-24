# ROS 2 CLI Task Index

Use this first when the user describes a goal and you must choose a `ros2` command. Then read `command-map.md` or `execution-patterns.md` for exact option details.

Rows below are reusable patterns. Replace every example resource name with the exact topic, service, action, node, container, package, executable, parameter, bag, policy, keystore, or enclave named in the task.

## Command Selection Rules

- Parse names literally:
  - A leading-slash token such as `/chatter`, `/fixture_node`, `/fibonacci`, `/ComponentManager`, or `/robot/nav` is a ROS graph/enclave name.
  - An interface type such as `std_msgs/msg/String`, `example_interfaces/srv/AddTwoInts`, or `example_interfaces/action/Fibonacci` is not a topic/service/action name. Never turn its suffix into `/msg/String`, `/srv/AddTwoInts`, or `/action/Fibonacci`.
  - Slash-separated prose such as `publishers/subscribers/services`, `type/count`, or `stdout/stderr` is not a ROS name.
  - Non-slash bag paths such as `sample_bag` and file names such as `policy.xml` are still concrete arguments and must be copied exactly.
- Need current graph state: use `--no-daemon --spin-time 2` where available. For verbs without daemon options, run the default command and cross-check related direct graph commands; do not restart the daemon as a first step.
- Need one sample: prefer `--once`, `--times N`, or an outer timeout. Do not leave `echo`, `hz`, `bw`, `delay`, `service call -r`, `action send_goal`, `bag record`, `bag play --loop`, `launch`, `doctor hello`, or `multicast receive` unbounded.
- Need machine parsing: capture stdout/stderr separately, strip ANSI Fast DDS SHM diagnostics from raw stdout, and use `--no-lost-messages` for `/rosout`.
- Need bounded `/rosout` collection: use direct `timeout ... ros2 topic echo ... >file 2>file` when `timeout` is available. Do not create a new Python heredoc unless `timeout`/`tmux` is unavailable or custom parsing is truly required.
- Need to mutate files: use a fresh output path. Never reuse bag directories, package directories, keystores, or artifact directories.
- Need to validate a mutation: run a second command that observes the resulting state.
- If the task gives concrete names, use those exact names. Do not answer with placeholders such as `/topic`, `/node`, `/service_name`, `/container`, `Type`, `sample_bag`, or `my_pkg`.
- Final resource self-check: every leading-slash ROS name in your answer should either appear in the task, or be a required internal helper path for that exact task (`/rosbag2_player/play_next`, `/rosbag2_recorder/snapshot`, `/rosout`, `/dev/shm`). If not, replace it before answering.
- If the user asks to decide, explain, classify, or identify a risk, include the key reason in `notes`: e.g. "QoS DURABILITY incompatible; inspect with topic info and retry auto-match", "Node not found is graph availability; SHM text is transport noise", "Python launch files are loaded and may have import/generation side effects", "`--wait-for-all-acked 0` can wait forever", or "Humble CSV has no header row".
- Do not answer from category labels alone. If an answer contains `example_package`, `/unknown`, `/msg/String`, `/subscribers/services`, `/count`, `path`, `with`, or `Category: ...`, re-read the task sentence and replace those artifacts with the task's concrete names and a meaningful note.

## High-Frequency Exact Forms for Small Agents

Use these exact forms when the task wording matches:

| Wording cue | Correct command form | Common wrong answer |
| --- | --- | --- |
| "Publish one `std_msgs/msg/String` ... on `/chatter`" | `ros2 topic pub -1 /chatter std_msgs/msg/String '{data: hello}'` | Using `/msg/String` as the topic. |
| "Publish five ... at 2 Hz on `/chatter`" | `ros2 topic pub --times 5 -r 2 -w 1 /chatter std_msgs/msg/String '{data: hello}'` | Omitting `/chatter` or `--times 5`. |
| "List parameters on `/fixture_node` with types" | `ros2 param list /fixture_node --param-type` | Omitting `--param-type`. |
| "Set parameter `label` to literal string `off`" | `ros2 param set /fixture_node label '!!str off'` | Using `/topic` or unquoted `off`. |
| "List transitions for `/lifecycle_fixture`" | `ros2 lifecycle list /lifecycle_fixture` | Running `ros2 lifecycle list` without the node. |
| "Run talker remapped to `/talker_exam`" | `ros2 run demo_nodes_cpp talker --ros-args -r __node:=talker_exam` | Omitting `--ros-args -r __node:=...`. |
| "Inspect metadata for `sample_bag`" | `ros2 bag info sample_bag` | Using a literal word like `path`. |
| "Play `sample_bag` with keyboard controls disabled" | `ros2 bag play sample_bag --disable-keyboard-controls` | Omitting `sample_bag` or the flag. |
| "Print only failed doctor report sections" | `ros2 doctor --report-failed` | Using `--report`. |
| "Action goal with feedback, bounded externally" | `timeout 20s ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci '{order: 5}' --feedback` | Omitting `--feedback` or using `send_goal --timeout`. |
| "Hidden topic types" | `ros2 topic --include-hidden-topics list -t` | Using top-level help. |
| "Hidden service types" | `ros2 service --include-hidden-services list -t` | Using top-level help. |
| "Fresh service type; verb has no daemon options" | `ros2 service type /add_two_ints; ros2 service list -t --no-daemon --spin-time 2` | Appending `--no-daemon --spin-time` to `service type`, or restarting the daemon as a first step. |
| "Capture `/rosout` as CSV without lost-message text" | `ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages` | Omitting `--no-lost-messages`. |
| "Most active `/rosout` logger in the next 10 seconds" | `timeout -s INT 10s ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >rosout.csv 2>ros2.stderr; awk -F, 'NF >= 8 {count[$4]++} END {for (name in count) print count[name], name}' rosout.csv \| sort -nr >by_logger.txt` | Generating a fresh Python parser or claiming no ROS logs from one empty window. |
| "Convert bag using output options YAML" | `printf 'output_bags:\n  - uri: converted_bag\n    storage_id: sqlite3\n    all: true\n' > output_options.yaml; ros2 bag convert -i input_bag sqlite3 -o output_options.yaml` | Omitting the top-level `output_bags:` key. |
| "SHM diagnostics in successful stdout" | Capture stdout/stderr separately, strip ANSI `RTPS_TRANSPORT_SHM` lines, and run `fastdds shm clean; fastdds shm clean`; classify exit 0 plus valid ROS YAML as command success with transport diagnostics | Treating SHM text as CLI failure or omitting cleanup/filtering. |
| "Missing topic definition in noisy environment" | `ros2 topic type /missing_topic >topic.type.out 2>topic.type.err; type=$(grep -E '^[A-Za-z_][A-Za-z0-9_]*/(msg|srv|action)/[A-Za-z_][A-Za-z0-9_]*$' topic.type.out | head -1); [ -n "$type" ] && ros2 interface show "$type"` | Omitting the guarded `interface show` or running `interface show -`. |
| "QoS incompatibility timeout" | `ros2 topic info -v /chatter; timeout 10s ros2 topic echo --once /chatter std_msgs/msg/String` | Repeating incompatible explicit QoS instead of checking QoS and using auto-match. |
| "Late subscriber missed transient-local sample" | `ros2 topic pub -1 --keep-alive 5 /chatter std_msgs/msg/String '{data: latched}' --qos-reliability reliable --qos-durability transient_local --qos-depth 1` | Adding `--keep-alive` but omitting transient local durability. |
| "Publisher visible but `topic hz` says not published" | `ros2 topic list -t; ros2 topic info -v /chatter; timeout 15s ros2 topic hz /chatter` | Running only unbounded `topic hz`. |
| "Unavailable service call may hang" | `ros2 service list -t; ros2 service type /add_two_ints; timeout 10s ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts '{a: 1, b: 2}'` | Calling a service without precheck or bound. |
| "param set SHM noise then Node not found" | `ros2 node list --no-daemon --spin-time 2` and classify as graph/node availability issue, not SHM result | Reporting only the set/get output. |
| "Claim hidden resource absence" | `echo "ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-0}" "RMW_IMPLEMENTATION=${RMW_IMPLEMENTATION:-default}"; ros2 node list -a; ros2 topic --include-hidden-topics list -t; ros2 service --include-hidden-services list -t; ros2 param list --include-hidden-nodes; ros2 node list --no-daemon --spin-time 2` | Checking only visible topics/nodes, or restarting the daemon to refresh the graph. |
| "`/rosout --field msg --filter` substring" | `timeout 10s ros2 topic echo --once /rosout rcl_interfaces/msg/Log --field msg --filter '"timeout" in m.lower()' --no-lost-messages` and note that with `--field msg`, `m` is the selected message string | Treating `m` as the whole log object. |
| "`bag play --wait-for-all-acked 0` in automation" | `timeout 30s ros2 bag play sample_bag --wait-for-all-acked 1000 --disable-keyboard-controls` and note `--wait-for-all-acked 0` can wait forever | Using `0` unbounded. |

## Graph Inventory

| Goal | First command(s) | Expected result / next step |
| --- | --- | --- |
| Check daemon | `ros2 daemon status` | Prints daemon reachability. |
| Start daemon | `ros2 daemon start` | Use only when explicitly managing/diagnosing the daemon, not as graph refresh. |
| Stop daemon | `ros2 daemon stop` | Use only when explicitly managing/diagnosing the daemon or with user approval. |
| Top-level help | `ros2 -h` or `ros2 --help` | Lists top-level command groups. |
| Command help | `ros2 topic -h` | Lists verbs for that command group. |
| Verb help | `ros2 topic echo -h` | Lists verb options. |
| Refresh after env/domain/RMW change | Re-run the target command; for graph checks prefer `ros2 node list --no-daemon --spin-time 2` and matching topic/service direct list commands | Avoid stale daemon graph without stopping the daemon. |
| Daemon restart for explicit daemon diagnosis | `ros2 daemon status; ros2 daemon stop; ros2 daemon start; ros2 daemon status` | Only when the task is daemon diagnosis/recovery or the user explicitly approves restart. |
| Fresh graph snapshot | `ros2 node list --no-daemon --spin-time 2; ros2 topic list -t --no-daemon --spin-time 2; ros2 service list -t --no-daemon --spin-time 2` | Current nodes/topics/services without daemon restart. |
| List visible nodes | `ros2 node list` | Node names. |
| List hidden nodes | `ros2 node list -a` | Includes names with hidden basename. |
| Count nodes/topics/services | `ros2 node list -c`, `ros2 topic list -c`, `ros2 service list -c` | Count only. |
| Inspect a node | `ros2 node info /node_name` | Publishers, subscribers, services, actions. Use `--include-hidden` for hidden endpoints. |
| Hidden topic inventory | `ros2 topic --include-hidden-topics list -t` | Hidden topics included. |
| Hidden service inventory | `ros2 service --include-hidden-services list -t` | Hidden services included. |
| Hidden node parameters | `ros2 param list /_hidden_node --include-hidden-nodes` | Parameters for hidden node. |
| Claim absence robustly | Compare default graph commands with direct graph commands, include hidden flags, record `ROS_DOMAIN_ID` and `RMW_IMPLEMENTATION`; do not restart daemon unless explicitly diagnosing daemon behavior | Avoid false absence from stale graph and avoid making the graph emptier by restarting the daemon. |

## Topics and Interfaces

| Goal | Command recipe | Expected result / next step |
| --- | --- | --- |
| List topics with types | `ros2 topic list -t` | `/topic [pkg/msg/Type]`. |
| List hidden topics | `ros2 topic --include-hidden-topics list` | Includes hidden topic names. |
| Count topics | `ros2 topic list -c` | Topic count. |
| Topic info verbose | `ros2 topic info -v /topic` | Publishers/subscribers and QoS profile details. |
| Find topics by type | `ros2 topic find std_msgs/msg/String` | Matching topic names. |
| Get topic type only | `ros2 topic type /topic` | `pkg/msg/Type` or nonzero/empty if unknown. |
| Safe topic type to definition | `ros2 topic type /topic >topic.type.out 2>topic.type.err; type=$(grep -E '^[A-Za-z_][A-Za-z0-9_]*/(msg|srv|action)/[A-Za-z_][A-Za-z0-9_]*$' topic.type.out | head -1); [ -n "$type" ] && ros2 interface show "$type"` | Never feed empty text or SHM diagnostics to `interface show`. |
| Safe service type to definition | `ros2 service type /service >service.type.out 2>service.type.err; type=$(grep -E '^[A-Za-z_][A-Za-z0-9_]*/(msg|srv|action)/[A-Za-z_][A-Za-z0-9_]*$' service.type.out | head -1); [ -n "$type" ] && ros2 interface show "$type"` | Same guard for services. |
| Show a known interface | `ros2 interface show std_msgs/msg/String` | Message/service/action definition. |
| List message interfaces | `ros2 interface list -m` | Message interfaces only. |
| List packages with services | `ros2 interface packages -s` | Packages that provide service interfaces. |
| List interfaces in package | `ros2 interface package std_msgs` | Interfaces in that package. |
| Prototype payload | `ros2 interface proto example_interfaces/srv/AddTwoInts --no-quotes` | YAML skeleton. |
| Echo one message | `timeout 10s ros2 topic echo --once /topic pkg/msg/Type` | One YAML/field output or timeout. |
| Echo one field | `timeout 10s ros2 topic echo --once /odom nav_msgs/msg/Odometry --field pose.pose.position` | Selected field only. |
| Publish one message | `ros2 topic pub -1 -w 1 /chatter std_msgs/msg/String '{data: hello}'` | Publishes once. |
| Publish N messages | `ros2 topic pub --times 5 -r 2 -w 1 /chatter std_msgs/msg/String '{data: hello}'` | Five messages at 2 Hz. |
| Publish stamped header | `ros2 topic pub -1 /pose geometry_msgs/msg/PoseStamped '{header: auto, pose: {position: {x: 1.0}}}'` | Stamp is updated. |
| Publish time field as now | `ros2 topic pub -1 /clocklike rosgraph_msgs/msg/Clock '{clock: now}'` | Time field set to current time. |
| Late subscriber / latched test | `ros2 topic pub -1 --keep-alive 5 /latched_string std_msgs/msg/String '{data: latched}' --qos-reliability reliable --qos-durability transient_local --qos-depth 1` | Publisher stays alive long enough for late subscriber. |
| Exact QoS echo | First run `ros2 topic info -v /topic`; only then use `ros2 topic echo --once /topic pkg/msg/Type --qos-reliability reliable --qos-durability transient_local` | If incompatible, use auto-match echo instead. |
| Rate/bandwidth/delay | `timeout 15s ros2 topic hz /topic`, `timeout 15s ros2 topic bw /topic`, `timeout 15s ros2 topic delay /stamped_topic` | These may wait or say topic not published despite visible publishers; inspect `topic info -v`. |
| Avoid untrusted filter | Do not run untrusted `--filter`; use trusted simple filters or post-process captured output | `--filter` is Python `eval`. |
| CSV capture | `ros2 topic echo /topic pkg/msg/Type --csv` | No header row in Humble. |
| Empty pipeline to `interface show -` | `ros2 topic type /topic >topic.type.out 2>topic.type.err; type=$(grep -E '^[A-Za-z_][A-Za-z0-9_]*/(msg|srv|action)/[A-Za-z_][A-Za-z0-9_]*$' topic.type.out | head -1); [ -n "$type" ] && ros2 interface show "$type"` | Never run `ros2 interface show -` when upstream may be empty. |

## `/rosout` and Middleware Noise

| Goal | Command recipe | Expected result / next step |
| --- | --- | --- |
| Capture `/rosout` for parsing | `ros2 topic echo /rosout rcl_interfaces/msg/Log --no-lost-messages >rosout.raw.yaml 2>ros2.stderr` | Raw YAML-ish stdout, middleware stderr separate. |
| Bounded `/rosout` CSV capture | `timeout -s INT 10s ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >rosout.csv 2>ros2.stderr` | Exit 124/timeout can be expected after a bounded window; inspect the output file. |
| Bounded `/rosout` when `timeout` is missing but `tmux` exists | `session="rosout-$(date +%H%M%S)"; tmux new-session -d -s "$session" 'ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >rosout.csv 2>ros2.stderr'; sleep 10; tmux send-keys -t "$session" C-c` | Prefer tmux over a fresh Python heredoc. |
| Diagnose tmux "not preserved" claim | `tmux new-session -d -s probe 'sleep 60'; tmux list-sessions; session="tmux-probe-$(date +%H%M%S)"; tmux new-session -d -s "$session" 'command -v ros2; ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >rosout.csv 2>ros2.stderr; printf "rc=%s\n" "$?" >rosout.rc; sleep 60'; sleep 3; tmux capture-pane -pt "$session" -S -200 >tmux-pane.txt` | If the sleep probe persists but the ROS command session disappears, inspect pane/stdout/stderr/rc; likely command/setup/quoting/path issue, not tmux persistence. |
| `/rosout` when tmux is not preserved by the agent runtime | `out="rosout_$(date +%Y%m%d_%H%M%S)"; mkdir -p "$out"; sh -c 'setsid ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >"$1/rosout.csv" 2>"$1/ros2.stderr" & echo $! >"$1/pid"' sh "$out"; pid="$(cat "$out/pid")"; ps -p "$pid" -o pid,stat,comm,args >"$out/process.txt"` | Detached fallback before Python; record PID/output paths and stop later with literal `kill -INT <pid>`. |
| Identify `/rosout` publisher names | `ros2 topic info -v /rosout` | Cheaper than repeatedly scanning `ros2 topic echo --field name`; lists publisher nodes and QoS. |
| Identify whether a node publishes to `/rosout` | `ros2 topic info -v /rosout; ros2 node info /node_name` | If the node has no `/rosout` publisher, its logs may be disabled with `enable_rosout:=False` or routed to launch/journal/container logs. |
| Empty `/rosout` window despite many nodes | `ros2 topic info -v /rosout; ros2 node info /node_name; timeout -s INT 30s ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --no-lost-messages >rosout.csv 2>ros2.stderr` | Empty window means no `/rosout` records observed in that interval, not that nodes are absent or not writing stdout/journal logs. |
| Specific logger `/rosout` capture | `tmux new-session -d -s rosout-log 'ros2 topic echo /rosout rcl_interfaces/msg/Log --csv --filter '\''m.name == "cocoda_logger_node"'\'' --no-lost-messages >cocoda_logger.csv 2>ros2.stderr'` | Use the exact logger name obtained from `ros2 node list`/`ros2 topic info -v`; do not switch to another cocoda node. |
| Custom `"time node level msg"` log lines | Capture `--csv` or YAML first; then post-process. Humble has no `topic echo --format` template. `rcl_interfaces/msg/Log` CSV columns are `stamp.sec, stamp.nanosec, level, name, msg, file, function, line`; levels are 10/20/30/40/50. | Trying to make `ros2 topic echo` itself emit arbitrary templates. |
| `/rosout` capture contaminated by SHM/lost text | `ros2 topic echo /rosout rcl_interfaces/msg/Log --no-lost-messages >rosout.raw.yaml 2>ros2.stderr` then strip ANSI `RTPS_TRANSPORT_SHM` lines from `rosout.raw.yaml` | Do not parse raw stdout directly. |
| Suppress lost-message text | Always include `--no-lost-messages` | Prevents `A message was lost!!!` from mixing into stdout. |
| Strip ANSI SHM diagnostics | `python3 -c 'import re,sys; ansi=re.compile(r"\x1b\[[0-9;]*[A-Za-z]"); [sys.stdout.write(s) for line in sys.stdin if "RTPS_TRANSPORT_SHM" not in (s:=ansi.sub("", line)) and "Failed init_port fastrtps_port" not in s]' <rosout.raw.yaml >rosout.yaml` | Cleaned stdout for parser. |
| Filter warning logs | `timeout 10s ros2 topic echo --once /rosout rcl_interfaces/msg/Log --filter 'm.level >= 30' --no-lost-messages` | One warning-or-higher record. |
| Filter by logger | `timeout 10s ros2 topic echo --once /rosout rcl_interfaces/msg/Log --filter 'm.name == "talker"' --no-lost-messages` | One talker log. |
| Filter selected field | `timeout 10s ros2 topic echo --once /rosout rcl_interfaces/msg/Log --field msg --filter '"timeout" in m.lower()' --no-lost-messages` | With `--field`, `m` is the field value. |
| Explain `--field` filter binding | `timeout 10s ros2 topic echo --once /rosout rcl_interfaces/msg/Log --field msg --filter '"timeout" in m.lower()' --no-lost-messages` | With `--field msg`, `m` is the selected `msg` string, not the whole log object. |
| Classify SHM on success | If exit is 0 and ROS output is present, treat SHM text as transport diagnostics, not CLI failure | Use `fastdds-shm-triage` if transport diagnosis matters. |
| Clean stale SHM | `fastdds shm clean; fastdds shm clean` | Second run should report `0 zombie ... cleaned`. |
| SHM persists with 0 zombies | Check `/dev/shm` usage and live holders: `df -h /dev/shm; df -i /dev/shm; lsof /dev/shm/fastrtps* 2>/dev/null | head; fuser -v /dev/shm/fastrtps* 2>/dev/null | head` | Do not blindly delete `/dev/shm/fastrtps*`. |
| SHM-specific diagnostic run | `FASTDDS_BUILTIN_TRANSPORTS=UDPv4 ros2 node list --no-daemon --spin-time 2` | Diagnostic only, not production fix. |

## Services, Actions, Parameters, Lifecycle

| Goal | Command recipe | Expected result / next step |
| --- | --- | --- |
| List services with types | `ros2 service list -t` | Service/type pairs. |
| List hidden services | `ros2 service --include-hidden-services list` | Includes hidden service names. |
| Find services by type | `ros2 service find example_interfaces/srv/AddTwoInts` | Matching service names. |
| Get service type | `ros2 service type /add_two_ints` | Service type or diagnostic text. |
| Service type to definition | Use safe service type recipe above | Definition only if type found. |
| Call service once | `timeout 10s ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts '{a: 1, b: 2}'` | Response repr or timeout. |
| Repeated service call | `timeout 10s ros2 service call /trigger std_srvs/srv/Trigger '{}' -r 1` | Bound repeated loop. |
| Service may be unavailable | Wrap `ros2 service call ...` in an outer timeout or Python wrapper; absence can wait instead of failing immediately | Avoid indefinite wait. |
| Service unavailable precheck | `ros2 service list -t; ros2 service type /add_two_ints; timeout 10s ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts '{a: 1, b: 2}'` | Precheck type/list before the bounded call. |
| Action info | `ros2 action info -t /fibonacci` | Type and counts. |
| List actions with types | `ros2 action list -t` | Action names and types. |
| Check action internal timeout | `ros2 action send_goal -h | grep -E -- '(-t, --timeout|--timeout)'` | Use internal timeout only if help lists it. |
| Send action goal | `timeout 20s ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci '{order: 5}'` | Bounded wait. |
| Send action goal with feedback | `timeout 20s ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci '{order: 5}' --feedback` | Feedback printed if server responds. |
| List node params with types | `ros2 param list /fixture_node --param-type` | Parameter names/types or `Node not found`. |
| List all params | `ros2 param list` | Parameters grouped by node. |
| List params on node | `ros2 param list /fixture_node` | Parameters for node. |
| Get param value only | `ros2 param get /fixture_node enabled --hide-type` | Value only. |
| Set boolean param | `ros2 param set /fixture_node enabled true` | YAML boolean conversion. |
| Dump params | `ros2 param dump /fixture_node` | YAML to stdout. |
| Load params | `ros2 param load /fixture_node node.params.yaml` | Loads YAML into node. |
| Force string YAML | `ros2 param set /fixture_node label '!!str off'` | Avoid YAML boolean conversion. |
| Dump params bounded | `timeout 20s ros2 param dump /fixture_node` | YAML or `Node not found`. |
| Load and verify params | `ros2 param load /fixture_node node.params.yaml; ros2 param dump /fixture_node` | Verify with second command. |
| SHM plus Node not found | Re-check graph: `ros2 node list --no-daemon --spin-time 2`; do not classify SHM text as param result | Graph dependency issue likely. |
| Lifecycle inspect | `ros2 lifecycle get /lifecycle_fixture; ros2 lifecycle list /lifecycle_fixture --all` | State and transitions. |
| Lifecycle transition | `ros2 lifecycle set /lifecycle_fixture configure; ros2 lifecycle get /lifecycle_fixture` | Verify state after mutation. |

## Components

| Goal | Command recipe | Expected result / next step |
| --- | --- | --- |
| List component types | `ros2 component types` or `ros2 component types demo_nodes_cpp` | Registered plugins. |
| List containers | `ros2 component list --containers-only` | Container node names. |
| Inspect container | `ros2 component list /ComponentManager` | Loaded component IDs. |
| Load and verify | `ros2 component load /ComponentManager demo_nodes_cpp demo_nodes_cpp::Talker -n component_talker -r chatter:=component_chatter; ros2 component list /ComponentManager` | Output includes assigned UID; verify with list. |
| Load then capture UID for unload | `uid=$(ros2 component load /ComponentManager demo_nodes_cpp demo_nodes_cpp::Talker | sed -n 's/.*Loaded component \\([0-9][0-9]*\\).*/\\1/p'); [ -n "$uid" ] && ros2 component unload /ComponentManager "$uid"` | If UID parsing fails, stop and inspect load output; do not guess. |
| Unload and verify | `ros2 component unload /ComponentManager 1; ros2 component list /ComponentManager` | Component removed. |
| Run standalone bounded | `timeout 20s ros2 component standalone demo_nodes_cpp demo_nodes_cpp::Talker` or tmux/Python wrapper | Otherwise it blocks; avoid dynamic shell `kill "$pid"` recipes. |
| Hidden container services | Inspect hidden services with `ros2 service --include-hidden-services list -t` and containers with `ros2 component list --containers-only` | Component manager services are hidden. |

## Packages, Run, Launch

| Goal | Command recipe | Expected result / next step |
| --- | --- | --- |
| Package executables | `ros2 pkg executables demo_nodes_cpp`, add `--full-path` for paths | Executable list. |
| List packages | `ros2 pkg list` | Installed packages. |
| Package prefix/share | `ros2 pkg prefix demo_nodes_cpp`, `ros2 pkg prefix demo_nodes_cpp --share` | Install/share directories. |
| Package XML | `ros2 pkg xml demo_nodes_cpp` | Package XML. |
| Package XML tag | `ros2 pkg xml demo_nodes_cpp -t version` | Matching XML tag. |
| Create package safely | `pkg="my_pkg_$(date +%Y%m%d_%H%M%S)"; ros2 pkg create "$pkg" --build-type ament_python --node-name talker --dependencies rclpy std_msgs` | Fails if target exists; use fresh name. |
| Run executable | `ros2 run demo_nodes_cpp talker --ros-args -r __node:=talker_exam` | Long-running node. Use tmux/timeout as appropriate. |
| Run with prefix | `ros2 run --prefix 'echo' demo_nodes_cpp talker` | Prefix wraps executable. |
| Show launch args | `ros2 launch demo_nodes_cpp talker_listener.launch.py --show-args` | Loads launch description; Python launch may have import/generation side effects. |
| Print launch description | `ros2 launch demo_nodes_cpp talker_listener.launch.py --print` or `ros2 launch /path/file.launch.py --print` | Does not start long-lived processes, but still loads the launch file. |
| Single-file launch mode | If first positional is an existing file, `ros2 launch /path/file.launch.py name:=value` uses single-file mode; a second positional is treated as a launch argument | Do not pass a second launch filename. |
| Show subprocess output bounded | `timeout 20s ros2 launch --show-all-subprocesses-output pkg file.launch.py` | Bound long-running launch. |
| Launch prefix filter | `ros2 launch --launch-prefix 'gdb -ex run --args' --launch-prefix-filter 'talker' pkg file.launch.py` | Filter is invalid without prefix. |

## Bags

| Goal | Command recipe | Expected result / next step |
| --- | --- | --- |
| List storage plugins | `ros2 bag list storage --verbose` | Installed storage plugins. |
| List compression plugins | `ros2 bag list compressor --verbose; ros2 bag list decompressor --verbose` | Compressor/decompressor plugins. |
| Bag info | `ros2 bag info sample_bag` | Metadata and topics. |
| Bag play once | `ros2 bag play sample_bag --disable-keyboard-controls` | Plays until bag ends; bound with timeout/tmux if uncertain. |
| Record safely | `bag="bag_$(date +%Y%m%d_%H%M%S)"; timeout -s INT 30s ros2 bag record -o "$bag" /chatter /rosout; ros2 bag info "$bag"` | Unique directory, SIGINT writes metadata, info verifies. |
| Existing output directory | Root cause is the existing `-o` path. Choose a new path; do not interpret later metadata errors as playback bugs | `bag record` rejects existing output before recording starts. |
| Record hidden topics | `ros2 bag record -a --include-hidden-topics -o "$bag"` | Hidden topics included. |
| Record future/unpublished topics | `ros2 bag record --regex '/camera/.*' --include-unpublished-topics -o "$bag"` | Subscribes to matching unpublished topics. |
| Deterministic play | `ros2 bag play sample_bag --start-paused --disable-keyboard-controls; ros2 service call /rosbag2_player/play_next rosbag2_interfaces/srv/PlayNext '{}'` | Service-driven playback. Also use `burst` or `seek` as needed. |
| Play with clock/remap | `ros2 bag play sample_bag --clock 40 --remap /old:=/new` | Publishes `/clock` and remaps topics. |
| Avoid infinite ack wait | Do not use `--wait-for-all-acked 0` in automation unless intentional; use finite value and an outer timeout | `0` waits forever. |
| Reindex and verify | `ros2 bag reindex sample_bag; ros2 bag info sample_bag` | Metadata reconstructed/validated. |
| Convert bag | `ros2 bag convert -i input_bag sqlite3 -o output_options.yaml` with top-level `output_bags:` | YAML shape must match rosbag2 expectations. |
| Snapshot mode flush | `ros2 service call /rosbag2_recorder/snapshot rosbag2_interfaces/srv/Snapshot '{}'` | Flush buffered snapshot data. |
| MCAP compression caveat | Do not use `--storage mcap --compression-mode message`; use file compression or MCAP storage config for chunk compression | Message compression is not supported for MCAP in this Humble source. |

Minimal `ros2 bag convert` output options shape:

```yaml
output_bags:
  - uri: converted_bag
    storage_id: sqlite3
    all: true
```

Then run:

```bash
ros2 bag convert -i input_bag sqlite3 -o output_options.yaml
```

## Security

| Goal | Command recipe | Expected result / next step |
| --- | --- | --- |
| Create keystore safely | `keystore="keystore_$(date +%Y%m%d_%H%M%S)"; ros2 security create_keystore "$keystore"` | Existing valid keystore is an intentional error. |
| Create/list enclave | `ros2 security create_enclave "$keystore" /robot/nav; ros2 security list_enclaves "$keystore"` | Enclave appears. |
| Generate artifacts from env keystore | `export ROS_SECURITY_KEYSTORE="$keystore"; ros2 security generate_artifacts -e /robot/nav /robot/vision` | Uses env when `-k` omitted. |
| Generate policy from graph | `ros2 security generate_policy policy.xml --no-daemon --spin-time 2` | Hidden nodes are excluded in Humble. |
| Create permission | `ros2 security create_permission "$keystore" /robot/nav policy.xml` | Policy must contain matching `<enclave path="/robot/nav">`; keystore keys alone are not enough. |
| Policy cannot include hidden nodes on Humble | `ros2 security generate_policy policy.xml --no-daemon --spin-time 2` | Humble policy generation excludes hidden nodes; state that limitation explicitly. |

## Diagnostics, Multicast, Extensions

| Goal | Command recipe | Expected result / next step |
| --- | --- | --- |
| Doctor basic/warnings/report | `ros2 doctor`, `ros2 doctor --include-warnings`, `ros2 doctor --report` | Exit 0 can still have warning text on stderr. |
| Doctor failed report sections only | `ros2 doctor --report-failed` | Failed sections only. |
| Doctor hello once | `timeout 10s ros2 doctor hello --once` | One network check. |
| Send multicast probe | `ros2 multicast send --ttl 1` | Sends one datagram. |
| Receive multicast probe | `ros2 multicast receive` | Receives one datagram and exits; start before send. |
| Multicast test | `tmux new-session -d -s multicast-receive 'ros2 multicast receive >multicast.receive 2>multicast.stderr'; ros2 multicast send --ttl 1; cat multicast.receive` | Start receive before send; receive exits after one datagram. |
| No tmux multicast | Use the Python multicast wrapper below | Starts receive before send and bounds cleanup without shell PID/kill control. |
| Extension inventory | `ros2 extension_points`, `ros2 extensions` | Non-verbose inventory. |
| Extension verbose validation | `set -o pipefail; ros2 extension_points -v 2>extension.stderr | sed -n '1,20p'; rc=$?` | Captures traceback and preserves nonzero rc. |
| Fresh shell/subagent setup | `command -v ros2 >/dev/null 2>&1 || { [ -n "${ROS_DISTRO:-}" ] && [ -f "/opt/ros/$ROS_DISTRO/setup.bash" ] && . "/opt/ros/$ROS_DISTRO/setup.bash"; }; command -v ros2` | Do not assume environment survives `bash -lc` or subagents. |
| Check shell timeout exists | `command -v timeout >/dev/null 2>&1 && echo timeout-available || echo timeout-missing` | Do not assume GNU `timeout`. |
| Check tmux exists | `command -v tmux >/dev/null 2>&1 && echo tmux-available || echo tmux-missing` | Choose tmux only if installed. |
| No tmux/no timeout observation | Use the Python bounded capture wrapper below or in `execution-patterns.md` | Avoid dynamic shell `kill "$pid"` recipes; safety-gated shells may reject them before execution. |
| No tmux and no timeout for bag | Use the Python bag wrapper below | Send SIGINT first to preserve metadata without shell PID/kill control. |
| Python timeout fallback | Use the Python wrapper below | Use when shell `timeout` is missing; SIGINT before terminate for bag. |
| Pipe validation | Use `set -o pipefail` or capture `ros2` stdout/stderr/rc before `sed`, `head`, or `grep` | Downstream filters can hide failures. |

Python timeout fallback for bag recording when both `tmux` and shell `timeout` are unavailable:

```bash
python3 - <<'PY'
import signal
import subprocess

p = subprocess.Popen(['ros2', 'bag', 'record', '-o', 'bag_unique', '/topic'])
try:
    p.wait(timeout=10)
except subprocess.TimeoutExpired:
    p.send_signal(signal.SIGINT)
    try:
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        p.terminate()
        p.wait(timeout=5)
PY
ros2 bag info bag_unique
```

Python bounded capture fallback for non-stateful observations such as `/rosout` when both `tmux` and shell `timeout` are unavailable:

```bash
python3 - <<'PY'
import subprocess

cmd = [
    'ros2', 'topic', 'echo', '/rosout', 'rcl_interfaces/msg/Log',
    '--qos-reliability', 'reliable',
    '--qos-durability', 'transient_local',
    '--qos-depth', '1000',
    '--no-lost-messages',
]
with open('rosout.raw.yaml', 'wb') as out, open('ros2.stderr', 'wb') as err:
    try:
        subprocess.run(cmd, stdout=out, stderr=err, timeout=3, check=False)
    except subprocess.TimeoutExpired:
        pass
PY
```

Python multicast fallback when `tmux` and shell `timeout` are unavailable:

```bash
python3 - <<'PY'
import subprocess
import time

with open('multicast.receive', 'wb') as out, open('multicast.stderr', 'wb') as err:
    recv = subprocess.Popen(['ros2', 'multicast', 'receive'], stdout=out, stderr=err)
    time.sleep(1)
    subprocess.run(['ros2', 'multicast', 'send', '--ttl', '1'], check=False)
    try:
        recv.wait(timeout=5)
    except subprocess.TimeoutExpired:
        recv.terminate()
        try:
            recv.wait(timeout=2)
        except subprocess.TimeoutExpired:
            recv.kill()
            recv.wait()
PY
cat multicast.receive
```
