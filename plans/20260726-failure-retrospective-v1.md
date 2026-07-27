# Failure Retrospective and Learning Promotion v1

## Purpose / big picture

Add a `failure-retrospective` skill that extracts reusable learning from
failures (rollbacks, abandoned approaches, misrouting, weak verification,
delegation failures, rejected completions) and routes each learning by scope
and enforceability: task-only → the retrospective record; project-specific →
LLM Wiki plus local enforcement when machine-checkable; cross-project →
existing-skill absorption first, plus shared lint/harness when
machine-checkable; unclear causality → observe-first. The center of gravity
(user directive, 2026-07-26): a preventable, deterministically checkable
failure can never be closed with prose alone.

## Scope

In: new skill package (SKILL.md + reference + 3 templates), retrospective
pack artifact (`reports/retrospectives/<slug>/record.json+report.md`),
LLM Wiki scaffold (`.agent/wiki/`), `learning` checker in the artifact-lint
family + registry kinds, `init_artifact.py` multi-file-pack support,
adjacent-skill wiring (execution-plans, branch-completion,
bug-investigation-and-rca, research-synthesis, preflight-engineering),
trigger + behavior eval seeds, full routing A/B measurement, behavior-eval
subject runs, workflow-contract review, adversarial review, submission
evidence, branch completion with learning capture.
Out (v1 non-goals, binding): external wiki services, vector/embedding
search, automatic skill generation, unapproved central-skill rewrites from
retrospectives, mandatory retrospectives on all tasks, success-only
retrospectives, performance appraisal, new modes/intents, retrospective as
submit blocker, full initializer refactor, causality judged by lint,
always-on wiki context.

## Constraints and quality targets

Delivery mode, high risk, intent=feature. Gates never weaken; eval
expectations never edited to improve scores; machine-checkable closure rule
applies to this change itself. New artifacts must be lint-clean — no new
baseline entries to hide findings. SKILL.md within context budget (≤150
cap class); required reference ≤400. Routing metrics must be measured
before/after on the full corpus under identical conditions; regressions are
repaired via description/anti-trigger/handoff first, never via expectation
edits without an adjudicated rules-alignment rationale. Quality bar for
default visibility: ≥2 positive / ≥3 negative trigger cases (spec ships
5/6). Commit messages in English; Japanese prose under japanese-tech-writing.

## Context and orientation

Base: current main b66c946 (lint-migration Waves 0-2 + Opus 5 promotion all
merged). Existing machinery this builds ON: `.agents/artifact-registry.json`
+ `scripts/lint_artifacts.py` (checker registry: docs/packs → add
`learning`), `scripts/init_artifact.py` (single-file kinds → add one
multi-file pack kind), `scripts/run_routing_eval.py` +
`evals/routing-runs/RUNBOOK.md` (212-case corpus, isolated subjects),
`scripts/run_behavior_eval.py` + `evals/behavior-runs/`, submission
evidence (`submission_run.py`/`lint_submission.py`), quality-gate reduced to
judgment + lint pointers. Boundary contract (binding):
bug-investigation-and-rca owns single-failure RCA; research-synthesis owns
experiment-ledger synthesis; failure-retrospective owns multi-attempt /
misrouting / weak-oracle / delegation-failure / rejected-completion process
learning; quality-gate owns submit; branch-completion owns lifecycle.

## Design

The user directive of 2026-07-26 is the binding spec (sections 1-19):
skill frontmatter/trigger/anti-trigger text, attempt and learning object
schemas with fixed enums, closure rules 5.1-5.6, pack layout and report
headings, wiki page contract and index, `learning` checker's mechanical
check list (and its explicit limit: no semantic/causal judgment), initializer
pack semantics (no overwrite, --force, no partial creation, unsafe-slug
rejection), adjacent wiring including the not-a-merge-blocker rule for
branch-completion, and v1 exclusion of quality-gate/submission-evidence
coupling (no cycles). Visibility starts as `default` (hypothesis); the
routing A/B decides whether to fall back to explicit-only + handoffs.
The AGENTS.md wiki bootstrap line ships only if the routing/context A/B
supports it. Registry entries are authored by the supervisor after the
checker module lands (checker-name resolution is fail-closed).

## Validation and acceptance

Acceptance = directive §17 items 1-17, verified by: unit tests (§15 lists),
`make verify`, artifact lint clean on the new pack kinds, routing A/B report
(recall / compliance / co-fire / confusion / surface size / new-skill
accuracy / adjacent boundaries), behavior-eval subject runs on all new
cases (model+commit recorded, responses never rewritten), workflow-contract
review with Decision submit, adversarial review findings resolved and
re-verified, clean submission evidence record, branch completion record
with learning capture.

## Progress (WBS)

- [x] W-A: skill package + trigger/behavior eval seeds (run c1a60103;
      SKILL.md 133 lines, reach 322, quality bar met with zero warnings)
- [x] W-B: `learning` checker + lint_artifacts wiring + checker unit tests
      (run 3b812531; two modules 383+186 lines, 40 tests)
- [x] W-C: init_artifact multi-file pack + unit tests (run 9bd9f356;
      write-then-rollback pack creation, 10 tests)
- [x] Supervisor: registry kinds added (failure-retrospective + llm-wiki);
      record.json template aligned with the checker's §5.5 fields
- [x] W-D: wiki scaffold + retrospectives README + adjacent skill wiring
      (run 068f8988; 5 skills wired additively, AGENTS.md untouched)
- [x] Docs: README skill map/catalog, REFERENCES.md, CHANGELOG, indexes,
      symlinks
- [x] Routing A/B (full corpus, 25+6 isolated Sonnet subjects): common-212
      recall 88.97% -> 88.97% (run2, matched), compliance 98.62 -> 98.34,
      co-fire 3.349 -> 3.274; new cases 9/9 recall, zero common-case
      fires; run-1 dip adjudicated as per-subject variance — the initial
      repacking mechanism was DISPROVED by the adversarial review (the
      cluster batch is byte-identical across variants) and the report
      corrected; the decision-carrying evidence is the zero-fire result
      (evals/routing-runs/20260727-failure-retrospective-ab-report.md)
- [x] Behavior eval: run 1 (7 subjects) had a zero-denominator decision
      metric (F3, corrected honestly); run 2 after the Disposition-marker
      fix measures decision accuracy 7/7 on a real denominator,
      output-contains 27/33 with rotating fragment misses
      (evals/behavior-runs/20260727-failure-retrospective-run2-sonnet-5.json)
- [x] Workflow-contract review: three rounds, Decision=submit
      (reports/workflow-contract-review/20260727-failure-retrospective-v1.md;
      runs 9c423e4c / 1ebcb5a5 / eedb3e47)
- [x] Opus adversarial review (run 9c423e4c): integrate-after-fixes,
      3 blockers (F1 closure-rule evasions, F2 inert fill sentinel, F3
      zero-denominator decision metric) + F4-F9 + nits; all blockers and
      should-fixes applied with regression tests; F4 corrected this
      record's own variance-mechanism claim; workflow-contract report at
      reports/workflow-contract-review/20260727-failure-retrospective-v1.md;
      round-2 found F16 (the F7 fix itself failed open on unresolvable
      attempt_refs), fixed fail-closed with a both-halves regression test;
      round-3 verdict integrate-as-is, Decision=submit (run eedb3e47)
- [x] First real retrospective pack recorded and lint-clean
      (reports/retrospectives/20260727-retrospective-v1-shipping/ — the
      rejected-completion-claim trigger fired on this wave itself)
- [ ] quality-gate, submission evidence, branch completion, PR (§19 report)

## Surprises and discoveries

- Two of the three blocking review findings were introduced or left by
  FIXES, not by the original change (F16 came out of the F7 repair). The
  reviewer caught both only by re-running its original adversarial probes
  after each round — recorded as learning L1 in the wave's own first
  retrospective pack.
- The behavior harness silently reported decision accuracy 1.0 on a
  zero denominator when no case declared expected_decision (F3) — the
  same trap the harness README already documented for a different skill.
- preflight-engineering's SKILL.md sits exactly at its ratchet cap
  (166/166), so the wiki-inventory rule went into its resources-tier
  reference (repo-inspection-output-template.md) instead of the SKILL
  body — a conditional-load placement, accepted to avoid breaching the
  cap; the adversarial review is asked to weigh whether the load
  condition covers the inventory moment.

## Decision log

- 2026-07-26: visibility=default as starting hypothesis; explicit-only
  fallback only on measured co-fire/discovery regression (directive §1/§14).
- 2026-07-26: AGENTS.md bootstrap line is measurement-gated, not
  unconditional (directive §10).
- 2026-07-26: registry entries supervisor-authored after checker lands
  (fail-closed checker resolution; Wave-1 precedent).
- 2026-07-27: A/B decisions — visibility=default confirmed (zero false
  fires, surface +0.8%); AGENTS.md wiki bootstrap line NOT added (no
  measurement signal; directive makes it measurement-gated).
- 2026-07-26: R-B escalations adjudicated. (1) Closure rules 5.1/5.2
  correlate at RECORD level (any preventable attempt x deterministic
  learning) — the schema has no attempt-to-learning link, and the
  record-level reading is the only guess-free one; it over-flags safely.
  Accepted; the adversarial review is asked to re-examine it. (2) §5.5's
  observe-first fields (signal, artifact_path, revisit_condition) are
  additive retention-action fields; the record.json template now documents
  them. (3) The report-heading check and wiki duplicate-link check exceed
  §8's literal list but are grounded in §6/§7 text — kept.

## Handoff

- 2026-07-26: branch `failure-retrospective-v1` created from main b66c946.
  This plan + the user directive are the binding inputs to worker briefs.

## Outcomes and retrospective

- What shipped / merged: the failure-retrospective skill package, learning
  artifact checker family (3 modules) + 2 registry kinds, multi-file pack
  initializer, LLM Wiki scaffold, adjacent wiring in 5 skills, 11 trigger
  + 7 behavior eval seeds, full routing A/B + 2 behavior runs, the
  three-round contract review, and this wave's own first retrospective
  pack. Quantitative targets vs outcomes: SKILL.md 135/150 lines, reach
  324/400; common-corpus recall 88.97% -> 88.97% (matched run) vs the
  no-regression target; new-case recall 9/9 vs the quality bar; behavior
  decision accuracy 7/7 (run 2, real denominator).
- Failed, rejected, or abandoned attempts: the F7 closure-scoping fix was
  rejected in round-2 review (F16 fail-open) and amended; the run-1
  routing dip's repacking explanation was retracted after being disproved.
- Failure retrospective:
  - report: reports/retrospectives/20260727-retrospective-v1-shipping/
- Remaining follow-ups / debt: F11 (Skill Delta Gate machine-link), F12
  (no-durable-change lightweight exit), F14 (wiki dead-link vs traversal
  conflation), applies_when/does_not_apply_when not yet required fields,
  findings-phrase fragment calibration (rotating misses), AGENTS.md wiki
  bootstrap line stays measurement-gated for a future campaign.
