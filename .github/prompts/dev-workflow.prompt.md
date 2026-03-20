# dev-workflow

Use this prompt to route a task: decide risk and required trigger branches only.

## Workflow

1) Risk route first
- Classify `low` / `normal` / `high` with one-line rationale.
- State required planning depth and required verification depth for that risk.

2) Required trigger branches
- Mark each as `triggered` or `not triggered` with evidence:
  - bug/regression/flaky/crash/hang → `/bug-report` or `$bug-investigation-and-rca`
  - structural boundary/refactor change → `$code-smells-and-antipatterns`
  - concurrency/parallelism change → `$concurrency-core` + `$thread-safety-tooling`
  - runtime behavior change → `$observability`
  - strict low-level constraints/repeated compile-test loops → `$staged-lowering`
  - legacy/no reliable tests/nondeterminism → `$working-with-legacy-code`
  - UI change → `/ui-verify` or `$visual-regression-testing` (+ platform skill)

3) Route summary (handoff contract)
- Selected risk route
- Triggered required branches
- Required verification depth before gate

4) Implement + verify at the routed depth
- Keep diffs minimal.
- Run canonical commands at required depth.

5) Hand off to `/quality-gate`
- Do not make final submit/no-submit judgment here.
