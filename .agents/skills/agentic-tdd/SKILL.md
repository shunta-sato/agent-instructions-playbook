---
name: agentic-tdd
description: "Develop user-visible runtime behavior from an executable acceptance/E2E test, or honor explicitly requested TDD. Use UTs inside that loop; not a mandatory workflow for static edits or already-explained trivial fixes."
---

# Acceptance-first agentic TDD

The outer loop proves the user's outcome through the actual required entrypoint and
integration boundaries. The inner loop uses unit/component/integration tests for fast,
focused feedback. Unit tests passing alone do not complete a required user journey.

Before substantial implementation, inherit the agreed outcome, required NFRs, E2E boundary,
permitted substitutes, execution environment and authority. If these are missing or the
verification path has not been demonstrated, use `preflight-engineering` to resolve them
with the requester and establish readiness. Do not repeat valid prior agreements.

Express success as observable behavior before production behavior is implemented. Exercise
the real CLI, API, UI, device or appropriate public boundary. Identify the acceptance failure
caused by the missing/defective feature, not by an unavailable runner, dependency, account or
target. Existing relevant failing tests can serve as Red. For new projects, a minimal bootable
slice may precede feature Red. If a pre-change comparison is impossible, explain why and the
replacement evidence; do not claim a test-first sequence that did not occur.

Implement with focused lower-level tests, then close the outer acceptance test on the final
candidate. Choose test granularity and iteration order without fixed cycle counts or a
compulsory refactoring pass. Cover meaningful failure behavior and persistence/restart or
cross-process state when the requested outcome depends on it. A screenshot, successful tap,
healthy process or exit 0 is not enough without the agreed result assertion.

Keep required E2E real across the boundary being claimed. Use mocks/test services only inside
the agreed scope and describe what they cannot establish. More E2E tests are not intrinsically
better; exercise decisive journeys and use cheaper tests for detailed combinations. Performance,
power and deadline obligations still need their own appropriate evidence, not a functional
E2E pass. Do not change expected values to match an implementation without a legitimate
requirement correction and its recorded source; never delete/skip the failing criterion to win.

Report which acceptance checks actually ran, their candidate/environment identity and results,
and material limits. No-tests/all-skipped, missing environment or unrun target evidence is not
Green. Missing required evidence blocks the associated completion claim even if UTs pass.
Communicate a newly blocked path immediately, repair only within authority, and continue useful
independent work; a handoff or Draft PR is not a completed feature. Explicitly requested TDD
must also preserve its requested test-before-implementation ordering.

A compact PR description and existing test output are sufficient unless the task needs another
artifact. This Skill defines evidence and sequencing dependencies, not an obligatory test
framework, hypothesis quota, report pack or universal approval checkpoint.
