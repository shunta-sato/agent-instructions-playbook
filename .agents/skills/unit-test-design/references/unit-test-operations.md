# Unit test operations reference

Covers: coverage gates and repo-wide guidance, the test-double ladder,
isolation/speed/flakiness rules, test-code style, regression-fix criteria,
and advanced-technique selection. For risk tiers, the design-basis matrix,
boundary values, combination testing, state transitions, and the stop
criteria/PR checklist, see `references/unit-test-case-design.md`.

## 7. Code coverage criteria

### 7.1 Coverage is a miss detector, not a goal

Code coverage shows that code **ran**, not that it was **correctly
verified**. Even 100% line coverage does not mean every branch or
data-dependent failure was caught. Google also positions coverage as a
lossy proxy metric with no single ideal value that holds across every
product. (Code Coverage Best Practices: https://testing.googleblog.com/2020/08/code-coverage-best-practices.html)

### CI hard gate

| Target | Criterion |
| --- | ---: |
| Changed/added executable lines | **90% or higher** |
| Changed/added branches | **80% or higher** |
| Changed branches in high-risk code | **90% or higher** |
| Critical specified/rejection results | **All cases, regardless of count** |

When the tooling does not provide changed-branch coverage, combine
changed-line 90%+ with a review-time check of "was each branch outcome
tested?"

### Repo-wide

* For new, healthy projects, use line coverage around **75%** as a
  dashboard guideline
* The normal healthy range is roughly **70-85%**
* Do not suddenly impose a 75% overall gate on existing legacy code
* For legacy code, start from changed-code 90%
* After the overall figure exceeds 90%, do not uniformly push normal
  areas to 95% or 100%
* Monitor high-risk modules separately from the overall average

Google treats 60% as a general reference point for acceptable, 75% for
commendable, and 90% for exemplary, while avoiding a one-size-fits-all
top-down target and cautioning against over-focusing on pushing an entire
project from 90% to 95%. It does treat 90% as a good floor at the
change-unit level. This makes "75% overall guideline, 90% on changed code"
a practically well-balanced initial default.

### Coverage exclusions

The following may be excluded, but the reason must be stated explicitly
and reviewed:
* Auto-generated code
* Compiler-generated code
* Declaration-only DTOs or constants
* Defensive code proven unreachable
* Platform-specific processing that cannot run in the test environment

Do not exclude an entire package or directory without justification.

## 8. Test double and mock criteria

Use this priority order:
1. **A fast, deterministic, in-process real implementation**
2. **Fake**
3. **Stub**
4. **Mock-based call verification**

Google's own practice also prefers a real implementation when it is fast,
deterministic, and has simple dependencies, and reaches for a Fake when the
real implementation does not fit. Overusing Mocks and Stubs couples the
test to implementation details and makes it fragile under refactoring.
(SWE Book ch13: https://abseil.io/resources/swe-book/html/ch13.html)

Verify call count or call order with a Mock only when **the interaction
itself is the contract**, such as:
* Must not double-charge
* An external send must happen exactly once
* Retries are capped at 3 attempts
* Must not fetch data before authentication
* An audit record must be written before commit
* Cache usage bounds the number of DB calls

Otherwise verify return values, state changes, or emitted events instead of
the call sequence.

When a Fake is provided as shared infrastructure, run the same public
contract tests against both the real implementation and the Fake. A Fake
left unmaintained drifts from the real implementation's behavior, so the
Fake itself needs its own tests.

## 9. Isolation, speed, and stability

Unit tests must, in principle, prohibit:
* External network access
* Starting a real DB or external process
* Dependence on the real filesystem
* Waiting via `sleep`
* Direct dependence on the real system clock
* Unseeded randomness
* Dependence on test execution order
* Mutable state shared between tests

Inject a Clock for time, a Random Source for randomness, and a Fake for
external services. Google's small-test definition also excludes network,
disk I/O, and sleep to secure speed and determinism.

Recommended initial SLOs:

| Metric | Initial target |
| --- | ---: |
| Local unit tests for the changed target | Within 30 seconds |
| Full unit-test stage on a PR | p95 within 5 minutes |
| Known flaky tests in Required | 0 |
| Fixed `sleep` inside unit tests | 0 |

In large monorepos, protect developer feedback time with change-impact
analysis, caching, and parallelization rather than total full-suite
runtime.

Passing after a rerun alone does not count as "passing." A test confirmed
flaky must be fixed the same day, or quarantined with an owner, issue, and
deadline. Reruns are an aid to investigation, not a permanent fix. As
flaky tests accumulate, developers stop trusting test results, and the
value of the test suite itself erodes.

## 10. How to write test code

The following are mandatory.

### One behavior per test

A test verifies, in principle, one behavior. Multiple asserts are fine as
long as they describe the result of the same behavior.

### Naming

Names should let the reader read off:
```text
condition / operation / expected result
```
Examples:
```text
withdraw_whenBalanceIsInsufficient_returnsInsufficientFunds
calculateTax_whenAmountIsExactlyThreshold_usesReducedRate
createUser_whenEmailAlreadyExists_doesNotPersistUser
```

### Structure

Use Arrange/Act/Assert, or Given/When/Then.

### No test-internal logic

`if`, `switch`, complex loops, or recomputing expected values inside the
test body are prohibited in principle, because defects can creep into the
test's own logic. Simple parameterized tests are allowed, but each row
must make clear which partition or boundary it represents.

### Do not test implementation details

* Do not call private methods directly
* Do not assert on local variables or internal data structures
* Do not pin a Mock's call order when it is not necessary
* Do not pin the shape of SQL or an internal algorithm

If a private method is too complex and you are tempted to test it
directly, consider extracting that logic into its own responsibility,
class, or pure function.

A test should, in principle, need no change when the production
implementation is refactored without changing its published behavior.
Excessive Mocking or Stubbing undermines this property.

## 11. Criteria for fixing defects

When fixing a defect found in production or acceptance testing, add a
regression test in principle. That test must satisfy:
1. Fails against the pre-fix implementation
2. Passes against the post-fix implementation
3. Uses the minimal input/state that reproduces the failure
4. Sits at the lowest appropriate test level possible
5. Also reviews the boundaries and equivalence partitions of the same
   defect class

Microsoft similarly recommends adding a corresponding regression test when
fixing a bug, so the past problem does not recur.
(https://learn.microsoft.com/en-us/cpp/code-quality/build-reliable-secure-programs?view=msvc-170)

However, do not try to reproduce defects caused by DB transaction isolation
levels or real inter-service contracts using Mock-centric unit tests alone.
In that case, add an Integration Test or Contract Test instead.

## 12. Choosing advanced techniques

### Property-based testing

Use it when a strong invariant exists, such as:
* Decoding after encoding returns the original value
* A serialize/deserialize round trip
* Sorting produces an ordered result and preserves the element set
* Running normalization multiple times does not change the result
* The sum after splitting an amount matches the original amount
* No crash on any valid arbitrary input

Property-based testing is a strong complement to ordinary unit tests, but
not necessarily a replacement. Keep boundary values and past-failure
inputs you always want to run as explicit tests.
(https://hypothesis.readthedocs.io/en/latest/tutorial/introduction.html)

### Mutation testing

Use it, scoped to changed code or high-risk pure logic, when:
* Coverage is high but defects are still frequent
* Assertions may be weak
* Important conditional logic involves money, authorization, tax, or
  discounts
* Complex comparison operators or Boolean expressions are involved

Mutation testing inserts small defects into the code and evaluates whether
tests catch them; it is a strong technique, but running it exhaustively is
computationally expensive, so scoping it to diffs and important areas is
realistic. Early on, do not gate on the overall score — instead review
which important mutants survived.
(https://research.google/pubs/state-of-mutation-testing-at-google/)

### Fuzzing

For parsers, decoders, file formats, and protocol handling that accept
untrusted external input, run Fuzzing as a separate process instead of
manually multiplying example-based unit tests into the hundreds. Add
reproducible inputs found by Fuzzing as regression tests.
