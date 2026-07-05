# Function Design Behavioral Evals

These evals verify whether an agent following the function-design skills produces cleaner final code, not whether the skill prose sounds reasonable.

The layers are:

1. Existing repository validation:
   - `python scripts/validate_skills.py`
   - `python scripts/validate_skill_trigger_evals.py`
   - `python scripts/report_skill_inventory.py --check --format text`
   - `python scripts/generate_agent_index.py --check`
2. Trigger-routing evals in `evals/skill-triggers/function-design.json`.
3. Protocol/static checks in `scripts/validate_function_design_protocol.py`.
4. Behavioral fixtures under `evals/function-design/fixtures/`.
5. Scenario oracles that inspect files, run behavior tests, check ledgers, and reject forbidden patterns.
6. Bad final-state samples that prove each oracle is not too weak.
7. Agent-run report artifacts under `reports/function-design-evals/`.

## Fixture Layout

Each scenario uses this shape:

```text
fixtures/<scenario>/
  README.md
  task.md
  src/
  tests/
  expected/
    good/
    bad/<case>/
  oracle.py
```

The root `src/` and `tests/` represent the intentionally flawed baseline. The oracle is meant to run against a completed workspace, so the harness checks `expected/good` and `expected/bad/*`.

Run all behavioral oracles:

```sh
python evals/function-design/scripts/run_oracles.py
```

In environments without a `python` alias, run the same command with `python3`.

## Scenario Scorecard

For each real agent run, score each item as `pass`, `fail`, or `not_applicable`:

- Trigger correctness: expected skills loaded, irrelevant skills avoided
- Task behavior: requested behavior works
- Function design: expected final abstraction achieved
- Restraint: no over-refactor or unrelated cleanup
- Destructive protocol: red state used only when appropriate and convergence achieved
- Call-site migration: complete and coherent
- Ledger quality: relevant and specific
- Verification quality: tests and oracle pass
- Autonomy: no human option selection required

Pre-merge acceptance requires all static validation to pass, all trigger evals to validate, all protocol checks to pass, all expected-good workspaces to pass their oracles, all intentionally bad workspaces to fail their oracles, and at least one smoke report artifact or template to exist.

## Agent-Run Report Format

Store manual or semi-automated agent runs under:

```text
reports/function-design-evals/YYYYMMDD-HHMMSS/<scenario>/
  task.md
  transcript.md or summary.md
  diff.patch
  oracle-output.txt
  verification-output.txt
  decision.json
```

`decision.json` must include:

```json
{
  "scenario": "...",
  "triggered_skills": [],
  "decision": "replaced | merged | keep_parallel | no_op | rollback",
  "temporary_red_state_used": true,
  "old_abstractions": [],
  "new_abstractions": [],
  "deleted_functions": [],
  "migrated_call_sites": [],
  "forbidden_patterns_found": [],
  "ledger_updates": [],
  "verification_commands": [],
  "oracle_result": "pass | fail"
}
```

The report is evidence for comparing agent behavior over time. It is not a substitute for the oracle inspecting the resulting files.
