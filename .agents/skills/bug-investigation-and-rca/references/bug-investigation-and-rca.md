# Bug investigation and RCA reference

## A) Evidence-first rules (anti-cheat)

- Do not claim root cause without evidence.
- Separate **facts** (observed output, logs, traces, tests) from **assumptions**.
- Use no more than two competing hypotheses before selecting a leading one.
- If only a workaround is currently possible, label it as workaround and file a follow-up task for root-cause fix.

## B) Bug report template guidance

Keep reports short and concrete:

- Include reproducible steps.
- State expected behavior vs actual behavior.
- Record environment (version, platform, config, feature flags).
- Include evidence links/snippets (stack traces, logs, metrics, traces, failing test output).

## C) Five Whys guidance

Use Five Whys to move from symptom to systemic root cause. Avoid blame; stop at a process/system condition that can be changed.

Example (short):
1. Why crash? null dereference in parser.
2. Why null? missing config key returned empty value.
3. Why missing key not handled? validation skipped for migration path.
4. Why skipped? migration path bypassed normal schema check.
5. Why bypass exists? no regression test for migrated configs (root cause).

## D) Prevention action taxonomy

Every bug report should include at least one measurable action with owner/tracking:

- **Prevent**: eliminate recurrence path (e.g., stronger validation, guardrails).
- **Detect**: detect earlier (e.g., alert, test, metric threshold).
- **Mitigate**: reduce blast radius (e.g., fallback with circuit breaker).

Each action must have:
- verifiable end state,
- owner,
- tracking ID or issue link.

## E) Tool selection matrix

| Symptom | Tools | Expected outcome |
|---|---|---|
| Crash / memory corruption (C/C++) | ASan/UBSan + debugger (gdb/lldb) | Failing location and invalid memory access cause |
| Deadlock / race | ThreadSanitizer, thread dump, stress/repeat test | Contended locks/order inversion or race path identified |
| Flaky tests | Repeated test runs + targeted instrumentation | Deterministic failure pattern and triggering condition |
| Performance regression | Profiler + baseline/current metrics | Hot path and regression delta quantified |
| Missing observability | Add structured logs/metrics/traces | Evidence available to validate hypotheses |

## F) Integration pointers (route to other skills)

- Missing logs/metrics/traces for evidence: invoke `$observability`.
- Concurrency suspected: invoke `$thread-safety-tooling` (if available) or `$concurrency-core`.
- Error translation/retries/fallbacks hide cause: invoke `$error-handling`.
- Legacy area lacks safe tests: invoke `$working-with-legacy-code`.
