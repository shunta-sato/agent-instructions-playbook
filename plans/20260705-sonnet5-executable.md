# Sonnet 5 executability (Phase 2, WS5+WS6) — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Make the two mandatory skills (dev-workflow, quality-gate) and the highest-risk predicates executable by a mid-tier model (Sonnet 5) without frontier-level inference, per the comprehensibility audit in `reports/skillset-review-20260705.md` (GAP G5).
- Follows Phase 1 (PR #80, structure gates). WS7 (output-contract lint) and WS8 (requires manifest) are deferred to a separate PR.

## Scope

### In scope (WS5)
- dev-workflow: replace the routing-priority prose (9 interacting "if the primary question is X" rules) with a first-match-wins precedence table.
- quality-gate: explicit sweep rule (evaluate all items, never stop at first failure) in SKILL + reference + gotcha; rewrite triple/double negatives into positive form (constitution-only NFR line, telemetry line).
- Align "measurable quality drivers" wording in dev-workflow with the checkable definition owned by architecture-decision-analysis.

### In scope (WS6 — thresholds; decisions by supervisor, application delegated to a Sonnet 5 worker)
- design-balance: large class (>400 lines OR >7 public functions OR ≥3 reasons to change), god object/hub (≥3 unrelated dependents AND ≥3 reasons to change), excess layering (pure-forwarding layer OR one operation crossing >3 layers).
- code-smells-and-antipatterns: large class (cross-ref design-balance), long parameter list (>4).
- function-boundary-governor: numeric decision rule on the scoring rubric (every positive ≥1, positive total ≥ 2/3 of max, every risk ≤1, else no-op); checkable textual-similarity test.
- architecture-decision-analysis: measurable = metric + target + measurement method, with contrasting examples; missing any → requirements-engineering first.
- requirements-engineering: ambiguous = testable acceptance criteria cannot be written from the request alone; non-trivial = ≥2 modules OR ≥2 user-visible behaviors OR new domain concept.

### Out of scope / non-goals
- WS7 output-contract lint, WS8 requires-manifest (next PR).
- Vocabulary unification across all 50 skills (glossary WS0b).
- Embedded anti-triggers (Phase 4).

## Progress (WBS)

- [x] (P0) dev-workflow precedence table (first-match-wins) — verify: make verify + routing smoke eval
- [x] (P0) quality-gate sweep rule + negative-form rewrites
- [x] (P1) WS6 threshold application via Sonnet 5 worker — verify: validate_skills.py + supervisor diff review
- [x] (P2) Sonnet 5 routing smoke eval (10 scenario prompts vs expected routing) — verify: 9/10, AC2 met (see Outcomes)
- [x] (P3) PR + verification record

## Decision log

- 2026-07-05: Precedence expressed as a first-match-wins table because ordered-table semantics survive mid-tier execution better than 9 interacting prose rules ("primary question" judgment is replaced by row order).
- 2026-07-05: Threshold values chosen to align with existing anchors (400-line structure budget) so the corpus has one number per concept, not two.
- 2026-07-05: WS6 delegated to a Sonnet 5 worker with fixed threshold decisions (supervisor-owned) — continues piloting the mixed-model operating pattern from the review.

## Surprises & Discoveries

- 2026-07-05: First smoke-eval run scored 7/10, but all three failures were harness bugs (a "list 1-4 skills" cap made a 5-skill expected case unwinnable; chained second-hop skills were excluded by instruction). Lesson for the mixed-model pattern: judge-harness instructions need the same checkable-predicate discipline as the skills themselves.
- 2026-07-05: On rerun, the judge applied precedence row 2 exactly as designed — SQLite-vs-Postgres was routed to `requirements-engineering` first because the prompt lacked a measurement method, demonstrating the WS6 "measurable = metric + target + measurement method" definition working in a mid-tier model.
- 2026-07-05: The single remaining miss (`observability` on the embedded-daemon case) matches the portfolio audit's "observability underfires" finding — Phase 4 signal, not a Phase 2 regression.

## Handoff (update at every stop)

- Current branch: `sonnet5-executable-phase2`
- Next steps: routing smoke eval; PR.

## Validation & Acceptance

- AC1: `make verify` green.
- AC2: Sonnet 5 routing smoke eval — given only the rewritten dev-workflow + trigger-eval scenario prompts, routing decisions match `should_trigger`/`should_not_trigger` on ≥9/10 sampled cases.
- AC3: No semantic regressions in quality-gate (all original criteria still present; only form changed) — supervisor diff review.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: WS5 (precedence table, sweep rule, negative-form rewrites) + WS6 (checkable thresholds in 5 skills, applied by a Sonnet 5 worker from supervisor-fixed decisions; diff-reviewed, zero deviations).
- Routing smoke eval (Sonnet 5 judge, 10 blind cases sampled across core/project-structure/performance/embedded/function-design): **9/10** — AC2 (≥9) met. AC1 `make verify` green. AC3 diff review: insert-only, no semantic regressions.
- What went well: worker applied all thresholds faithfully including auditable rounding (⅔ of 14 → ≥10 with the fraction stated inline); precedence table survived blind mid-tier execution.
- What went wrong: first eval run invalidated by my own harness bugs (cap + missing chain rule) — fixed and rerun.
- Follow-ups / tech debt tickets: WS7 output-contract lint + WS8 requires-manifest (next PR); observability trigger strengthening (Phase 4, see miss above).
