---
name: failure-retrospective
description: "Use at a stable checkpoint or closeout after rollback, abandoned/rejected approaches, material rerouting, repeated failure, two+ materially different attempts, a rejected completion claim, or an explicit lessons-learned request; routes learning to task, project, or cross-project scope. Do not use for clean first-pass work, transient retries, a single bug RCA, one disconfirmed experiment, or submit gating."
metadata:
  short-description: Failure learning and promotion routing
  requires:
    - references/failure-retrospective.md
  templates:
    - templates/report.md
    - templates/record.json
    - templates/llm-wiki-entry.md
---

## Purpose

Turn failure evidence — rollbacks, abandoned approaches, misrouting, weak
verification, delegation failures, rejected completions — into reusable
learning, then route each learning by scope and machine-checkability:
task-only learning stays in the retrospective record; project-specific
learning goes to the LLM Wiki plus local enforcement when checkable;
cross-project learning goes to an existing skill (a new skill only as a
last resort) plus a shared lint/harness when checkable; unclear causality
becomes an observe-first plan. A preventable, deterministically checkable
failure can never close on prose alone.

## When to use (triggers)

At a stable checkpoint or closeout, use this skill when any apply:

- Explicit request: retrospective, postmortem, lessons learned, 振り返り.
- Two or more **materially different attempts** at the same goal (below).
- Rollback, abandonment, or replacement of an implementation, design,
  migration, or workflow.
- A completion claim was rejected by review, quality-gate, or a
  delegated-run judge.
- A discovery changed mode, risk, intent, route, owning skill, or a major
  design assumption.
- A workaround or temporary mitigation was left in place.
- The same failure signature recurred from a prior retrospective.
- Recovery took multiple failed fixes or rejected approaches.

**Materially different attempt** — the hypothesis/assumption,
architecture/implementation approach, mode/risk/intent/route/owning skill,
verification method/oracle/evidence contract, or delegation
boundary/allowed-scope/model role changed between attempts. Re-running the
same command, a network retry, or repeating the same content is not a new
attempt.

## When not to use (anti-triggers)

Do not use for: clean first-pass work; a typo/formatting/one-line fix;
re-running after a transient network failure; a single bug's RCA only; one
registered experiment disconfirmed as expected; merging/publishing/cleaning
up a branch with no failed attempts; ordinary review-comment accept/refute;
success-only praise; final submit-readiness judgment.

Boundary with adjacent skills:

| Skill | Owns |
|---|---|
| `bug-investigation-and-rca` | Single-incident reproduction / root cause / fix / prevention |
| `research-synthesis` | Registered-experiment supported / falsified / still-open synthesis |
| `failure-retrospective` | Multiple attempts, misrouting, weak oracle, delegation failure, rejected completion, reusable process learning |
| `quality-gate` | Submit / no-submit |
| `branch-completion` | Branch/PR lifecycle |

## How to use (procedure)

Full detail, enums, and worked conditions:
`references/failure-retrospective.md`.

1. Fix evidence (ExecPlan Decisions/Surprises/Handoff, diffs, test/build/repro
   output, gate findings, review comments, delegated run ID + judge result,
   bug reports, experiment IDs, artifact/submission lint findings). Never
   rewrite history into a success story.
2. Reconstruct the attempt sequence for materially different attempts only
   (attempt table; Result / Failure-class enums).
3. Characterize each failure: invariant, earliest signal, preventability,
   contrast with what changed next, causal confidence, applies-when /
   does-not-apply-when. A final attempt succeeding never alone promotes
   causal confidence to `confirmed`.
4. Classify learning scope: task-only / project-specific /
   cross-project-reusable.
5. Classify machine-checkability: explanatory / model-evaluable /
   deterministic.
6. Search for recurrence (`reports/retrospectives/`, `.agent/wiki/`,
   `reports/bug-reports/`, `evals/`) by failure-class + failed-invariant +
   earliest-signal + affected boundary; mark first-seen or repeated.
7. Decide exactly one disposition: `amend-current-work` |
   `harden-repository` | `no-durable-change` | `insufficient-evidence`.
8. Assign one or more retention actions per learning, in priority order:
   regression test/fixture/oracle -> deterministic lint/gate -> existing
   skill's trigger/anti-trigger/decision-rule/output-contract ->
   LLM Wiki/project instruction -> tracked follow-up -> explicit
   no-durable-change reason. A new skill is the last resort.

## Closure rules (hard)

- Preventable + deterministic -> a local or reusable lint/harness is
  required; a note-only close is refused.
- Repeated + preventable -> docs-only close is refused; at minimum add a
  lint/harness or an observe-first mechanism.
- Project-specific + criticality `required-before-action`/`submit-blocking`
  -> Wiki alone is insufficient; add a project instruction or local
  lint/harness.
- Cross-project -> judge existing-skill absorption before proposing a new
  skill; record the runtime decision delta, skills considered, why
  trigger/anti-trigger/reference/output-contract changes are insufficient,
  and positive/near-miss examples. No `new-skill-candidate` without passing
  the README Skill Delta Gate.
- Insufficient-evidence / observe-first -> record the missing evidence, the
  next signal to collect, an artifact path, a re-evaluation condition, and
  an owner/tracking reference.
- Invalid actions: "be more careful", "communicate better", "test more",
  "review more carefully", "remember next time". Every action needs a
  target path, an owner/tracking ID, a verification method, and a closure
  condition.

## Output expectation

Produce a retrospective pack at `reports/retrospectives/YYYYMMDD-<slug>/`
(`record.json` + `report.md`), bootstrapped with:

```
python scripts/init_artifact.py --kind failure-retrospective --slug YYYYMMDD-<slug>
```

Start with: `Disposition: <amend-current-work | harden-repository | no-durable-change | insufficient-evidence>`

`record.json` follows `templates/record.json`; `report.md` follows
`templates/report.md` and its required heading set, and must cite the
retrospective ID plus every Attempt ID and Learning ID. When
project-specific learning is promoted, add or update a
`.agent/wiki/<domain>.md` entry from `templates/llm-wiki-entry.md` — never
one page per task.
