# ROS 2 Humble `bag`, `launch`, and `security`

Source basis: `source-provenance.md` is authoritative for the `rosbag2`, `launch_ros`, `launch`, and `sros2` repository, branch, and commit scope used by this reference.

Do not assume a source checkout path. Use file names below as evidence anchors only.

## `ros2 bag`

Source anchors:

- CLI entry points: `ros2bag/setup.py`, `ros2bag/ros2bag/command/bag.py`.
- Parser and behavior: `ros2bag/ros2bag/verb/*.py`, `ros2bag/ros2bag/api/__init__.py`.
- Runtime transport behavior: `rosbag2_transport/src/rosbag2_transport/recorder.cpp`, `player.cpp`, `qos.cpp`, `topic_filter.cpp`.
- Storage/plugin behavior: `rosbag2_storage/src/rosbag2_storage/default_storage_id.cpp`, `rosbag2_storage_default_plugins/plugin_description.xml`, `rosbag2_storage_mcap/plugin_description.xml`.

Entry point:

- `ros2cli.command`: `bag = ros2bag.command.bag:BagCommand`
- `ros2bag.verb`: `convert`, `info`, `list`, `play`, `record`, `reindex`

Exact Humble option surface:

- `ros2 bag info <bag_path> [-s|--storage STORAGE]`
- `ros2 bag reindex <bag_path> [-s|--storage STORAGE]`
- `ros2 bag list {storage,converter,compressor,decompressor} [--verbose]`
- `ros2 bag convert -i <uri> [storage_id] [-i <uri> [storage_id] ...] -o <output_options.yaml>`
- `ros2 bag play <bag_path> [-s|--storage STORAGE] [--read-ahead-queue-size N] [-r|--rate RATE] [--topics TOPIC ...] [--qos-profile-overrides-path FILE] [-l|--loop] [--remap|-m OLD:=NEW ...] [--storage-config-file FILE] [--clock [Hz]] [-d|--delay SEC] [--disable-keyboard-controls] [-p|--start-paused] [--start-offset SEC] [--wait-for-all-acked TIMEOUT_MS] [--disable-loan-message] [--log-level {debug,info,warn,error,fatal}]`
- `ros2 bag record [TOPIC ...] [-a|--all] [-e|--regex REGEX] [-x|--exclude REGEX] [--include-unpublished-topics] [--include-hidden-topics] [-o|--output URI] [-s|--storage STORAGE] [-f|--serialization-format FORMAT] [--no-discovery] [-p|--polling-interval MS] [-b|--max-bag-size BYTES] [-d|--max-bag-duration SEC] [--max-cache-size BYTES] [--compression-mode {none,file,message}] [--compression-format FORMAT] [--compression-queue-size N] [--compression-threads N] [--snapshot-mode] [--ignore-leaf-topics] [--qos-profile-overrides-path FILE] [--storage-preset-profile PROFILE] [--storage-config-file FILE] [--start-paused] [--use-sim-time] [--log-level {debug,info,warn,error,fatal}] [version-sensitive: --node-name NAME]`

Reader args:

- `bag_path` must exist.
- `-s/--storage` choices come from registered reader plugins; default is empty, meaning auto-detect.

Record constraints implemented in `record.py`:

- Must provide exactly one selection mode: explicit topic list, `--regex`, or `--all`.
- `--all` cannot be combined with explicit topic names.
- `--all` plus `--regex` is allowed but warns that `--all` overrides `--regex`.
- `--exclude` cannot be used with an explicit topic list.
- `--exclude` requires `--all` or `--regex`.
- Output defaults to `rosbag2_YYYY_MM_DD-HH_MM_SS`.
- Existing output directory is rejected.
- `--compression-format` requires `--compression-mode` other than `none`.
- `--compression-mode message` is rejected with `--storage mcap`.
- `--compression-queue-size` must be non-negative.
- `--use-sim-time` and `--no-discovery` are incompatible because `/clock` must be discovered.
- If the recorder creates an empty output directory and records nothing, it removes that empty directory after exit.
- `--node-name` appears in this source snapshot but may be absent from installed Humble `ros2 bag record -h`; verify installed help before using it.

Record behavior:

- Record is long-running until interrupted; use `tmux` for persistent capture or shell `timeout` for bounded tests.
- Use SIGINT for bounded recording (`timeout -s INT`, `tmux send-keys C-c`, or Python `Popen.send_signal(signal.SIGINT)`) so recorder shutdown writes metadata. Avoid dynamic shell `kill "$pid"` recipes in safety-gated agent shells. A hard or too-short stop can leave no `metadata.yaml`, and later `bag info`, `play`, `reindex`, or `convert` will fail.
- Use a unique output directory for every recording. If a previous failed run left an output directory, do not reuse it; an existing directory is rejected before recording starts, and a metadata-less directory causes misleading follow-on `bag info`, `play`, `reindex`, or `convert` failures.
- `--snapshot-mode` delays writes until service `~/snapshot` is called on the recorder node.
- Recorder publishes split events on `events/write_split`.
- `--start-paused` starts paused and the recorder logs that space resumes recording.
- `--use-sim-time` waits for `/clock` before subscribing/writing.
- Default topic polling interval is 100 ms unless `--no-discovery`.
- `--include-hidden-topics` is required for topics with any path token beginning `_`.
- `--include-unpublished-topics` permits topics with no publishers.
- `--ignore-leaf-topics` skips topics with no subscribers.
- Topic filter uses Python/C++ regular expressions through `std::regex_search`, not exact match.

Record QoS:

- Without a QoS override, recorder adapts subscription reliability/durability to publishers.
- If all publishers are Reliable, recorder requests Reliable; otherwise Best Effort.
- If all publishers are Transient Local, recorder requests Transient Local; otherwise Volatile.
- Mixed publishers warn and choose the less strict policy to connect to all compatible endpoints.
- If a new publisher later appears with incompatible Reliability or Durability, recorder warns that messages from that new publisher will not be recorded.

QoS override YAML keys accepted by `ros2bag.api.interpret_dict_as_qos_profile()`:

```yaml
/topic_name:
  history: keep_last
  depth: 10
  reliability: reliable
  durability: volatile
  liveliness: automatic
  deadline:
    sec: 0
    nsec: 0
  lifespan:
    sec: 0
    nsec: 0
  liveliness_lease_duration:
    sec: 0
    nsec: 0
  avoid_ros_namespace_conventions: false
```

Duration values must include both `sec` and `nsec`; negative durations and negative scalar values are rejected.

Play behavior:

- `play` is long-running until the bag ends, loops, or is interrupted.
- `--loop` makes playback indefinite; guard with `tmux` or shell `timeout`.
- `--clock` without a value uses 40 Hz; omitted means no `/clock` publisher.
- `--delay` and `--rate` must be positive where required; `--start-offset` and `--wait-for-all-acked` must be non-negative.
- `--wait-for-all-acked 0` waits forever for acknowledgments and only applies to Reliable publishers.
- Keyboard controls exist unless `--disable-keyboard-controls`: space toggles pause/resume, right arrow plays next, up/down adjusts rate by 10%.
- `--storage-config-file` is limited to read-only storage settings for playback.
- Player creates control services under its node namespace: `~/pause`, `~/resume`, `~/toggle_paused`, `~/is_paused`, `~/get_rate`, `~/set_rate`, `~/play_next`, `~/burst`, `~/seek`.
- `--start-paused` is useful for deterministic service-driven playback with `play_next`, `burst`, or `seek`.

Play QoS:

- Playback offers QoS based on recorded offered profiles.
- If all original publishers had effectively the same compatibility-affecting QoS, playback offers that profile with default history.
- If recorded profiles are mixed, playback warns and falls back to rosbag2 default publisher QoS.

Storage/plugin facts:

- Default storage id in this Humble source resolves through `get_default_storage_id()` and is normally `sqlite3`; installed help may show `sqlite3`, but installed plugin availability is runtime-dependent. Use `ros2 bag list storage --verbose`.
- Built source plugins include `sqlite3` and `mcap`, but a target image may install only a subset.
- `ros2 bag list converter|compressor|decompressor --verbose` reads ament pluginlib resource indices and prints class name, description, type, and base class.

Convert and reindex:

- `convert` requires one or more `-i/--input` entries and one `-o/--output-options`.
- Each input accepts one URI and optional storage id; more than two values raise an argparse type error.
- Output options YAML must have top-level key `output_bags`, containing a sequence of `StorageOptions` and `RecordOptions` dictionaries.
- `bag_rewrite` sets compression queue size to 0 for conversion so conversion does not drop messages due to a bounded compression queue.
- `reindex` requires `bag_path` to be a directory and reconstructs metadata using the selected or autodetected storage.

## `ros2 launch`

Source anchors:

- CLI entry point: `ros2launch/setup.py`, `ros2launch/ros2launch/command/launch.py`.
- API behavior: `ros2launch/ros2launch/api/api.py`.
- Core runtime: `launch/launch/launch_service.py`.
- File loading: `launch/launch/launch_description_sources/*_launch_file_utilities.py`.
- XML/YAML frontend: `launch_xml/setup.py`, `launch_xml/launch_xml/parser.py`, `launch_yaml/setup.py`, `launch_yaml/launch_yaml/parser.py`.

Entry point:

- `ros2cli.command`: `launch = ros2launch.command.launch:LaunchCommand`

Exact Humble option surface:

```bash
ros2 launch [-n|--noninteractive] [-d|--debug] \
  [-p|--print|--print-description | -s|--show-args|--show-arguments] \
  [-a|--show-all-subprocesses-output] \
  [--launch-prefix CMD] [--launch-prefix-filter REGEX] \
  <package_name|launch_file_path> [launch_file_name] [name:=value ...]
```

Additional options may be injected by installed `ros2launch.option` extensions. Inspect installed help before assuming a target image has no extension-specific options.

Modes:

- If the first positional argument is an existing file, `ros2 launch` uses single-file mode.
- Otherwise it uses package-file mode and searches the package share directory recursively for an exact file-name match.
- In package-file mode, zero matches and multiple matches are both errors.
- In single-file mode, the optional `launch_file_name` positional is treated as the first launch argument, not as a second file name.

Launch arguments:

- Launch file arguments must use `<name>:=<value>`.
- Malformed forms such as `foo`, `:=bar`, or `foo:=` are rejected.
- Duplicate arguments use last-one-wins semantics.
- `--launch-prefix` appends launch argument `launch-prefix:=...`.
- `--launch-prefix-filter` requires `--launch-prefix` and appends `launch-prefix-filter:=...`.
- If the user also supplies `launch-prefix:=...` directly, the CLI option wins because it is appended later.

Inspection modes:

- `--show-args` loads the launch description and prints declared arguments, descriptions, defaults, and marks conditionally included arguments with `*`.
- `--print` loads the launch description and prints the introspected launch description.
- Python launch files are imported and `generate_launch_description()` is called for both inspection and execution. Avoid assuming `--show-args` is side-effect free if the launch file has import-time side effects.

Runtime behavior:

- `--noninteractive` defaults to true when stdin is not a TTY.
- `--debug` sets launch logging to DEBUG and enables asyncio debug.
- `--show-all-subprocesses-output` sets environment `OVERRIDE_LAUNCH_PROCESS_OUTPUT=both`.
- `LaunchService.run()` must run in the main thread, catches KeyboardInterrupt, and returns nonzero when async action/event exceptions occur.
- On first SIGINT, launch emits shutdown; repeated SIGINT is ignored by the launch signal handler.
- SIGTERM/SIGQUIT can terminate and may leave orphaned launched processes; use normal shutdown or a process supervisor when possible.

File formats:

- Python launch files use `.py` and must define `generate_launch_description()`.
- XML parser extensions: `launch.xml`, `xml`, `launch`.
- YAML parser extensions: `launch.yaml`, `launch.yml`, `yaml`, `yml`, `launch`.
- For a `.py` file, Python loading is attempted first.
- For other recognized frontend files, frontend loading is attempted and Python is a fallback.
- If extension inference fails, available frontend parsers are tried.

Frontend notes:

- XML root tag must be `launch`.
- YAML must have exactly one root key, normally `launch`.
- XML applies type coercion for attributes; YAML checks that values already have the expected type.
- Frontend substitutions use `$(name args...)` grammar.
- Core exposed tags include `arg`, `let`, `include`, `group`, `executable`, `timer`, `log`, `set_env`, `unset_env`, `append_env`, `reset_env`, `reset`, and `shutdown`.
- ROS-specific frontend extensions from `launch_ros` include `node`, `node_container`, `load_composable_node`, `push_ros_namespace`/`push-ros-namespace`, `set_parameter`, `set_parameters_from_file`, `set_remap`, `set_use_sim_time`, and `ros_timer`.
- ROS-specific substitutions include `$(find-pkg-prefix ...)`, `$(find-pkg-share ...)`, `$(exec-in-pkg ...)`, and `$(param ...)`.
- For `node` XML/YAML: executable is `exec`, package is `pkg`, CLI arguments are `args`, ROS arguments are `ros_args`, remaps are nested `remap` entries, parameters are nested `param` entries.

Use `tmux` for long-running launches after confirming `tmux` exists, especially when collecting logs or preserving process state.

## `ros2 security`

Source anchors:

- CLI entry point: `sros2/setup.py`, `sros2/sros2/command/security.py`.
- Verbs: `sros2/sros2/verb/*.py`.
- Keystore implementation: `sros2/sros2/keystore/*.py`.
- Artifact and policy generation: `sros2/sros2/api/_artifact_generation.py`, `_policy.py`, `sros2/sros2/policy/__init__.py`.

Entry points:

- `ros2cli.command`: `security = sros2.command.security:SecurityCommand`
- `sros2.verb`: `create_keystore`, `create_enclave`, `create_permission`, `generate_artifacts`, `generate_policy`, `list_enclaves`
- Deprecated aliases: `create_key` for `create_enclave`, `list_keys` for `list_enclaves`

Exact Humble option surface:

- `ros2 security create_keystore <ROOT>`
- `ros2 security create_enclave <ROOT> <NAME>`
- `ros2 security create_key <ROOT> <NAME>` deprecated alias
- `ros2 security list_enclaves <ROOT>`
- `ros2 security list_keys <ROOT>` deprecated alias
- `ros2 security create_permission <ROOT> <NAME> <POLICY_FILE_PATH>`
- `ros2 security generate_artifacts [-k|--keystore-root-path ROOT] [-e|--enclaves [NAME ...]] [-p|--policy-files [FILE ...]]`
- `ros2 security generate_policy <POLICY_FILE_PATH> [--spin-time N] [-s|--use-sim-time] [--no-daemon]`

Keystore behavior:

- `create_keystore` creates `public`, `private`, and `enclaves` directories.
- It creates CA key/cert material, symlinks identity/permissions CA files, creates `enclaves/governance.xml`, and signs `enclaves/governance.p7s`.
- A valid keystore must contain `public/permissions_ca.cert.pem`, `public/identity_ca.cert.pem`, `private/permissions_ca.key.pem`, `private/identity_ca.key.pem`, and `enclaves/governance.p7s`.
- `create_keystore` fails if the target is already a valid keystore.
- Use a fresh keystore/artifact path for tests and automation; an existing keystore is an intentional error for `create_keystore`, while `generate_artifacts` may create a keystore only when the selected path is invalid.
- Governance and permissions use current `ROS_DOMAIN_ID`, defaulting to `0`.

Enclave behavior:

- Enclave names are validated using namespace validation and should be absolute names such as `/robot/nav`.
- `create_enclave` creates enclave directory material under `enclaves/<relative enclave path>`.
- It creates/symlinks `identity_ca.cert.pem`, `permissions_ca.cert.pem`, `governance.p7s`, `cert.pem`, `key.pem`, `permissions.xml`, and `permissions.p7s`.
- Default permissions for a newly created enclave are broad wildcard permissions from the packaged default policy.
- `list_enclaves` finds enclaves by locating `key.pem` under the keystore's `enclaves` tree and prints sorted absolute enclave names.

Permission and artifact generation:

- `create_permission ROOT NAME POLICY_FILE_PATH` extracts the matching `<enclave path="NAME">` from the policy file and writes/signs permissions for that enclave; an enclave existing in the keystore is not enough.
- Policy files are XML, support XInclude, and are schema-validated before use.
- `generate_artifacts` uses `ROS_SECURITY_KEYSTORE` when `--keystore-root-path` is omitted.
- If the selected keystore is invalid, `generate_artifacts` creates a new keystore.
- `generate_artifacts -e` creates enclaves directly.
- `generate_artifacts -p` loads policy files, creates enclaves for each policy enclave, and replaces their broad default permissions with policy-derived permissions.

Policy generation:

- `generate_policy` is graph-dependent and uses the normal `NodeStrategy` options.
- It excludes hidden nodes; there is no CLI option in this Humble source to include them.
- If no nodes are detected, it prints a message to stderr and exits `1`.
- If the policy output file already exists, it is loaded and updated; otherwise a new policy root is created.
- It groups permissions by enclave path, node namespace, and node name from `get_node_names_and_namespaces_with_enclaves()`.
- It adds topic publish/subscribe and service request/reply permissions from current graph endpoints.
- Relative forms are shortened when a topic/service belongs under the same node FQN or namespace.

Security environment reminders:

```bash
export ROS_SECURITY_ENABLE=true
export ROS_SECURITY_STRATEGY=Enforce
export ROS_SECURITY_KEYSTORE=<keystore>
```

The `security` CLI creates artifacts; running nodes securely still depends on ROS/RMW security environment variables and launch/run arguments for enclave selection.
