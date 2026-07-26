# Failure Retrospective — Reference

Full procedure detail, closure conditions, LLM Wiki operating rules,
adjacent-skill handoff conditions, and the lint boundary for
`failure-retrospective`. `SKILL.md` is the router; this file is the detail.

## 4. Procedure

### 4.1 Fix evidence

Ground the retrospective in artifacts, not memory: ExecPlan
Decision/Surprises/Handoff entries, commit/revert/diff history, test/build/
benchmark/repro output, quality-gate findings, review comments, delegated
run ID + judge result, bug reports, experiment IDs, artifact/submission
lint findings. Never rewrite the history into a success story.

### 4.2 Attempt sequence (materially different attempts only)

| Attempt | Hypothesis / approach | Evidence sought | Result | Failure class | What changed next |
|---|---|---|---|---|---|
| A1 | | | | | |

- Result enum: `failed | rejected | abandoned | succeeded | inconclusive`
- Failure class enum: `assumption | approach | routing | verification | coordination | environment`

### 4.3 Nature of the failure

For each attempt, record:

- failed invariant
- earliest signal (what was observable at the time, not in hindsight)
- preventability: `preventable | productive-exploration | unknown`
- the concrete difference from the next attempt
- causal confidence: `confirmed | plausible | unknown`
- applies when / does not apply when

Rule: the final attempt succeeding is never, by itself, enough to promote
causal confidence to `confirmed`.

### 4.4 Learning scope

- `task-only` -> retention action `retrospective-only`
- `project-specific` -> `llm-wiki` / `project-instruction` / `local-lint` /
  `local-harness`
- `cross-project-reusable` -> `existing-skill` / `new-skill-candidate` /
  `reusable-lint` / `reusable-harness`

### 4.5 Machine-checkability

`explanatory | model-evaluable | deterministic`

### 4.6 Recurrence search

Search `reports/retrospectives/`, `.agent/wiki/`, `reports/bug-reports/`,
`evals/`. Minimum failure-signature match set: failure class + failed
invariant + earliest signal + affected workflow/boundary.
Recurrence: `first-seen | repeated`. Never treat `repeated` as a one-off.

### 4.7 Disposition (exactly one)

`amend-current-work | harden-repository | no-durable-change | insufficient-evidence`

### 4.8 Retention action (one or more per learning)

`retrospective-only | llm-wiki | project-instruction | existing-skill | new-skill-candidate | local-lint | local-harness | reusable-lint | reusable-harness | observe-first | tracked-follow-up`

Priority order: (1) regression test / replay fixture / oracle
(2) deterministic validator / lint / gate (3) an existing skill's
trigger / anti-trigger / decision rule / output contract
(4) LLM Wiki / project instruction (5) tracked follow-up (6) an explicit
no-durable-change reason. A new skill is the last resort, never the first.

## 5. Closure rules (hard rules)

5.1 Preventable AND deterministic -> one of `local-lint | local-harness |
reusable-lint | reusable-harness` is required. A note-only close is
forbidden.

5.2 Repeated AND preventable -> a docs-only close is forbidden. At minimum
add a lint/harness change or a new observe-first observation mechanism.

5.3 Project-specific AND criticality in `{required-before-action,
submit-blocking}` -> the Wiki alone is insufficient. A project-instruction,
local-lint, or local-harness is also required.

5.4 Cross-project -> an existing-skill absorption judgment is required
before proposing `new-skill-candidate`. Record: the runtime decision delta;
existing skills considered; why a trigger/anti-trigger/reference/
output-contract change is insufficient; positive trigger examples;
near-miss negative examples. `new-skill-candidate` is forbidden unless it
passes the README Skill Delta Gate.

5.5 insufficient-evidence / observe-first -> required fields: the missing
evidence, the next signal to collect, an artifact path, the re-evaluation
condition, and an owner/tracking reference.

5.6 Invalid actions (never sufficient alone): "be more careful",
"communicate better", "test more", "review more carefully", "remember next
time". Every action needs a target path, an owner/tracking ID, a
verification method, and a closure condition.

## 7. LLM Wiki operating rules

Layout: `.agent/wiki/README.md`, `.agent/wiki/index.md`,
`.agent/wiki/<domain-or-component>.md`. No external wiki or DB in v1 —
repository-local Markdown is canonical.

Entry required headings (exact, in order): `# <Project knowledge title>`,
`## Scope`, `## Project knowledge`, `## Applies when`, `## Does not apply
when`, `## Operational consequence`, `## Evidence`, `## Confidence`,
`## Freshness`, `## Promoted learning`.

Fixed fields (present on every entry): `Status: active | superseded |
expired`, `Confidence: confirmed | plausible | unknown`,
`Last verified: YYYY-MM-DD`, `Revisit when:`.

`index.md` links to every entry. Orphan entries, dead links, and duplicate
links are lint findings, not judgment calls.

Seven operating rules:

1. Not one page per task — update the existing component/constraint/
   failure-pattern page instead of creating a new one.
2. Never copy raw timelines or logs into a Wiki entry — link to the
   retrospective pack instead.
3. A general rule does not stay confined to the Wiki — treat it as an
   existing-skill promotion candidate.
4. A critical rule is never Wiki-only — also add a project instruction or a
   local lint/harness.
5. After a rule is promoted to something generic, the Wiki keeps only the
   project-specific applies-when conditions, exceptions, and examples.
6. Never load the whole Wiki at once — read only entries whose scope
   matches the current task's paths/components.
7. `index.md` is the entry point; keep it link-complete (rule above) so
   preflight-engineering and other readers can navigate without a full
   load.

## 10. Adjacent-skill handoffs

Hand off to `bug-investigation-and-rca` only when: multiple failed fixes
were needed; RCA alone would not close a workflow/process failure; a
reusable verification-contract defect was found; or the same failure
signature recurred from a prior retrospective. Do not double-fire this
skill on an ordinary single bugfix that RCA already closes.

Hand off to `research-synthesis` only when: repeated not-evaluable results
accumulated; a defect exists in the experiment harness itself; the same
wrong probe kept getting selected; or a promotion-boundary/evidence-
integrity failure occurred. An ordinary expected-disconfirmed experiment
stays entirely inside `research-synthesis`/`experiment-loop`.

`execution-plans`: at closeout, add a retrospective-trigger evaluation line
to the ExecPlan (`## Outcomes & Retrospective`). When the trigger fires,
the detail lives in the retrospective pack; the ExecPlan carries only a
link, not a duplicated narrative.

`branch-completion`: before discarding or cleaning up a branch that had a
rollback, an abandoned approach, or a repeated failed attempt, evaluate
this skill's trigger first. Do not force a retrospective on every merge or
publish; an unrun retrospective is never an ordinary merge blocker; but
cleanup must never discard evidence from an already-triggered
retrospective.

`preflight-engineering`: treat `.agent/wiki/index.md` as the project-
knowledge inventory entry point; read only entries matching the task's
path/component; reference relevant entries from `.agent/ctx` or the
work-routing map; never copy Wiki body text into `AGENTS.md`.

`quality-gate` / submission evidence: v1 does not add this skill to the
submit gate or to mandatory-trigger branches (this avoids a review cycle
between the two skills). A retrospective-caused change re-enters ordinary
`dev-workflow` + `quality-gate` like any other change.

## Never about people

Never attribute failure to an individual, name a person as a cause, or
grade anyone's performance — the unit of analysis is the process,
verification contract, or routing rule. A draft that reads as an
appraisal is rewritten or discarded.

## Lint boundary

The `learning` artifact checker verifies structure only: required files
and fields present, JSON parses, enum values valid, no duplicate Attempt or
Learning IDs, no empty evidence-ref lists, paths are repo-relative (no
absolute paths, no `..`), the report's retrospective ID matches the
record's, the report cites every Attempt and Learning ID, the 5.1-5.4
closure rules above are structurally satisfied (lint/harness action present
when required, absorption rationale present for `new-skill-candidate`,
etc.), implemented-action target paths exist, planned actions carry a
tracking ref, lint/harness actions carry a verification command,
observe-first actions carry a signal/path/revisit-condition, Wiki required
headings and fixed fields are present, Wiki entries are index-reachable, no
symlinks, and no leftover `<fill>`. It never judges whether a causal claim,
a generalization, or a semantic argument is actually correct — that
judgment stays with the human or the owning skill, never the lint.
