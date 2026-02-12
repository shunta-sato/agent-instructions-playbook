# Test-driven development quick reference

This file is the reference for the `test-driven-development` skill. Use it to keep TDD as a fixed procedure.

## 1) Test List (do this first)

- List “variants” of expected behavior for the new change.
- This is analysis, but it is **behavior analysis**, not a full spec rewrite.
- Do not write all tests at once. Pick one item from the list and finish it end-to-end.

Example Test List:

- basic case
- key not in DB
- external service timeout
- invalid input
- permission denied

## 2) One item at a time (Red → Green → Refactor)

- **Red**: write exactly one failing test and confirm it fails for the expected reason.
- **Green**: implement the smallest change to make it pass, and keep all existing tests passing.
- **Refactor**: improve structure without changing behavior (tests + production code), while keeping tests green.

## 3) Ordering tips

- Start with the smallest case you can make pass (few dependencies, easy observation).
- Then move to edge cases and failure paths.
- When you discover a new case during implementation, put it back into the Test List (do not expand scope immediately).

## 4) Minimum test readability rules

- The test name alone should explain “what must be true to succeed”.
- Assertions should help you get closer to the cause when the test fails (specific checks).
- Do not bury intent in setup: keep “input → action → expectation” visible.
- Each test must make the **why** and the **what** readable (test name + 1–2 lines of comment, or an equivalent structure).
