# Structure gates (Phase 1) — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Prevent the monolith failure mode observed in Codex runs (a giant `main.rs` holding all logic and inline tests) by adding structural, state-based gates to the skill system.
- Root-cause analysis: `reports/skillset-review-20260705.md`. All existing triggers were event-based, the smallest-safe-change principle plus `implementation-economy` favored appending to one file, and `quality-gate` had no structural exit criteria.

## Scope

### In scope
- `scripts/check_structure.py`: mechanical structure-budget checker (stdlib only) + unit tests.
- New `project-structure` skill (generative layout guidance; Rust reference first).
- `dev-workflow`: mandatory structure watch at all risk levels; low-risk lane skip now requires a passing structure check; new trigger branch to `project-structure`.
- `quality-gate`: structural exit check (1b) independent of triggered branches.
- `AGENTS.md` / `implementation-economy`: resolve the incentive contradiction (required splits are complexity placement, not new abstraction or broad cleanup).
- `test-driven-development`: test placement pointer.
- Trigger eval seeds for `project-structure`.

### Out of scope / non-goals
- Phase 2 (decision-tree rewrites for Sonnet 5), Phase 3 (`.claude/` wiring, model catalog/lockfile), Phase 4 (embedded anti-triggers, portfolio rebalance) — tracked in the review report.
- Language references beyond Rust (add per demand).
- Committing the pre-existing untracked function-design eval work (separate change).

## Constraints / Quality targets

- Stdlib-only scripts; `make verify` stays green.
- Structure budget defaults: source file ≤ 400 lines; entrypoint logic ≤ 150 lines; Rust inline tests ≤ 200 lines/file. Overridable by flags.

## Design

- The checker is **state-based**: it inspects current file shape, so it catches slow accretion that event-based triggers miss.
- Ownership: `project-structure` owns the budget numbers; `dev-workflow` runs the watch; `quality-gate` enforces at exit; `design-balance`/`function-boundary-governor` own split naming/ownership decisions.

### Testing strategy
- Unit tests: `tests/test_check_structure.py` covers detection (inline-test blocks, entrypoints) and the exact monolithic-main.rs scenario (all three rules fire).
- Behavior validation: Sonnet 5 agent runs a greenfield Rust CLI task under the revised skills; oracle = `check_structure.py` pass on the produced repo (supervised A/B against pre-change skills).

## Progress (WBS)

- [x] (P0) `scripts/check_structure.py` — deliverable: checker with 3 rules — verify: 9 unit tests pass
- [x] (P0) `tests/test_check_structure.py` — verify: `make test-unit`
- [x] (P1) `project-structure` SKILL + Rust reference — verify: `validate_skills.py`
- [x] (P1) `dev-workflow` structure watch + trigger branch (SKILL + reference)
- [x] (P1) `quality-gate` structural exit check (SKILL + reference)
- [x] (P1) `AGENTS.md` principle amendment + regenerated index
- [x] (P1) `implementation-economy` / `test-driven-development` boundary clauses
- [x] (P2) `evals/skill-triggers/project-structure.json` — verify: `validate_skill_trigger_evals.py`
- [x] (P3) Sonnet 5 supervised behavior validation on the PR (Rust CLI fixture task) — verify: A/B oracle results in Outcomes

## Surprises & Discoveries

- 2026-07-05: The A/B control run (Sonnet 5 + pre-change skills) did **not** reproduce the monolith: Claude Sonnet 5's default instincts already produce modular code, unlike the Codex agent in the original incident. The differential the gates buy on a strong model is therefore (a) canonical layout (`lib.rs` growth path — control produced a binary-only crate with no `lib.rs`), (b) a thinner entrypoint (25 vs 54 logic lines), and (c) **verifiable** structural evidence instead of unverified instinct. The regression case (weak model / bad day / accretion over many sessions) is covered by the mechanical oracle unit test.
- 2026-07-05: The structure budget produced zero false positives on the control run (6 files, pass) — calibration holds for idiomatic non-gated output.

## Decision log

- 2026-07-05: Budget thresholds set to 400/150/200 because they are far above idiomatic sizes but well below the observed failure (700+ line main.rs), keeping false positives low while making the failure mode impossible to pass silently.
  - Options considered: stricter (200/50/100), metric-based (cyclomatic complexity).
  - Chosen: line-count rules — checkable by stdlib, explainable to a mid-tier model in one sentence.
  - Consequences: coarse; complexity-based rules can be layered later.
- 2026-07-05: The watch runs at **all** risk levels including low, because the monolith grew exactly through low-risk appends that skipped every lane.

## Handoff (update at every stop)

- Current branch / commit: `structure-gates-phase1`
- What is done: all P0–P2 items; `make verify` green.
- What is not done: P3 Sonnet 5 behavior validation (runs against the PR).
- How to test: `make verify`; `python3 -m unittest tests.test_check_structure`.
- Next 1–3 steps: open PR; run supervised Sonnet 5 fixture task; record results in the PR.

## Validation & Acceptance

- AC1: A 700-line `main.rs` with 250 lines of inline tests produces all three findings.
  - Verification: `tests/test_check_structure.py::test_monolithic_main_rs_scenario_flags_all_three`.
- AC2: `make verify` passes with the new skill and eval seeds.
  - Verification: CI / local run.
- AC3 (post-merge): A Sonnet 5 agent given a greenfield Rust CLI task under the revised skills produces a repo where `check_structure.py` passes.
  - Verification: supervised agent run, oracle scripted.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: PR #80 (structure gates) + supervised A/B validation.
- A/B validation (2026-07-05, task: stdlib-only Rust CLI `logstat`, identical prompts, Sonnet 5 workers, independent judge verification):
  - Run A (control, main skills): modular but **no `lib.rs`** (binary-only crate, integration tests must subprocess); `main.rs` 54 lines; structure check pass (6 files); `cargo test` 38/38; no structural evidence produced (nothing in the main-branch gate asks for it).
  - Run B (treatment, PR skills): canonical `main.rs` (25 wiring lines) + `lib.rs` + 4 domain modules + `tests/`; structure watch executed and cited (`check_structure.py` pass, 7 files); `project-structure` triggered with layout decisions recorded; `cargo test` 40/40.
  - AC3 met: treatment repo passes `check_structure.py`; the revised skill chain (dev-workflow step 6 → project-structure → quality-gate 1b) was discovered and executed by Sonnet 5 without any hint in the task prompt, with zero misexecution.
- What went well: Sonnet 5 followed the new decision points exactly (numeric budget, mandatory watch, evidence contract) — supports the review's thesis that checkable predicates are what mid-tier models need.
- What went wrong: nothing blocking; note the control's quality means monolith-prevention could not be demonstrated end-to-end on this model (covered instead by the oracle unit test for the incident scenario).
- Follow-ups / tech debt tickets: Phase 2 (decision-tree rewrites), Phase 3 (`.claude/` wiring + model catalog/lockfile), Phase 4 (embedded anti-triggers) per `reports/skillset-review-20260705.md`.
