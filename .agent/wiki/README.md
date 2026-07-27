# LLM Wiki

Repository-local, project-specific knowledge for this repository only — not
a general software-engineering knowledge base, and not task-scoped
narrative (that belongs in a `reports/retrospectives/` pack instead). No
external wiki or database backs this in v1: every entry is a Markdown file
here, and this repository-local set is canonical.

## What belongs here

Constraints, exceptions, and operational consequences that hold for *this*
project specifically. A rule that generalizes across projects is an
existing-skill promotion candidate, not a wiki entry.

## Seven operating rules

1. Not one page per task — update the existing component/constraint/
   failure-pattern page instead of creating a new one.
2. Never copy raw timelines or logs into an entry — link to the
   retrospective pack instead.
3. A general rule does not stay confined here — treat it as an
   existing-skill promotion candidate.
4. A critical rule is never wiki-only — also add a project instruction or a
   local lint/harness.
5. After a rule is promoted to something generic, keep only the
   project-specific applies-when conditions, exceptions, and examples here.
6. Never load the whole wiki at once — read only entries whose scope
   matches the current task's paths/components.
7. `index.md` is the entry point; keep it link-complete so readers can
   navigate without a full load.

## Entry contract

Every entry (any file here other than this README and `index.md`) follows
`templates/llm-wiki-entry.md` from `.agents/skills/failure-retrospective/`
and carries, in order: `# <title>`, `## Scope`, `## Project knowledge`,
`## Applies when`, `## Does not apply when`, `## Operational consequence`,
`## Evidence`, `## Confidence`, `## Freshness`, `## Promoted learning`, plus
the fixed fields `Status`, `Confidence`, `Last verified`, `Revisit when`.

## How entries are created

An entry is created when a `failure-retrospective` learning's retention
action is `llm-wiki`: copy `templates/llm-wiki-entry.md`, fill it in for the
component, constraint, or failure pattern involved, and add a link from
`index.md`.

## Structure lint

`python3 scripts/lint_artifacts.py` checks this directory's structure only
— required files, headings, fixed fields, and index reachability — never
whether the recorded knowledge is actually true or correctly scoped.
