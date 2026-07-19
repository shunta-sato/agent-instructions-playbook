# Unit test case design reference

Covers: scope, risk tiers, the design-basis matrix, boundary values, multi-input/combination testing, state transitions, the stop criteria, and the PR review checklist. For coverage gates, test doubles, isolation/speed/style, regression-fix criteria, and advanced techniques, see `references/unit-test-operations.md`.

## Scope and headline policy

This policy targets ordinary business systems, web/API services, and mobile
applications. It excludes regulated domains such as medical, aviation,
automotive, and safety-control systems. Where regulation, contract, or an
industry standard imposes a different requirement, that requirement takes
priority over this policy.

Headline rule: normally, test **specified behavior + equivalence
partitioning + 2-value boundary values**. Escalate to 3-value boundaries,
combinatorial testing, state transitions, and Mutation Testing only for
high-risk areas (money, authorization, data loss, and similar). Do not
target 100% coverage overall — judge changed code strictly instead. The
acceptance criterion is not "every value, every combination, every private
method tested," but whether **each test case reduces at least one distinct
risk**.

ISTQB describes the purpose of test techniques as "systematically deriving a
relatively small, but sufficient, test set." Equivalence partitioning takes,
in principle, one case per partition; boundary value testing has 2-value and
3-value variants; and when condition combinations grow too large, decision
table reduction or risk-based selection is accepted. "Normally 2-value,
3-value for high-risk" is therefore consistent with standard test design
technique. (ISTQB CTFL Syllabus: https://istqb.org/?download_id=3345&sdm_process_download=1)

## 1. Purpose of unit tests

Limit the purpose of a unit test to these three points:
1. Verify, quickly, behavior specified in the spec that must not break
2. Detect regressions from a change, early and close to the developer
3. Leave an executable document of how the implementation is used and what
   it is expected to do

A unit test fundamentally tests a **small range of observable behavior**,
not "one method." Google's own practice treats being small, fast,
deterministic, and easy to diagnose on failure as important productivity
properties of unit tests. (SWE Book ch12: https://abseil.io/resources/swe-book/html/ch12.html)

Do not force DB constraints, SQL dialects, communication with external
services, framework configuration, or real-browser behavior into unit
tests — delegate them to Integration Tests, Contract Tests, Component
Tests, and E2E Tests. The test pyramid's basic shape has many unit tests,
but Google's "80% / 15% / 5%" is also only a rough guideline, and the ratio
itself should not become a KPI. (SWE Book ch11: https://abseil.io/resources/swe-book/html/ch11.html)

## 2. Risk tiers (E / S / H)

Classify every unit-test target into one of three tiers:

| Tier | Judgment | Applied policy |
| --- | --- | --- |
| **E: dedicated-test exemption candidate** | Auto-generated code, declaration-only DTOs, logic-free getters/setters, simple DI wiring, pure delegation to a framework | No dedicated unit test required in principle. Confirm via compilation, static analysis, and integration tests |
| **S: standard** | Ordinary business logic, transformations, calculations, input validation, branching logic | Equivalence partitioning + 2-value boundary values + the main results |
| **H: high risk** | Money, tax, billing, authentication, authorization, personal data, data deletion, irreversible external operations, public API compatibility, concurrency, complex state machines, failure-prone areas | 3-value boundary values, decision tables, state transitions, strong branch criteria, Mutation/PBT as needed |

Tier tie-breaks (both observed in blind validation):
* A computation whose result directly determines a charged or paid amount
  (rates, discounts, tax, billing math) falls under the money/billing
  category — **H** — even when the unit itself does not move the money.
* For an E-tier unit, record the classification and add NO dedicated test
  unless a special-value trigger (see the special-values section) applies;
  compilation, static analysis, and integration tests are its verification.

When the tier is unclear, use this formula:
```text
Risk score = impact (1-3) x likelihood of defect (1-3)
```
6 or higher is high risk. However, treat anything with clearly large impact
regardless of the score — authorization, payment, data loss, regulatory
violation — as high risk. Evaluating risk from likelihood and impact, and
varying test scope, technique, priority, and effort by the result, matches
ISTQB's risk-based testing.

Judge "likelihood of defect" from these factors:
* Complex conditional branches, states, or formulas
* Handles concurrency, date/time, randomness, or floating point
* Changed frequently
* The same kind of failure has happened before
* Parses or transforms external input
* Unfamiliar territory for the implementer or reviewer

## 3. Test design basis matrix

| Aspect | Standard S | High-risk H |
| --- | --- | --- |
| Specified results | All identified results | Same |
| Equivalence partitioning | One case each from valid/invalid partitions with distinct meaning | Same |
| Boundary values | 2-value boundary + 1 normal value | 3-value boundary + 1 normal value |
| Condition combinations | Small decision table: all cases. Large: reduce + cover important rules | Important rules: all cases. Remaining: reduction/combinatorial technique |
| State transitions | All valid transitions + a representative invalid transition | All valid transitions + high-impact invalid transitions |
| Coverage | Changed lines 90%, changed branches 80% | Changed branches 90% |
| Advanced techniques | Only when needed | Selectively use Mutation, Property-based, Fuzzing |

An "invalid partition" here applies **only when the unit itself has a
contract to handle invalid input**. There is no need to mechanically add
values such as `null` that are unreachable from the caller or the type
system and are not part of the unit's contract.

## 4. Boundary value testing — concrete criteria

### 4.1 Standard is 2-value boundary + normal value

ISTQB's 2-value boundary testing uses, for one boundary, "the boundary
value" and "the nearest value in the adjacent partition." 3-value boundary
testing uses the boundary value and both of its neighbors, which can catch
implementation errors that 2-value testing would miss.

For example, take this spec:
```text
1 <= quantity <= 100
```
#### Standard S
```text
0, 1, 50, 100, 101
```
Meanings:
* `0`: invalid partition below the lower bound
* `1`: lower bound
* `50`: a normal valid value
* `100`: upper bound
* `101`: invalid partition above the upper bound

#### High-risk H
```text
0, 1, 2, 50, 99, 100, 101
```
Check both sides of the lower and upper bound.

Using this "5 for standard, 7 for high-risk" as the initial baseline for a
simple lower/upper-bound check keeps the test count down while making
`<` vs `<=` mistakes, off-by-one boundaries, and implementations that only
pass on the boundary itself easier to catch.

However, if pricing or the processing result differs across `1-10`,
`11-50`, and `51-100`, those are not the same valid partition. Add a test
for each of those boundaries, and apply the tier's boundary treatment
(2-value for S, 3-value for H) at EVERY identified boundary — the
result-changing internal boundaries included, not only the outer domain
edges.

### 4.2 The unit of an "adjacent value"

Do not mechanically use `+/-1`. Use **the smallest unit that has meaning in
the spec**.

| Data | Adjacent-value definition |
| --- | --- |
| Integer count | +/-1 |
| Money | The smallest currency unit, e.g. 1 yen, 1 cent |
| Date | 1 day |
| Time | 1 second if the spec is in seconds, 1 millisecond if in milliseconds |
| String length | 1 character if the spec counts characters, 1 byte if it counts bytes |
| Version | The spec's next/previous value, e.g. under semantic versioning |
| Floating point | Not machine epsilon — the spec's tolerance or rounding unit |

Avoid habitually inserting "boundary +/- machine epsilon" for floating
point. Test against the business rounding unit, display precision, or
comparison tolerance instead.

### 4.3 Special values only when the meaning differs

Do not mechanically test the following values against every function:
```text
null, empty string, whitespace-only string, empty collection, NaN,
Infinity, a type's min/max value, overflow, Unicode combining characters,
timezone, DST
```
Add one only as an independent equivalence partition when at least one of
these applies:
* It may be accepted per the API contract
* It is reachable from an actual input path
* It produces a different result than a normal value
* There is a related past incident
* It could cause problems in casting, arithmetic, storage, or serialization
* It is security-relevant

For example, whether a string-length limit of "255 characters" means 255
characters or 255 UTF-8 bytes changes what tests are needed substantially.
Test the business/API-contract boundary first, not the implementation
type's boundary.

## 5. Multiple inputs and combination testing

### 5.1 Independent inputs are not a full cartesian product

When input items are independent, build one standard input set and pass
each input's equivalence partitions through at least once. Having 3
partitions for each of 3 inputs does not mean, in principle, building
`3 x 3 x 3 = 27` cases. ISTQB calls the criterion of passing every
partition of every input at least once "Each Choice," but Each Choice does
not guarantee coverage of combinations between inputs.

### 5.2 Use a decision table when the result changes by combination

Use a decision table when:
* Membership tier combines with a campaign
* Contract status, payment status, and permission combine
* Multiple flags change the result or a side effect
* Conditions have a priority order
* Some condition combination is impossible

This policy's initial criteria:
* **16 or fewer feasible decision rules**: test all rules
* **17 or more**: remove infeasible conditions and conditions that do not
  affect the result
* After reduction: test every distinct result and every high-risk rule
* Reduce the remaining conditions using Pairwise
* Add known 3+-factor interactions explicitly — do not leave them to
  Pairwise

Decision tables grow exponentially with the number of conditions, so ISTQB
also accepts reduction and risk-based selection. NIST research also shows
that most defects are caused by interactions of one or two parameters, and
that combinatorial testing works effectively with a smaller test set than
the full cartesian product. However, Pairwise is not a technique that
guarantees catching all defects, and it is not a reason to omit known
important multi-factor rules.

## 6. State transition criteria

For classes and domain models with state, prioritize state transitions over
plain input values.

### Standard S
* Every valid transition at least once
* Invalid transitions that produce the same rejection result: one
  representative per equivalence class
* Transitions with a side effect: verify both the state change and the
  side effect

### High-risk H
* Every valid transition
* Invalid transitions that lead to money, authorization, or data loss
* Re-execution of an operation that requires idempotency
* State after a mid-way failure
* State after retry, cancel, or timeout

ISTQB treats "all valid transitions" as the common baseline, and treats
"all transitions, including invalid ones," as the minimum bar in
safety/mission-critical domains. Uniformly testing every invalid cell in
ordinary business software tends to be excessive, so the usual target is
"equivalence classes of invalid transitions" for standard, and "high-impact
invalid transitions" for high risk.

## 13. Stop criteria to prevent "over-testing"

A new test case or parameterized row must add at least one of the
following:
1. A new specified behavior or result
2. A new valid or invalid equivalence partition
3. A new boundary value
4. A new important decision rule
5. A new state transition
6. Prevention of regression for a past defect
7. A high-risk invariant
8. Detection of an important surviving mutant

**As a rule, do not add a test that adds none of these.**

For example, avoid:
* Picking 10 normal values from the same equivalence partition without
  justification
* Building the full cartesian product of every input combination
* Exhaustively testing every getter/setter
* Creating one test per private method
* Writing weak-assertion tests just to raise line coverage
* Duplicating verification of the same behavior across multiple layers
* Pinning a Mock's call order when the spec does not require it

Conversely, normal test design for a unit can be considered finished once:
```text
Every identified behavior has been verified
+ every equivalence partition with distinct meaning has been verified
+ risk-appropriate boundary values have been verified
+ important combinations and state transitions have been verified
+ the changed-code coverage criteria are met
+ the risk of any untested area has been accepted in review
```

## PR review checklist

```text
[ ] Classified the target as E, S, or H
[ ] Tests public behavior and expected results
[ ] Identified equivalence partitions with distinct meaning
[ ] Confirmed 2-value boundaries for standard, 3-value for high-risk
[ ] Did not build meaningless full combinations
[ ] Used a decision table or combinatorial technique when conditions
    depend on each other
[ ] Confirmed valid transitions and important invalid transitions for
    stateful targets
[ ] Added a regression test for defect fixes
[ ] Met changed-line 90% and changed-branch 80%
[ ] Met branch 90% for high-risk changes
[ ] Does not depend on network, a real DB, sleep, or the real clock
[ ] Mock call verification covers only interactions the spec requires
[ ] Each test case adds a distinct risk or coverage item
[ ] Introduces no new known flaky test
```

The center of this standard is not "increasing the number of test cases"
but "covering distinct failure causes — spec, boundary, branch, state, and
past defects — with as few tests as possible." Continuously watching the
diff, important untested branches, execution time, flaky count, and the
content of escaped defects — rather than overall coverage or test count —
is the operating approach that best balances efficiency and effectiveness.
