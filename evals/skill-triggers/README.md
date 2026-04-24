# Skill Trigger Evals

These files are lightweight dispatch eval seeds for repository-local skills.

They do not score a model automatically. They define expected skill-routing behavior that can be used by humans, future harnesses, or subagents when reviewing whether a skill description is too broad, too narrow, or overlapping.

## Schema

Each `*.json` file uses:

- `version`: currently `1`
- `cases`: list of eval cases
- `id`: stable case identifier
- `prompt`: realistic user request or task fragment
- `should_trigger`: skill names expected to be relevant
- `should_not_trigger`: skill names expected to stay inactive
- `notes`: optional rationale

## Validation

Run:

```sh
python scripts/validate_skill_trigger_evals.py
```

The validator checks JSON shape and verifies that every referenced skill exists under `.agents/skills`.

## Usage

Use these evals before and after changing skill descriptions or merging skills:

1. Read the prompt only.
2. Decide which skills should load from metadata.
3. Compare against `should_trigger` and `should_not_trigger`.
4. If a near-miss appears, fix the skill description before adding more body text.
