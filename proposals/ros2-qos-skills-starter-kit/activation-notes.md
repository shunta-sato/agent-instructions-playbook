# Activation notes

This starter kit is intentionally staged under `proposals/`.

## Activate the skill

1. Copy the proposed skill directory:

```bash
mkdir -p .agents/skills/ros2-qos-investigation
cp -R proposals/ros2-qos-skills-starter-kit/skills/ros2-qos-investigation/. .agents/skills/ros2-qos-investigation/
```

2. Copy the trigger eval:

```bash
cp proposals/ros2-qos-skills-starter-kit/evals/ros2-qos-investigation.json evals/skill-triggers/ros2-qos-investigation.json
```

3. Add `ros2-qos-investigation` to the hand-authored Skill Map in `README.md`. A suggested location is the Investigation and safety nets section.

4. Regenerate the machine-readable indexes:

```bash
python scripts/generate_agent_index.py --write
```

5. Run the validation suite:

```bash
python scripts/validate_skills.py
python scripts/validate_skill_trigger_evals.py
python scripts/report_skill_inventory.py --check --format text
python scripts/generate_agent_index.py --check
```

## Suggested README Skill Map line

```markdown
- `ros2-qos-investigation` — source-based ROS 2 / Fast DDS QoS implementation investigation and discussion packets
```

## Suggested first report slug

```text
reports/ros2-qos/reliability-qos-fastdds-investigation.md
reports/ros2-qos/reliability-qos-fastdds-source-trace.md
reports/ros2-qos/reliability-qos-fastdds-experiment-plan.md
```

## Review checklist before activation

- The skill has a distinct job not covered by `concurrency-ros2`, `bug-investigation-and-rca`, or `observability`.
- The trigger eval has at least two positive cases and three near-miss negative cases.
- The output contract produces concrete report artifacts.
- The reference stays short enough to read during an investigation.
- Neighboring skills are routed only when their trigger conditions are present.
