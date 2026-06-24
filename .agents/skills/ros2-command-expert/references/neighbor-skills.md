# Neighbor Skills

Use this reference to keep `ros2-command-expert` from becoming a catch-all ROS 2 skill.

## Use `ros2-command-expert` For

- exact `ros2` command syntax
- CLI option placement
- bounded command execution plans
- interpreting `ros2` stdout/stderr with CLI evidence
- bag, launch, and security CLI operations
- `/rosout` command capture and interpretation limits

## Do Not Use As The Only Skill For

- application code changes: use `dev-workflow`, `test-driven-development`, and `quality-gate`
- ROS 2 executor/callback concurrency design: use `concurrency-ros2`
- broad DDS or transport root cause: use a relevant DDS/Fast DDS investigation skill when available
- Fast DDS SHM root cause: use `fastdds-shm-triage` when available
- production robot operation: require risk gate, user approval, and target-specific safety workflow
- performance, real-time, low-overhead, or production-readiness claims: require measurement and the relevant review skill

## Missing Neighbor Fallback

If `fastdds-shm-triage` is unavailable:

- classify SHM text as transport diagnostic output, not direct CLI failure
- preserve raw stdout and stderr artifacts before any filtering or cleanup
- filter SHM lines only for parsing cleaned ROS output; keep the raw files as evidence
- do not claim root cause without lower-layer evidence
- before suggesting direct cleanup, check `command -v fastdds`
- run `fastdds shm clean` only when `fastdds` exists and the user explicitly asks for SHM cleanup
- run `fastdds shm clean` once to remove zombies and a second time to confirm the result
- report exactly what the two cleanup runs printed and what was cleaned
- do not blindly delete `/dev/shm/fastrtps*`

## Boundary Checks

- A successful `ros2` command proves only the command result in the observed environment.
- A valid command plan does not prove the target robot, controller, or production system is safe.
- A CLI graph snapshot can be stale, incomplete, or domain-specific; record daemon/direct discovery mode before making absence claims.
