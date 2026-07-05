# Function Design Verification — ExecPlan

> This is a living document. Keep **Progress (WBS)**, **Decision log**, **Surprises**, and **Handoff** up to date.

## Purpose / Big Picture

Build a lightweight verification system that checks whether AI-led function-design skills change agent behavior, not just whether the skill files exist. The system should combine existing repository validation, trigger-routing evals, protocol/static checks, behavioral fixtures, oracle checks, bad final-state samples, and an agent-run report format.

## Scope

### In scope
- Add function-design trigger eval cases for positive, negative, and routing-overlap scenarios.
- Add a protocol/autonomy validator for critical concepts in `function-boundary-governor`, `destructive-refactor`, `quality-gate`, and `AGENTS.md`.
- Add six standard-library-only behavioral fixture scenarios with expected-good and expected-bad workspaces.
- Add a harness that proves good states pass and bad states fail.
- Initialize repository command wrappers enough for `make verify` to run the canonical validators.
- Document agent-run report format and scoring rubric.

### Out of scope / non-goals
- Running an actual LLM agent against every fixture.
- Introducing non-standard-library dependencies.
- Rewriting existing skills beyond what validation requires.
- Building subjective prose scoring.

## Constraints / Quality targets

- No heavy external dependencies; Python standard library only.
- Verification must inspect files and behavior, not rely on final-response prose.
- Existing validation commands must continue to pass.
- Bad samples must fail their scenario oracle.
- `COMMANDS.md` initialization can only be cleared after `make verify` succeeds.

## Context & Orientation

- Skill source: `.agents/skills/*/SKILL.md`
- Existing trigger evals: `evals/skill-triggers/core.json`
- Existing validators: `scripts/validate_skills.py`, `scripts/validate_skill_trigger_evals.py`, `scripts/report_skill_inventory.py`, `scripts/generate_agent_index.py`
- Function-design ledger path: `.agents/design-ledger/function-boundaries.md`
- New fixture target: `evals/function-design/`
- Discovery: `python` is not installed in this environment; `python3` is available as Python 3.14.3.

## Design

### Boundary sketch

- `evals/skill-triggers/function-design.json`: routing seed cases only; no model scoring.
- `scripts/validate_function_design_protocol.py`: static concept/autonomy checks over skill/core text.
- `evals/function-design/scripts/oracle_common.py`: reusable file, AST, test-runner, and check helpers.
- `evals/function-design/scripts/run_oracles.py`: scenario harness that runs each fixture oracle on `expected/good` and `expected/bad/*`.
- `evals/function-design/fixtures/<scenario>/oracle.py`: scenario-specific file and behavior checks.
- Fixture workspaces: root baseline plus `expected/good` and at least one `expected/bad/<name>` final state.

### Observability

- CLI tools print exact pass/fail summaries and failing check names.
- Oracle harness prints per-scenario good/bad validation results.
- Agent-run reports capture `oracle-output.txt`, `verification-output.txt`, and `decision.json`.

### Testing strategy

- Static checks: existing repository validators plus new protocol validator.
- Behavioral checks: run fixture tests inside each expected workspace through the oracles.
- Negative validation: every bad sample must return oracle failure.
- Wrapper verification: `make verify`.

## Milestones (high-level plan)

1. Add the ExecPlan and route the work through required repository workflows.
2. Add trigger-routing cases for function-boundary, destructive-refactor, legacy, quality-gate, and negative near-misses.
3. Implement protocol/autonomy validation for critical skill concepts.
4. Build six fixtures with good and bad final states plus scenario oracles.
5. Add harness documentation, scoring/report format, and Makefile/COMMANDS wrappers.
6. Run all requested validation commands and final quality gate.

## Progress (WBS)

- [x] (P0) Inspect existing repository, skill docs, validators, and command wrapper — deliverable: orientation facts above — verify: baseline validators run with `python3`
- [x] (P1) Add function-design trigger eval cases — deliverable: `evals/skill-triggers/function-design.json` — verify: `validate_skill_trigger_evals.py`
- [x] (P2) Add protocol/autonomy validator — deliverable: `scripts/validate_function_design_protocol.py` — verify: validator passes
- [x] (P3) Add behavioral fixtures and oracle harness — deliverable: `evals/function-design/...` — verify: `run_oracles.py`
- [x] (P4) Initialize command wrappers — deliverable: `Makefile`, `COMMANDS.md` — verify: `make verify`
- [x] (P5) Final validation and quality gate — deliverable: command results and final handoff — verify: all requested checks pass with `python3`; raw `python` unavailable

## Surprises & Discoveries

- 2026-05-25: `python` is unavailable (`command not found`); `python3 --version` reports Python 3.14.3. Make wrappers should use `PYTHON ?= python3`, and final reporting must mention the exact-command mismatch.
- 2026-05-25: Existing validators pass before changes when run with `python3`.
- 2026-05-25: Running fixture oracles initially generated `__pycache__` directories. The harness now sets `PYTHONDONTWRITEBYTECODE=1`, and `build-debug` uses a temporary `PYTHONPYCACHEPREFIX`.

## Decision log

- 2026-05-25: Keep behavioral evals deterministic by validating stored expected-good and expected-bad workspaces rather than trying to run an agent automatically.
  - Options considered: live agent harness, stored fixture oracles, prose-only report review.
  - Chosen: stored fixture oracles with report format for manual/semi-automated agent runs.
  - Consequences: lightweight and regression-friendly, but actual model execution remains manual/semi-automated.
- 2026-05-25: Initialize Makefile around repository validators with `PYTHON ?= python3`.
  - Options considered: leave uninitialized, require `python`, use `python3`.
  - Chosen: use configurable `PYTHON`.
  - Consequences: `make verify` can pass locally; raw `python ...` commands still depend on environment alias availability.
- 2026-05-25: Function-boundary decision record for this repo change: add a small reusable `oracle_common.py` plus scenario-specific `oracle.py` files.
  - Options considered: one monolithic harness, per-scenario duplicated helpers, shared helper plus scenario checks.
  - Chosen: shared file/test/AST utilities and per-scenario oracle logic.
  - Consequences: common behavior is centralized without hiding scenario-specific design assertions. No repository design-ledger update is required because no existing repo abstraction was replaced, intentionally duplicated, or staged.

## Handoff (update at every stop)

- Current branch / commit: landed on `ws0a-function-design-verification` (2026-07-05); the interim Makefile targets from the original run were superseded by the repository Makefile, so the protocol validator is wired into `make lint` / `make test-integration` / CI instead.
- What is done: trigger evals, protocol validator, six fixtures, good/bad oracle harness, report format, and lint/CI wiring for the protocol validator.
- What is not done: automated live LLM-agent execution against every fixture; this remains manual/semi-automated via the report format. The oracle harness is not yet a CI step (run it manually).
- How to run: `make verify` (includes `scripts/validate_function_design_protocol.py`), `python3 evals/function-design/scripts/run_oracles.py`.
- How to test: use `python3` equivalents of the requested Python commands in this environment because raw `python` is not installed.
- Known risks / open questions: direct `python ...` commands require a `python` alias on machines that do not provide one; `PYTHON=python` can be passed to Make when available.
- Next 1–3 steps: run a real agent against one fixture and store a report; expand bad samples if new failure modes appear.
- Pointers: `evals/function-design/README.md`, `evals/function-design/scripts/run_oracles.py`, `scripts/validate_function_design_protocol.py`, `evals/skill-triggers/function-design.json`.

## Validation & Acceptance

- AC1: Function-design skills have positive and negative trigger eval coverage.
  - Verification: `python3 scripts/validate_skill_trigger_evals.py`
- AC2: Protocol/static validation catches removal of critical concepts and autonomy guidance.
  - Verification: `python3 scripts/validate_function_design_protocol.py`
- AC3: Six behavioral scenarios exist with expected-good and expected-bad states.
  - Verification: `python3 evals/function-design/scripts/run_oracles.py`
- AC4: Good fixture states pass and bad fixture states fail.
  - Verification: oracle harness output reports pass for all expected-good and expected failure for all bad samples.
- AC5: Existing repository validation remains green.
  - Verification: existing validation command chain plus `make verify`.

## Outcomes & Retrospective (fill when done)

- What shipped / merged: new function-design routing eval file, protocol/autonomy validator, six behavioral fixtures with good/bad samples, oracle harness, report documentation/sample, and initialized Makefile/COMMANDS wrappers.
- What went well: good states pass, bad states fail, and the harness catches behavior/design evidence rather than final-response prose.
- What went wrong: local shell lacks `python`; validation had to use `python3`. Initial test runs generated cache directories until bytecode writing was disabled.
- Follow-ups / tech debt tickets: add live agent-run automation if a future harness can execute agents reproducibly; add more bad samples as real failures are observed.
