# Refactoring overhaul — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

- Fix the owner-reported refactoring failures: agents keep old APIs even when backward compatibility is explicitly waived; are weak at deleting unused APIs, consolidating near-duplicates, and flattening redundant class hierarchies; dev-workflow has no first-class refactoring routing; quality-gate never verifies that old APIs are actually gone; and there is no preparatory-refactor step ("make the change easy, then make the easy change").
- Diagnosis (quote-verified, 2026-07-05): all compat rules were permission-shaped ("forbidden unless staged/ledgered") with no imperative for the waived case; no mechanical old-symbol check existed; `design-balance` had removal triggers and destructive-refactor handoff missing entirely; AGENTS.md "No broad cleanups" lacked a refactoring exception; deletion/consolidation requests tripped no trigger vocabulary. The design ledger has never held a real entry — ledger-based enforcement was aspirational.

## Scope

### In scope
- **Compat-mode** (`preserve | staged | break-allowed`) recorded at routing (dev-workflow 1b), enforced at gate; `break-allowed` = delete, don't deprecate; staged-ledger escape unavailable under `break-allowed`.
- **`scripts/check_api_removal.py`**: mechanical removed-symbol sweep (word-boundary, ledger/changelog exempt), wired into quality-gate as tool-verified evidence — same pattern as `check_structure.py`.
- **Routing**: new dev-workflow triggers for rework/consolidation/deletion requests and zero-caller code; `delete` added to function-boundary-governor's action enum.
- **`design-balance` hardening**: removal-direction triggers, destructive-refactor execution handoff, anti-retention rule under `break-allowed`.
- **`destructive-refactor` hardening**: break-allowed imperatives, deletion checklist with sweep, "keep just in case" forbidden.
- **Preparatory refactor** step (2b) in the default lane with recorded `prep-refactor: done | not-needed`.
- **AGENTS.md**: refactoring exception extended to `design-balance`; "No broad cleanups" scoped to *unrelated* cleanups; compat-mode principle.
- Trigger evals (`evals/skill-triggers/refactoring.json`) + blind behavior validation (fixture: consolidate 3 near-duplicate APIs under an explicit compat waiver; oracle = old symbols gone + tests green).

### Out of scope / non-goals
- Language-specific dead-code tooling (cargo udeps etc.) — the sweep is name-based and language-agnostic.
- Committing behavior fixtures into the repo eval suite (function-design suite landing is tracked separately, WS0a).

## Progress (WBS)

- [x] (P0) AGENTS.md principles + dev-workflow compat-mode/1b, prep-refactor/2b, new triggers (SKILL + reference)
- [x] (P0) quality-gate refactor outcome criteria (SKILL + reference) + `delete` in evidence enum
- [x] (P0) `scripts/check_api_removal.py` + 4 unit tests
- [x] (P1) destructive-refactor / design-balance / function-boundary-governor hardening — Sonnet 5 worker, diff-reviewed
- [x] (P1) `evals/skill-triggers/refactoring.json` — Sonnet 5 worker
- [x] (P2) Blind behavior validation (Sonnet 5 worker on fixture, judge-verified oracle)
- [x] (P3) PR

## Decision log

- 2026-07-05: Compat-mode is recorded at **routing time** (dev-workflow 1b), not inside destructive-refactor — the mode must exist before any skill decides retention, and the gate needs one canonical place to verify it.
- 2026-07-05: The sweep exempts CHANGELOG/plans/reports/design-ledger by default — old names legitimately live in history; the check targets living code, tests, and docs.
- 2026-07-05: `delete` becomes a first-class function-boundary action (previously deletion had to masquerade as `replace`/`inline`, which structurally implies a successor exists).

## Surprises & Discoveries

- 2026-07-05: The design ledger (`.agents/design-ledger/function-boundaries.md`) has never contained a real entry — every ledger-gated rule so far has been enforcing against an empty file. The compat-mode + sweep design deliberately does not depend on ledger discipline under `break-allowed`.

## Handoff (update at every stop)

- Current branch: `refactoring-overhaul`
- Follow-ups: see Outcomes.

## Validation & Acceptance

- AC1: `make verify` green; new unit tests pass.
- AC2: Blind behavior test — a Sonnet 5 worker given the fixture task ("consolidate the three formatting APIs; compatibility may break") under the revised playbook produces a repo where `check_api_removal.py --symbol <two retired names>` passes and `cargo test` is green, with compat-mode recorded as `break-allowed`.
- AC3: Trigger evals validate; routing spot-check on the rework/deletion/flatten prompts.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: compat-mode routing + gate enforcement, `check_api_removal.py` sweep, refactoring trigger rows, `delete` action, design-balance/destructive-refactor/FBG hardening, prep-refactor lane, 7 trigger evals (corpus 185).
- **Blind behavior validation (AC2): PASS, judge-verified.** A Sonnet 5 worker given only "consolidate the three formatting APIs — you may break backward compatibility" under the revised playbook: recorded compat-mode `break-allowed` quoting the waiver; ran pre-edit call-site sweep; decided replace/delete/replace per function via the rubric; **deleted all three old names** (no deprecated markers, no aliases — independently verified: sweep zero hits, `cargo test` 3/3, API surface = one function, net −19 lines); ran the structure watch and the removed-symbol sweep unprompted; and correctly diagnosed a false positive from stale `target/` artifacts. It also escalated the ledger write (playbook read-only in the harness) instead of violating scope.
- What went well: the compat-mode imperative + mechanical sweep closed F1 exactly as designed; the worker chose NOT to invoke destructive-refactor because the migration stayed green atomically — a correct reading of the red-state trigger, showing the routing distinguishes "destructive intent" from "needs a break window".
- What went wrong: nothing blocking. Note the sweep's default path set can hit stale build artifacts (`target/`); the worker handled it, but adding `target/` to the default exemptions is a small follow-up.
- Follow-ups / tech debt tickets: add `target/`, `node_modules/`, `build/` to `check_api_removal.py` default exemptions; F4 (class-hierarchy flattening) behavior fixture once the function-design eval suite lands (WS0a); design ledger has never held a real entry — consider a lint that fails ledger-gated claims when the ledger is still the stub.
