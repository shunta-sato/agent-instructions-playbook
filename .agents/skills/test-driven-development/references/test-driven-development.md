# Test-driven development quick reference

Use this reference after TDD is explicitly requested, required by project policy, or selected as the test-first route. It preserves Red → Green, not a fixed amount of process.

## 1) Test List (do this first)

- List “variants” of expected behavior for the new change.
- Seed the list from acceptance criteria, regression evidence, and realistic boundary failures.
- There is no item quota. One decisive case may suffice; required safety/repository checks still apply.
- Load `unit-test-design` only for unresolved strategy, partition, coverage, test-double, or flakiness decisions.
- This is analysis, but it is **behavior analysis**, not a full spec rewrite.
- Do not write all tests at once. Pick one item from the list and finish it end-to-end.

Illustrative Test List (include only cases relevant to the current requirement):

- basic case
- key not in DB
- external service timeout
- invalid input
- permission denied

## 2) One item at a time (Red → Green → Refactor)

- **Red**: write one failing test and run it to confirm the expected failure before changing production code. Unexecuted tests are not Red evidence.
- **Green**: implement the smallest change to make it pass, and keep all existing tests passing.
- **Refactor**: make a scoped structural improvement only when needed, without changing behavior; keep tests green. If `implementation-economy` is active, honor its budget. No cleanup is required just to complete a cycle.

## 3) Ordering tips

- Start with the smallest case you can make pass (few dependencies, easy observation).
- Then move to edge cases and failure paths.
- When a relevant new case appears, update the Test List; defer unrelated cases rather than silently expanding scope.
- Stop when required cases are covered and perform the routed final verification.
- Show the list initially, at material scope changes, and at handoff, not after every tool call.

## 4) Minimum test readability rules

- The test name alone should explain “what must be true to succeed”.
- Assertions should help you get closer to the cause when the test fails (specific checks).
- Do not bury intent in setup: keep “input → action → expectation” visible.
- Each test must make the **why** and the **what** readable (test name + 1–2 lines of comment, or an equivalent structure).
