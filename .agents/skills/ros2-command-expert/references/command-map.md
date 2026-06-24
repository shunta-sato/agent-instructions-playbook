# ROS 2 `ros2` Command Map

Source basis: `source-provenance.md` is authoritative for repository, branch, commit, and package-version scope. This file covers the ROS 2 Humble `ros2cli` package family from that manifest. Supplemental Humble command packages are covered in `bag-launch-security.md`.

Use this as the exact command/verb map for ROS 2 Humble. Verify installed CLI help before assuming another ROS distro has identical options. Do not rely on a host-specific checkout path; source paths below are repository-relative evidence anchors.

## CLI Framework

Top-level executable:

- `ros2 = ros2cli.cli:main`
- `_ros2_daemon = ros2cli.daemon:main`

Top-level option:

- `--use-python-default-buffering`: do not force stdout line buffering. Without it, `ros2cli.cli.main()` tries `sys.stdout.reconfigure(line_buffering=True)` or patches `print(..., flush=True)`.

Extension loading:

- Commands are entry points in `ros2cli.command`.
- Verb groups are separate entry points such as `ros2topic.verb`.
- `add_subparsers_on_demand()` creates subparsers for all entry point names but loads only the selected command/verb unless help/completion needs all descriptions.
- Hidden from top-level help but callable: `ros2 extension_points`, `ros2 extensions`.

Common graph options added by `ros2cli.node.strategy.add_arguments()`:

- `--spin-time <float>`: discovery spin time for a direct node; default `0.5` seconds; only applies when not using an already running daemon.
- `-s`, `--use-sim-time`: set the CLI node parameter `use_sim_time`.
- `--no-daemon`: neither spawn nor use the daemon.

Common direct-node options added by `ros2cli.node.direct.add_arguments()`:

- `--spin-time <float>` default `0.5`.
- `-s`, `--use-sim-time`.
- No `--no-daemon`, because the command already uses a direct node.

Humble QoS choices used by `topic echo` and `topic pub`:

- `--qos-profile`: `unknown`, `system_default`, `sensor_data`, `services_default`, `parameters`, `parameter_events`, `action_status_default`
- `--qos-history`: `system_default`, `keep_last`, `keep_all`, `unknown`
- `--qos-reliability`: `system_default`, `reliable`, `best_effort`, `unknown`
- `--qos-durability`: `system_default`, `transient_local`, `volatile`, `unknown`

These are populated by `rclpy.qos.*.short_keys()` at runtime; use installed help when the active environment is not Humble.

## Entry Point Inventory

Top-level commands:

- `action`, `bag`, `component`, `daemon`, `doctor`, `extension_points`, `extensions`, `interface`, `launch`, `lifecycle`, `multicast`, `node`, `param`, `pkg`, `run`, `security`, `service`, `topic`, `wtf`.

Verb groups:

- `ros2 daemon`: `start`, `status`, `stop`
- `ros2 action`: `info`, `list`, `send_goal`
- `ros2 bag`: `convert`, `info`, `list`, `play`, `record`, `reindex`
- `ros2 component`: `list`, `load`, `standalone`, `types`, `unload`
- `ros2 doctor`: `hello`
- `ros2 interface`: `list`, `package`, `packages`, `proto`, `show`
- `ros2 lifecycle`: `get`, `list`, `nodes`, `set`
- `ros2 multicast`: `receive`, `send`
- `ros2 node`: `info`, `list`
- `ros2 param`: `delete`, `describe`, `dump`, `get`, `list`, `load`, `set`
- `ros2 pkg`: `create`, `executables`, `list`, `prefix`, `xml`
- `ros2 security`: `create_enclave`, `create_key` deprecated, `create_keystore`, `create_permission`, `generate_artifacts`, `generate_policy`, `list_enclaves`, `list_keys` deprecated
- `ros2 service`: `call`, `find`, `list`, `type`
- `ros2 topic`: `bw`, `delay`, `echo`, `find`, `hz`, `info`, `list`, `pub`, `type`

Extension point groups registered by this Humble source:

- `ros2cli.command`
- `ros2cli.daemon.verb`
- `ros2action.verb`
- `ros2bag.verb`
- `ros2component.verb`
- `ros2doctor.verb`
- `ros2interface.verb`
- `ros2lifecycle.verb`
- `ros2multicast.verb`
- `ros2node.verb`
- `ros2param.verb`
- `ros2pkg.verb`
- `ros2launch.option`
- `sros2.verb`
- `ros2service.verb`
- `ros2topic.verb`

## Option Quick Reference

Use this section to answer option-placement questions without rereading implementation.

- `ros2 [--use-python-default-buffering] <command> ...`
- `ros2 daemon start [-d|--debug]`
- `ros2 daemon status`
- `ros2 daemon stop`
- `ros2 node list [-a|--all] [-c|--count-nodes] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 node info <node_name> [--include-hidden] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 topic [--include-hidden-topics] list [-t|--show-types] [-c|--count-topics] [--include-hidden-topics] [-v|--verbose] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 topic [--include-hidden-topics] info <topic_name> [-v|--verbose] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 topic [--include-hidden-topics] type <topic_name> [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 topic [--include-hidden-topics] find <topic_type> [-c|--count-topics] [--include-hidden-topics] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 topic [--include-hidden-topics] echo <topic_name> [message_type] [--qos-profile PRESET] [--qos-depth N] [--qos-history KEY] [--qos-reliability KEY] [--qos-durability KEY] [--csv] [--field FIELD] [-f|--full-length] [-l|--truncate-length N] [--no-arr] [--no-str] [--flow-style] [--lost-messages] [--no-lost-messages] [--raw] [--filter EXPR] [--once] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 topic [--include-hidden-topics] pub <topic_name> <message_type> [values] [-r|--rate N] [-p|--print N] [-1|--once | -t|--times N] [-w|--wait-matching-subscriptions N] [--keep-alive N] [-n|--node-name NAME] [--qos-profile PRESET] [--qos-depth N] [--qos-history KEY] [--qos-reliability KEY] [--qos-durability KEY] [--spin-time N] [-s|--use-sim-time]`
- `ros2 topic [--include-hidden-topics] hz <topic_name> [-w|--window WINDOW] [--filter EXPR] [--wall-time] [--spin-time N] [-s|--use-sim-time]`
- `ros2 topic [--include-hidden-topics] bw <topic> [-w|--window WINDOW] [--spin-time N] [-s|--use-sim-time]`
- `ros2 topic [--include-hidden-topics] delay <topic> [-w|--window WINDOW] [--spin-time N] [-s|--use-sim-time]`

`topic echo --csv` has no header row. For `rcl_interfaces/msg/Log` on `/rosout`, useful CSV columns are `stamp.sec, stamp.nanosec, level, name, msg, file, function, line`. `topic echo` has no arbitrary `--format` template option in Humble; use `--csv`, `--field`, YAML, or post-processing.
- `ros2 service [--include-hidden-services] list [-t|--show-types] [-c|--count-services] [--include-hidden-services] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 service [--include-hidden-services] type <service_name>`
- `ros2 service [--include-hidden-services] find <service_type> [-c|--count-services] [--include-hidden-services]`
- `ros2 service [--include-hidden-services] call <service_name> <service_type> [values] [-r|--rate N]`
- `ros2 action list [-t|--show-types] [-c|--count-actions]`
- `ros2 action info <action_name> [-t|--show-types] [-c|--count]`
- `ros2 action send_goal <action_name> <action_type> <goal> [-f|--feedback] [version-sensitive: -t|--timeout N]`
- `ros2 bag info <bag_path> [-s|--storage STORAGE]`
- `ros2 bag reindex <bag_path> [-s|--storage STORAGE]`
- `ros2 bag list {storage,converter,compressor,decompressor} [--verbose]`
- `ros2 bag convert -i <uri> [storage_id] [-i <uri> [storage_id] ...] -o|--output-options <output_options.yaml>`
- `ros2 bag play <bag_path> [-s|--storage STORAGE] [--read-ahead-queue-size N] [-r|--rate RATE] [--topics TOPIC ...] [--qos-profile-overrides-path FILE] [-l|--loop] [--remap|-m OLD:=NEW ...] [--storage-config-file FILE] [--clock [Hz]] [-d|--delay SEC] [--disable-keyboard-controls] [-p|--start-paused] [--start-offset SEC] [--wait-for-all-acked TIMEOUT_MS] [--disable-loan-message] [--log-level {debug,info,warn,error,fatal}]`
- `ros2 bag record [TOPIC ...] [-a|--all] [-e|--regex REGEX] [-x|--exclude REGEX] [--include-unpublished-topics] [--include-hidden-topics] [-o|--output URI] [-s|--storage STORAGE] [-f|--serialization-format FORMAT] [--no-discovery] [-p|--polling-interval MS] [-b|--max-bag-size BYTES] [-d|--max-bag-duration SEC] [--max-cache-size BYTES] [--compression-mode {none,file,message}] [--compression-format FORMAT] [--compression-queue-size N] [--compression-threads N] [--snapshot-mode] [--ignore-leaf-topics] [--qos-profile-overrides-path FILE] [--storage-preset-profile PROFILE] [--storage-config-file FILE] [--start-paused] [--use-sim-time] [--log-level {debug,info,warn,error,fatal}] [version-sensitive: --node-name NAME]`
- `ros2 param list [node_name] [--filter REGEX] [--include-hidden-nodes] [--param-prefixes PREFIX ...] [--param-type] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 param get <node_name> <parameter_name> [--include-hidden-nodes] [--hide-type] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 param set <node_name> <parameter_name> <value> [--include-hidden-nodes] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 param delete <node_name> <parameter_name> [--include-hidden-nodes] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 param describe <node_name> <parameter_names...> [--include-hidden-nodes] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 param dump <node_name> [--include-hidden-nodes] [--output-dir DIR] [--print] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 param load <node_name> <parameter_file> [--include-hidden-nodes] [--no-use-wildcard] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 lifecycle nodes [-a|--all] [-c|--count-nodes] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 lifecycle get [node_name] [--include-hidden-nodes] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 lifecycle list <node_name> [--include-hidden-nodes] [-a|--all] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 lifecycle set <node_name> <transition> [--include-hidden-nodes] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 component list [container_node_name] [--containers-only] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 component types [package_name] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 component load <container_node_name> <package_name> <plugin_name> [-n|--node-name NAME] [--node-namespace NAMESPACE] [--log-level LEVEL] [-r|--remap-rule FROM:=TO] [-p|--parameter NAME:=VALUE] [-e|--extra-argument NAME:=VALUE] [-q|--quiet] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 component unload <container_node_name> <component_uid...> [-q|--quiet] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 component standalone <package_name> <plugin_name> [-n|--node-name NAME] [--node-namespace NAMESPACE] [--log-level LEVEL] [-r|--remap-rule FROM:=TO] [-p|--parameter NAME:=VALUE] [-e|--extra-argument NAME:=VALUE] [-c|--container-node-name NAME] [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 interface list [-m|--only-msgs] [-s|--only-srvs] [-a|--only-actions]`
- `ros2 interface packages [-m|--only-msgs] [-s|--only-srvs] [-a|--only-actions]`
- `ros2 interface package <package_name>`
- `ros2 interface proto <type> [--no-quotes]`
- `ros2 interface show [--all-comments | --no-comments] <type-or->`
- `ros2 pkg list`
- `ros2 pkg executables [package_name] [--full-path]`
- `ros2 pkg prefix <package_name> [--share]`
- `ros2 pkg xml <package_name> [-t|--tag TAG]`
- `ros2 pkg create <package_name> [--package-format {2,3}] [--description TEXT] [--license LICENSE] [--destination-directory DIR] [--build-type {cmake,ament_cmake,ament_cargo,ament_python}] [--dependencies DEP ...] [--maintainer-email EMAIL] [--maintainer-name NAME] [--node-name NAME] [--library-name NAME]`
- `ros2 run [--prefix 'prefix command'] <package_name> <executable_name> [argv...]`
- `ros2 launch [-n|--noninteractive] [-d|--debug] [-p|--print|--print-description | -s|--show-args|--show-arguments] [-a|--show-all-subprocesses-output] [--launch-prefix CMD] [--launch-prefix-filter REGEX] <package_name|launch_file_path> [launch_file_name] [name:=value ...]`
- `ros2 security create_keystore <ROOT>`
- `ros2 security create_enclave <ROOT> <NAME>`
- `ros2 security create_key <ROOT> <NAME>` deprecated alias
- `ros2 security list_enclaves <ROOT>`
- `ros2 security list_keys <ROOT>` deprecated alias
- `ros2 security create_permission <ROOT> <NAME> <POLICY_FILE_PATH>`
- `ros2 security generate_artifacts [-k|--keystore-root-path ROOT] [-e|--enclaves [NAME ...]] [-p|--policy-files [FILE ...]]`
- `ros2 security generate_policy <POLICY_FILE_PATH> [--spin-time N] [-s|--use-sim-time] [--no-daemon]`
- `ros2 doctor [--include-warnings|-iw] [--report|-r | --report-failed|-rf]`
- `ros2 wtf [--include-warnings|-iw] [--report|-r | --report-failed|-rf]`
- `ros2 doctor hello [-t|--topic TOPIC] [-ep|--emit-period N] [-pp|--print-period N] [--ttl N] [-1|--once]`
- `ros2 multicast send [--ttl N]`
- `ros2 multicast receive`
- `ros2 extension_points [-a|--all] [-v|--verbose]`
- `ros2 extensions [-a|--all] [-v|--verbose]`

## `ros2 daemon`

Source: `ros2cli/setup.py`, `ros2cli/command/daemon.py`, `ros2cli/verb/daemon/*.py`, `ros2cli/node/daemon.py`, `ros2cli/daemon/__init__.py`.

- `ros2 daemon start [-d|--debug]`
  - Starts daemon if absent.
  - Uses a 10 second startup timeout.
  - `--debug` keeps daemon output attached to current stdout/stderr.
- `ros2 daemon status`
  - Prints whether XMLRPC daemon is reachable.
- `ros2 daemon stop`
  - Stops daemon if running with a 10 second shutdown timeout.

Daemon implementation details:

- XMLRPC endpoint is `http://127.0.0.1:<11511 + ROS_DOMAIN_ID>/ros2cli/`.
- Daemon process receives `--rmw-implementation`, `--ros-domain-id`, and default idle `--timeout 7200`.
- Daemon serves graph APIs such as node/topic/service/action names, endpoint info, publisher/subscriber counts.

## `ros2 node`

Source: `ros2node/api/__init__.py`, `ros2node/verb/list.py`, `ros2node/verb/info.py`.

- `ros2 node list [-a|--all] [-c|--count-nodes] [--spin-time N] [-s] [--no-daemon]`
  - Lists node full names sorted.
  - `-a/--all` includes hidden nodes.
  - Prints duplicate-name warning to stderr when exact full names repeat.
- `ros2 node info <node_name> [--include-hidden] [--spin-time N] [-s] [--no-daemon]`
  - Prints subscribers, publishers, service servers, service clients, action servers, and action clients.
  - `--include-hidden` includes hidden topics/services/actions and hidden nodes in lookup.
  - If duplicate full node names exist, prints warning that only one node's information is shown.

Name handling:

- Relative node names are normalized to absolute by prepending `/`.
- Hidden node detection uses `rclpy.node.HIDDEN_NODE_PREFIX` on node basename.

## `ros2 topic`

Source: `ros2topic/command/topic.py`, `ros2topic/api/__init__.py`, `ros2topic/verb/*.py`.

Command-level option:

- `ros2 topic --include-hidden-topics <verb> ...`
  - Makes hidden topics visible to command-level parsing/completion and to verbs that use `args.include_hidden_topics`.
  - `list` and `find` duplicate this option at verb level; other verbs rely on command-level placement if they read the parsed field.

Verbs:

- `ros2 topic list [-t|--show-types] [-c|--count-topics] [--include-hidden-topics] [-v|--verbose] [--spin-time N] [-s] [--no-daemon]`
  - `-v` prints separate published and subscribed topic sections with counts.
- `ros2 topic info <topic_name> [-v|--verbose] [--spin-time N] [-s] [--no-daemon]`
  - Looks up topics with hidden topics included.
  - Prints type, publisher count, subscription count.
  - `-v` prints endpoint info including node name/namespace/type/GID/QoS when RMW supports it.
  - Returns `"Unknown topic '<name>'"` when not found.
- `ros2 topic type <topic_name> [--spin-time N] [-s] [--no-daemon]`
  - Prints every type associated with the exact topic name.
  - Returns exit code `1` when not found.
  - Respects `args.include_hidden_topics`; use command-level `ros2 topic --include-hidden-topics type /_hidden`.
- `ros2 topic find <topic_type> [-c|--count-topics] [--include-hidden-topics] [--spin-time N] [-s] [--no-daemon]`
  - Prints topic names whose type list contains `topic_type`.
- `ros2 topic echo <topic_name> [message_type] [QoS options] [format/filter options] [--once] [--spin-time N] [-s] [--no-daemon]`
  - QoS options: `--qos-profile <preset>`, `--qos-depth N`, `--qos-history <short-key>`, `--qos-reliability <short-key>`, `--qos-durability <short-key>`.
  - Output options: `--csv`, `--field path.to.field`, `-f|--full-length`, `-l|--truncate-length N` default `128`, `--no-arr`, `--no-str`, `--flow-style`, `--raw`.
  - Lost-message options: `--lost-messages` deprecated and does nothing except warn; `--no-lost-messages` disables message-lost event reporting.
  - Filter: `--filter <python-expr>` evaluates against `m` (or selected field value); it uses Python `eval`.
  - `--once` exits after first printed message.
  - If `message_type` is omitted, it discovers type from graph; multiple types on one topic raise a runtime error.
  - If no QoS option is supplied, starts from `sensor_data` preset and auto-adjusts reliability/durability to match all existing publishers when possible.
- `ros2 topic pub <topic_name> <message_type> [values] [publish options] [QoS options] [--spin-time N] [-s]`
  - `values` is YAML, default `{}`.
  - Publish options: `-r|--rate N` default `1.0`, `-p|--print N` default `1`, `-1|--once`, `-t|--times N`, `-w|--wait-matching-subscriptions N`, `--keep-alive N` default `0.1`, `-n|--node-name`.
  - `--once` and `--times` are mutually exclusive.
  - `--wait-matching-subscriptions` defaults to `1` for `--once`/`--times`, otherwise `0`.
  - Default publisher QoS is Reliable + Transient Local + depth 1.
  - QoS options match `echo`; `--qos-depth` default is `-1`, meaning do not override.
  - `auto` can populate `std_msgs/msg/Header`; `now` can populate `builtin_interfaces/msg/Time` and header stamps.
  - For Transient Local late-subscriber tests, set `--keep-alive` long enough; `-1` alone can exit before the subscriber appears.
- `ros2 topic hz <topic_name> [--window N] [--filter EXPR] [--wall-time] [--spin-time N] [-s]`
  - Direct node only.
  - Blocks until topic is published; can still wait or print not-published messages when discovery or QoS prevents matching.
  - Uses `qos_profile_sensor_data`.
  - Uses ROS time by default; `--wall-time` switches to system time.
  - Uses raw subscription only when no filter is supplied.
- `ros2 topic bw <topic> [--window N] [--spin-time N] [-s]`
  - Direct node only.
  - Blocks until topic is published; guard with an outer timeout in automation.
  - Uses `qos_profile_sensor_data`, raw subscription, and message byte length.
- `ros2 topic delay <topic> [--window N] [--spin-time N] [-s]`
  - Direct node only.
  - Blocks until topic is published; guard with an outer timeout in automation.
  - Requires message field `header.stamp`; otherwise raises `RuntimeError('msg does not have header')`.
  - Uses `qos_profile_sensor_data`.

QoS short keys come from `rclpy.qos.*.short_keys()` in the installed RCLPY, so confirm with help for the active distro.

### `/rosout` Log Collection with `topic echo`

There is no Humble `ros2 log` command in this source. Collect ROS logs by subscribing to `/rosout`:

```bash
ros2 topic echo /rosout rcl_interfaces/msg/Log --qos-reliability reliable --qos-durability transient_local --qos-depth 1000 --no-lost-messages
```

`rcl_interfaces/msg/Log` fields:

- Severity constants: `DEBUG=10`, `INFO=20`, `WARN=30`, `ERROR=40`, `FATAL=50`.
- Fields: `stamp`, `level`, `name`, `msg`, `file`, `function`, `line`.
- `name` is the logger name from the node's logger, not guaranteed to be the graph full node name. Inspect with `--field name` before writing exact node filters.

Filter examples:

- WARN and above: `ros2 topic echo /rosout rcl_interfaces/msg/Log --filter 'm.level >= 30'`
- One logger: `ros2 topic echo /rosout rcl_interfaces/msg/Log --filter 'm.name == "talker"'`
- Name suffix plus message substring: `ros2 topic echo /rosout rcl_interfaces/msg/Log --filter 'm.name.endswith("talker") and "timeout" in m.msg.lower()'`
- File/function/line: `ros2 topic echo /rosout rcl_interfaces/msg/Log --filter 'm.file.endswith("node.cpp") and m.function == "tick" and m.line >= 100'`
- Message only with substring filter: `ros2 topic echo /rosout rcl_interfaces/msg/Log --field msg --filter '"timeout" in m.lower()'`

Formatting facts from `ros2topic/verb/echo.py`:

- Default output is YAML plus `---` separators through `message_to_yaml()`.
- `--csv` outputs recursive fields separated by commas through `message_to_csv()` and has no header row in `ros2topic`.
- `--field a.b.c` selects a subfield before filtering and printing. With `--field msg`, `m` in `--filter` is the message string, not the full `Log`.
- `--flow-style`, `--no-arr`, `--no-str`, `--truncate-length N`, and `--full-length` affect YAML/CSV conversion, not arbitrary text templates.
- Humble `topic echo` has no `--format` option. For a required custom line format, use `--field`/`--csv` plus an external post-processor, or write a subscriber.
- `--raw` subscribes with raw binary messages; do not combine it with field-based log filtering.

QoS facts for `/rosout` from `rcl/logging_rosout.h`:

- Default `/rosout` publisher QoS is Keep Last depth `1000`, Reliable, Transient Local, lifespan `10s`.
- If `topic echo` starts after publishers exist and no QoS option is supplied, it auto-adjusts to existing publishers. If capture may start before the target node and the expected publisher offers Transient Local durability, pass `--qos-reliability reliable --qos-durability transient_local --qos-depth 1000`.

## `ros2 service`

Source: `ros2service/command/service.py`, `ros2service/api/__init__.py`, `ros2service/verb/*.py`.

Command-level option:

- `ros2 service --include-hidden-services <verb> ...`

Verbs:

- `ros2 service list [-t|--show-types] [-c|--count-services] [--include-hidden-services] [--spin-time N] [-s] [--no-daemon]`
  - Uses `NodeStrategy` with common graph options.
- `ros2 service type <service_name>`
  - Uses `NodeStrategy` but does not add common graph options in this Humble source.
  - Respects command-level `--include-hidden-services`.
  - Returns `1` when not found.
- `ros2 service find <service_type> [-c|--count-services] [--include-hidden-services]`
  - Uses `NodeStrategy` but does not add common graph options in this Humble source.
- `ros2 service call <service_name> <service_type> [values] [-r|--rate N]`
  - Creates its own direct node; no daemon options.
  - `values` is request YAML, default `{}`.
  - Waits indefinitely for service availability if not ready.
  - `-r` repeats at rate Hz; must be greater than zero.
  - Accepts both `pkg/srv/Name` and legacy-style `pkg/Name` type forms by inserting `srv`.

## `ros2 action`

Source: `ros2action/api/__init__.py`, `ros2action/verb/*.py`.

- `ros2 action list [-t|--show-types] [-c|--count-actions]`
  - Uses `NodeStrategy` but this Humble source does not add common graph options.
- `ros2 action info <action_name> [-t|--show-types] [-c|--count]`
  - Prints action client and server counts, then node names unless `--count`.
  - Validates expanded action name.
- `ros2 action send_goal <action_name> <action_type> <goal> [-f|--feedback] [version-sensitive: -t|--timeout N]`
  - `goal` is YAML for the action Goal message.
  - `--feedback` prints feedback message YAML.
  - This inspected Humble source has `-t/--timeout`, but a validated Humble target rejected it as an unrecognized argument. Treat it as version-sensitive and confirm with `ros2 action send_goal -h` before using it.
  - Prefer an outer shell timeout: `timeout 20s ros2 action send_goal ...`.
  - When present, `--timeout N` waits for server and result for up to N seconds; `--timeout 0` returns after a zero-time spin.
  - On SIGINT, tries to cancel an accepted/executing goal and validates the cancel response.

## `ros2 param`

Source: `ros2param/api/__init__.py`, `ros2param/verb/*.py`.

All verbs add common graph options through `NodeStrategy`; most verify node existence with graph discovery, then use a `DirectNode` to call parameter services.

- `ros2 param list [node_name] [--filter REGEX] [--include-hidden-nodes] [--param-prefixes P ...] [--param-type] [--spin-time N] [-s] [--no-daemon]`
  - Without node, lists parameters grouped under each node.
  - `--filter` uses Python `re.match`, not substring search.
  - `--param-prefixes` is sent to `ListParameters.Request.prefixes`.
  - `--param-type` calls `describe_parameters` and appends `(type: ...)`.
- `ros2 param get <node_name> <parameter_name> [--include-hidden-nodes] [--hide-type] [common graph options]`
  - Prints type label and value unless `--hide-type`.
- `ros2 param set <node_name> <parameter_name> <value> [--include-hidden-nodes] [common graph options]`
  - Infers parameter type from YAML parsing of `value`.
- `ros2 param delete <node_name> <parameter_name> [--include-hidden-nodes] [common graph options]`
  - Sends `PARAMETER_NOT_SET` value.
- `ros2 param describe <node_name> <parameter_names...> [--include-hidden-nodes] [common graph options]`
  - Prints descriptor type, description, read-only flag, ranges, and additional constraints.
- `ros2 param dump <node_name> [--include-hidden-nodes] [--output-dir DIR] [--print] [common graph options]`
  - Prints YAML to stdout by default.
  - `--output-dir` is deprecated; if not `.`, writes `<node_full_name_without_slash_with__/..>.yaml`.
  - `--print` is deprecated and only warns.
- `ros2 param load <node_name> <parameter_file> [--include-hidden-nodes] [--no-use-wildcard] [common graph options]`
  - Expects YAML shape `{node_name: {ros__parameters: {...}}}`.
  - By default also applies `/**: {ros__parameters: ...}` wildcard parameters.
  - Node-specific values override wildcard values when both are present.

Parameter YAML inference:

- `true`/`false` and YAML booleans such as `off` become bool.
- Integers, floats, and homogeneous bool/int/float/string arrays become matching parameter types.
- Mixed-type arrays become string parameters containing the original string.
- Invalid YAML parser errors fall back to string.
- Use YAML tags such as `!!str off` to force strings.

Source caveat for this Humble source:

- `ros2param/verb/set.py` and `delete.py` assign `Parameter.name = args.parameter_name` instead of `parameter.name = ...`. If installed behavior differs, trust the installed package; if this exact Humble source is under test, verify `param set/delete` with `param get/list`. `param load` uses `parameter.name` correctly through `parse_parameter_dict()`.

## `ros2 lifecycle`

Source: `ros2lifecycle/api/__init__.py`, `ros2lifecycle/verb/*.py`.

Lifecycle nodes are detected as nodes with `<node>/get_state` service of type `lifecycle_msgs/srv/GetState`.

- `ros2 lifecycle nodes [-a|--all] [-c|--count-nodes] [common graph options]`
  - Lists nodes with lifecycle services.
- `ros2 lifecycle get [node_name] [--include-hidden-nodes] [common graph options]`
  - With no node, prints states for all lifecycle nodes.
  - With one node, returns `Node not found` if not a lifecycle node.
- `ros2 lifecycle list <node_name> [--include-hidden-nodes] [-a|--all] [common graph options]`
  - Default: available transitions.
  - `--all`: transition graph.
- `ros2 lifecycle set <node_name> <transition> [--include-hidden-nodes] [common graph options]`
  - Accepts transition label first, then numeric id as fallback.
  - Prints available transitions when unknown.

## `ros2 component`

Source: `ros2component/api/__init__.py`, `ros2component/verb/*.py`.

Container detection requires all hidden services:

- `<container>/_container/load_node`
- `<container>/_container/unload_node`
- `<container>/_container/list_nodes`

Verbs:

- `ros2 component list [container_node_name] [--containers-only] [common graph options]`
  - Without container, lists containers and their loaded components.
  - With container, prints `<uid>  <full_node_name>`.
  - Component list service waits up to 5 seconds through an internal future/timer loop.
- `ros2 component types [package_name] [common graph options]`
  - Reads `rclcpp_components` ament index resources.
  - With no package, prints every package and component type.
- `ros2 component load <container_node_name> <package_name> <plugin_name> [component args] [-q|--quiet] [common graph options]`
  - Component args: `-n|--node-name`, `--node-namespace`, `--log-level`, `-r|--remap-rule from:=to`, `-p|--parameter name:=value`, `-e|--extra-argument name:=value`.
  - Parameter and extra-argument values use `ros2param.api.get_parameter_value()` YAML inference.
  - Waits 5 seconds for load service.
- `ros2 component unload <container_node_name> <component_uid...> [-q|--quiet] [common graph options]`
  - Waits 5 seconds for unload service.
- `ros2 component standalone <package_name> <plugin_name> [component args] [-c|--container-node-name NAME] [common graph options]`
  - Starts `rclcpp_components` executable containing `component_container`.
  - Default container name is `standalone_container_<12 random hex>`.
  - Loads component into that container, then waits for the container process.

## `ros2 interface`

Source: `ros2interface/api/__init__.py`, `ros2interface/verb/*.py`.

- `ros2 interface list [-m|--only-msgs] [-s|--only-srvs] [-a|--only-actions]`
  - Prints grouped `Messages:`, `Services:`, `Actions:`.
- `ros2 interface packages [-m|--only-msgs] [-s|--only-srvs] [-a|--only-actions]`
  - Lists packages providing interfaces.
  - Options use `action='count'`; multiple occurrences still act truthy.
- `ros2 interface package <package_name>`
  - Lists all interfaces in one package.
- `ros2 interface proto <type> [--no-quotes]`
  - Prints YAML prototype for a message, service Request, or action Goal.
  - Default wraps the YAML in outer double quotes; `--no-quotes` prints raw YAML.
- `ros2 interface show [--all-comments|--no-comments] <type-or->`
  - `-` reads one line from stdin; errors if stdin is a TTY or empty.
  - Shows nested message definitions indented under fields.
  - Default shows comments for the requested interface but not nested comments.
  - `--all-comments` includes nested comments; `--no-comments` strips comments and blank lines.

## `ros2 pkg`

Source: `ros2pkg/api/__init__.py`, `ros2pkg/api/create.py`, `ros2pkg/verb/*.py`.

- `ros2 pkg list`
  - Lists all packages from ament index.
- `ros2 pkg executables [package_name] [--full-path]`
  - Without package, scans every package.
  - Executables are executable files under `<prefix>/lib/<package>`.
- `ros2 pkg prefix <package_name> [--share]`
  - Prints install prefix or share directory.
- `ros2 pkg xml <package_name> [-t|--tag TAG]`
  - Without tag, dumps full `package.xml` XML.
  - With tag, prints `.text` for every matching child tag.
- `ros2 pkg create <package_name> [options]`
  - Options: `--package-format {2,3}` default `3`; `--description`; `--license` default TODO or `?` to list supported SPDX identifiers; `--destination-directory`; `--build-type {cmake,ament_cmake,ament_cargo,ament_python}` default `ament_cmake`; `--dependencies ...`; `--maintainer-email`; `--maintainer-name`; `--node-name`; `--library-name`.
  - Refuses to overwrite an existing directory.
  - `ament_python` package cannot be named `test`.
  - If node and library names match, node is renamed with `_node`.
  - Uses git `user.email` as fallback maintainer email, otherwise `<name>@todo.todo`.

## `ros2 run`

Source: `ros2run/api/__init__.py`, `ros2run/command/run.py`.

Syntax:

```bash
ros2 run [--prefix 'prefix command'] <package_name> <executable_name> [argv...]
```

Behavior:

- Finds executable by basename under `<prefix>/lib/<package>`.
- On Windows, also matches PATHEXT extensions and inserts Python interpreter for `.py`.
- If multiple matching executables exist, raises an error listing full paths.
- `--prefix` is parsed with `shlex.split()` and prepended to the command.
- Child process inherits signals; after exit, nonzero return prints `[ros2run]: ...`.

## `ros2 doctor` and `ros2 wtf`

Source: `ros2doctor/command/doctor.py`, `ros2doctor/api/*.py`, `ros2doctor/verb/hello.py`.

- `ros2 doctor [--include-warnings|-iw] [--report|-r | --report-failed|-rf]`
  - No verb: runs entry points in `ros2doctor.checks`.
  - `--include-warnings` counts warnings as failed checks.
  - `--report` prints every report.
  - `--report-failed` prints reports for failed categories only when failures exist.
- `ros2 wtf ...`
  - Alias to the same `DoctorCommand`.
- `ros2 doctor hello [-t|--topic TOPIC] [-ep|--emit-period N] [-pp|--print-period N] [--ttl N] [-1|--once]`
  - Publishes/subscribes `std_msgs/msg/String` and sends/receives UDP multicast.
  - Default topic `/canyouhearme`, emit period `0.1s`, print period `1.0s`.
  - Summary excludes messages from the same hostname.

Doctor checks/reports:

- Check entry points: `PlatformCheck`, `NetworkCheck`, `TopicCheck`, `QoSCompatibilityCheck`, `PackageCheck`.
- Report entry points: `PlatformReport`, `RosdistroReport`, `NetworkReport`, `RMWReport`, `TopicReport`, `QoSCompatibilityReport`, `PackageReport`.
- Platform and package checks may query rosdistro index/network.
- Network check uses `psutil` and POSIX interface flags when available.
- QoS compatibility check uses `rclpy.qos.qos_check_compatible` for every publisher/subscriber pair.
- Topic check ignores `/parameter_events` and `/rosout`.

## `ros2 multicast`

Source: `ros2multicast/api/__init__.py`, `ros2multicast/verb/*.py`.

- `ros2 multicast send [--ttl N]`
  - Sends one UDP datagram `Hello World!`.
  - Default group `225.0.0.1`, port `49150`.
- `ros2 multicast receive`
  - Waits for one UDP datagram on default group/port.
  - Blocks until datagram or KeyboardInterrupt.

## `ros2 extension_points` and `ros2 extensions`

Source: `ros2cli/command/extension_points.py`, `ros2cli/command/extensions.py`.

- `ros2 extension_points [-a|--all] [-v|--verbose]`
  - Lists registered extension point entry points.
  - `--all` includes failed imports prefixed by `- `.
  - `--verbose` prints module, attributes, and extension point version when available.
  - On some installed Humble images, `--verbose` can traceback with `AttributeError: 'EntryPoint' object has no attribute 'module_name'` because of entry point API differences. Capture rc/stderr and prefer non-verbose output when only inventory is needed.
- `ros2 extensions [-a|--all] [-v|--verbose]`
  - Lists extensions grouped by extension point.
  - Loads and instantiates extensions to validate them unless omitted by errors.
  - `--all` includes failed load/instantiate entries prefixed by `-`.
  - `--verbose` prints module, attributes, and distribution.
  - Do not pipe verbose output directly to `sed`/`head` for validation unless `set -o pipefail` is active; a traceback on stderr can be hidden by the downstream command's zero exit code.
