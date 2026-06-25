## Bug Report (RCA)
- Title: Delegated run judge accepts forged validation summary without command evidence
- Symptom (actual behavior): `judge_agent_run.py --require-accepted` accepted an `agent_run` ledger entry whose `validation` object contained only `passed: true` and no `validation.commands` entries.
- Expected behavior: delegated run acceptance must require concrete validation command evidence; a naked summary boolean must not satisfy the final gate.
- Severity/Impact: High integrity impact for Agent-facing final quality gate evidence, because a handwritten ledger record can bypass delegated-run validation.
- Environment (versions, platform, config): Python 3 stdlib scripts in this repository, current branch HEAD before this fix (`df8e02f`).
- Detection (how it was found): Aardvark vulnerability report and local reproduction with a temporary JSONL ledger.

### Reproduction
- Steps to reproduce:
  1. Create a temporary `.jsonl` ledger with one `agent_run` record containing matching `allowed_files` and `changed_files`, `outcome.agent_completed: true`, and `validation.passed: true`.
  2. Omit `validation.commands`.
  3. Run `python3 scripts/judge_agent_run.py --ledger <temp-ledger> --run-id poc-forged-no-validation-output --require-accepted --format json`.
- Minimal repro (if available): The temp-ledger reproduction recorded in this fix's verification output.
- Frequency: Deterministic before the fix.

### Evidence
- Logs / stack trace / metrics / traces: Before the fix, the repro printed `accepted: true` and `validation_passed: true` with `quality_gate: not_run`, then exited `0`.
- What changed recently (if known): Quality-gate instructions made `judge_agent_run.py --require-accepted` authoritative delegated-run evidence, while `validation_passed()` trusted `validation.passed` before inspecting command entries.

### Root Cause Analysis (Five Whys)
1) Why #1: The judge accepted the forged ledger because `evaluate_run_record()` treated `validation_ok` as true.
2) Why #2: `validation_passed()` returned `bool(validation["passed"])` whenever the field was present.
3) Why #3: The validation summary field was treated as primary evidence instead of a derived summary of command results.
4) Why #4: No regression test exercised a ledger with `validation.passed: true` and missing `validation.commands`.
5) Why #5 (root cause): The delegated-run evidence contract lacked an enforced invariant that acceptance requires non-empty command-result evidence.

> Rule: each “Why” must be backed by evidence or a clearly labeled assumption.

### Fix
- What changed (summary): `validation_passed()` now ignores naked summary booleans and requires a non-empty list of command result objects with non-empty `cmd`, integer `exit_code`, and `passed is True`.
- Why this fix addresses the root cause: A forged record cannot satisfy validation without command-result evidence, and the acceptance path continues to reuse the single centralized validation predicate.

### Verification
- Tests run: `make test-unit`; targeted forged-ledger replay; canonical `make verify`.
- Repro re-run result: After the fix, the same forged-ledger repro prints `accepted: false`, `validation_passed: false`, and exits `1` under `--require-accepted`.
- Tooling run (if relevant): Python unit tests cover forged and valid validation evidence paths.

### Prevention (must include at least one, measurable)
- Prevent: Unit tests now reject summary-only validation records and accept only non-empty passing command evidence.
- Detect: `make test-unit` is part of `make verify`, so the forged-ledger regression runs in the canonical verification chain.
- Mitigate: The judge still fails closed under `--require-accepted` when validation is missing, malformed, failed, or blocked.
- Follow-up tasks (with owners / tracking IDs if available): None for this minimal remediation.
- If missed workflow/product contract: missing invariant class was command-result evidence for delegated runs; generated-workflow regression is the forged ledger unit test; process update is the workflow-contract review report for this patch; replay fixture is the targeted temp-ledger command documented in verification.

### Workaround (only if unavoidable)
- Workaround description: Not applicable.
- Risk: Not applicable.
- Removal plan / tracking: Not applicable.
