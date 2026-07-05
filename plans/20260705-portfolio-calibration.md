# Portfolio calibration (Phase 4) — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Fix the two calibration defects measured in `reports/skillset-review-20260705.md` (GAP G8/G9) and confirmed by the Phase 2 smoke eval:
  1. Embedded skills co-fire on host-side work because their trigger vocabulary (logger/recorder/collector/sampler/polling/daemon) matches ordinary projects — 8-13% of Codex traffic was embedded-skill invocations on what may be non-embedded work.
  2. `observability` underfires (1% of traffic; reproduced in the Phase 2 eval where the judge walked the embedded table and skipped the general observability branch).
- Also closes part of WS15: high-traffic skills had 1-2 positive eval cases.

## Scope

### In scope
- WS13: explicit anti-trigger in all 10 embedded skills — work is embedded only with a physical target constraint (battery/power, thermal, flash wear, real-time deadline, constrained target CPU/RAM, separate target device); vocabulary alone does not qualify. Applied by a Sonnet 5 worker from a fixed policy text.
- Router fixes (supervisor): dev-workflow's observability trigger enumerates checkable sub-conditions; embedded NFR table gains an "adds, never replaces, general branches" rule plus the physical-constraint definition.
- WS15 (partial): `evals/skill-triggers/portfolio-calibration.json` — positive cases for implementation-economy (4), execution-plans (3), test-driven-development (3), bug-investigation-and-rca (3); observability regression cases (2, incl. the embedded-daemon miss); embedded anti-trigger regression cases (2 host-side prompts with embedded vocabulary).
- Re-run routing smoke eval on the weak spots (embedded daemon / host-side vocabulary cases).

### Out of scope / non-goals
- uidesign-orchestrator retirement decision (owner's call; carried from the 2026-04-24 review).
- Codex telemetry categorization ("other" 76%) — external to this repo's content.
- Portfolio re-weighting (adding/removing skills).

## Progress (WBS)

- [x] (P0) Router fixes in dev-workflow (observability enumeration + adds-not-replaces rule)
- [x] (P0) WS13 anti-triggers in 10 embedded skills — Sonnet 5 worker, diff-reviewed
- [x] (P1) WS15 eval seed file — Sonnet 5 worker, validator green
- [x] (P2) Smoke re-eval on regression cases — 4/4 (see Outcomes)
- [x] (P3) PR

## Decision log

- 2026-07-05: The observability fix is applied at the **router**, not the skill — the skill's own triggers were already precise; the miss happened while routing, so the enumeration belongs in dev-workflow's trigger line.
- 2026-07-05: Anti-trigger policy names the physical constraints positively (what MAKES work embedded) rather than listing exclusions only — a checkable predicate in both directions.

## Surprises & Discoveries

- 2026-07-05: In the regression eval, the host-side CLI case not only avoided all embedded skills but correctly picked up `project-structure` and `performance-review` — the Phase 1-2 additions compose with the new anti-triggers without interference.
- 2026-07-05: The positive control's only miss (`embedded-nfr-harness-design`) is the known second-order chain-depth weakness from the Phase 2 eval, present before the anti-triggers — not a regression from this change. Candidate future fix: make the harness-design row's trigger self-contained ("budget claims will need proof at gate time") rather than dependent on inferring measurement need.

## Handoff (update at every stop)

- Current branch: `portfolio-calibration-phase4`
- Open decisions for the owner: uidesign-orchestrator status; `.github/prompts/` retirement (WS10); Opus 4.8 smoke flip (Phase 3 follow-up).

## Validation & Acceptance

- AC1: `make verify` green (incl. new eval file validation).
- AC2: smoke re-eval — the embedded-daemon case now triggers `observability`, and host-side vocabulary cases trigger no embedded skills (≥3/4 cases pass, with the observability case mandatory).

## Outcomes & Retrospective (fill when done)

- What shipped / merged: WS13 anti-triggers (10 embedded skills, insert-only, Sonnet 5 worker), router fixes (observability enumeration + adds-not-replaces rule), WS15 eval seeds (17 cases; trigger eval corpus now 178 cases).
- Regression eval (Sonnet 5 judge, blind, 4 cases): **3/4 with both target regressions fixed** — embedded-daemon case now triggers `observability` (Phase 2 miss resolved); both host-side vocabulary cases trigger zero embedded skills; positive control keeps all primary embedded triggers. AC2 met.
- What went well: third and fourth clean delegated runs; anti-trigger policy text applied verbatim across 10 files with one style-adaptive exception correctly reported.
- What went wrong: nothing blocking.
- Follow-ups / tech debt tickets: harness-design chain-depth trigger (above); owner decisions still open — uidesign-orchestrator status, `.github/prompts/` retirement (WS10), Opus 4.8 smoke flip.
