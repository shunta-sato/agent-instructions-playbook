# Retrospective Packs

A retrospective pack records the reusable learning from a rollback,
abandoned approach, misrouted work, weak verification, delegation failure,
or rejected completion claim — never a success-only narrative.

## Create a pack

    python scripts/init_artifact.py --kind failure-retrospective --slug YYYYMMDD-<slug>

Creates `reports/retrospectives/YYYYMMDD-<slug>/` with `record.json` and
`report.md` together; without `--force`, a failed invocation removes what
it just created, so no half-pack survives. Under `--force` a mid-way
failure can leave a mixed pack — re-run the command.

## Pack contents

- `record.json` — trigger, attempt sequence, learnings, retention actions,
  and recurrence state (schema in `templates/record.json`).
- `report.md` — the human-readable narrative, citing the retrospective ID
  and every Attempt ID and Learning ID (headings in `templates/report.md`).

## Closure rules (in one paragraph)

A preventable, deterministically checkable failure can never close on
prose alone — it needs a local or reusable lint/harness. A repeated
preventable failure can never close docs-only. Project-specific learning
that is required-before-action or submit-blocking needs a project
instruction or local enforcement, not the wiki alone. Cross-project
learning needs an existing-skill absorption judgment before a new skill is
proposed.

## Skill

See `.agents/skills/failure-retrospective/SKILL.md` for triggers, the full
procedure, and every enum.
