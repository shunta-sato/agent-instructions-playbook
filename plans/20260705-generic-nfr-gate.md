# Generic NFR gate (non-embedded) — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Close the NFR asymmetry flagged by the owner: embedded work has a full pipeline (characterization → budgets → calibration → harness → nfr-gate + a no-measurement-no-claim rule), while non-embedded NFRs had only fragments — `requirements-engineering` could define measurable targets (metric + target + measurement method) but nothing verified them at exit, and "fast/scalable" claims were blocked only for embedded work.
- Approach: generalize the two proven embedded patterns instead of adding new skills (portfolio stays lean).

## Scope

### In scope
- quality-gate (SKILL + reference): (1) declared measurable quality/NFR targets must record measured value vs. target, or an explicit `not-measured`/`unmet` entry with reason — silently unmeasured/unmet is `no-submit` (mirrors the ExecPlan quantitative-targets rule); (2) non-embedded performance/reliability claims (fast, low-latency, scalable, high-throughput, reliable, production-ready) are blocked without measurement evidence or an explicit `provisional`/`not-measured` limit (generalizes the embedded claim rule).
- requirements-engineering: targets are recorded in a gate-checkable Quality Targets list (`metric | target | measurement method | measured result or not-measured reason`); added to Output expectation.
- Eval seeds: 3 trigger cases (declared target routes generic, vague words route to requirements-engineering first, physical target constraint still routes embedded) + 2 quality-gate behavior cases (claim-without-measurement → no-submit; measured-target → submit). Delegated to the `playbook-worker` custom agent — its first production run since the Claude Code wiring landed.

### Out of scope / non-goals
- A generic `nfr-design` skill (option 3 from the assessment) — deferred until 1+2 prove insufficient in practice.
- New measurement tooling; the gate checks recorded evidence, it does not run benchmarks.

## Progress (WBS)

- [x] (P0) quality-gate target-verification + generalized claim rule (SKILL + reference)
- [x] (P0) requirements-engineering Quality Targets list (step 9b + Output expectation)
- [x] (P1) eval seeds via playbook-worker with run evidence
- [x] (P2) make verify + PR

## Decision log

- 2026-07-05: Generalized existing embedded rules rather than adding a generic nfr-design skill — the portfolio audit showed skill-count growth is itself a cost, and the gate is where the enforcement gap was.
- 2026-07-05: Routing untouched — `requirements-engineering` already triggers on "explicit quality/NFR target"; the missing half was exit verification only.

## Surprises & Discoveries

- (fill as found)

## Handoff (update at every stop)

- Current branch: `generic-nfr-gate`
- Follow-ups: consider a generic `nfr-design` skill only if Quality Targets lists prove too weak for multi-attribute NFR work (watch real usage).

## Validation & Acceptance

- AC1: `make verify` green including the new eval seeds.
- AC2: worker run recorded in `.agents/runs/agent-runs.jsonl` with explicit run_id and passing validations (the delegated-evidence rule applied to our own delegation).

## Outcomes & Retrospective (fill when done)

- What shipped / merged:
- What went well:
- What went wrong:
- Follow-ups / tech debt tickets:
