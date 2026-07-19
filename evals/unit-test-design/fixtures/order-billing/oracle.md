# Oracle — order-billing fixture (held out of the worktree during validation)

NOTE (post-judgment): two items below were corrected by the validation itself and
are preserved as originally written for evidence integrity — see
validation-report.md F3 (the S call for `volume_discount_rate` was wrong against
the policy's money/billing category) and the per-partition normal-value bar
(stricter than policy text).

Judged against unit-test-design + comment-discipline. Each item marks PASS/FAIL.

## Tier classification (expected)

- `sku_label` → **E** (pure formatting, no logic): NO dedicated test, or at most one
  incidental usage. Dedicated exhaustive tests = over-testing FAIL.
- `volume_discount_rate` → **S** (business logic, branches; no money movement).
- `apply_refund` → **H** (money movement, irreversible external op; risk ≥ 6).

## volume_discount_rate (S: equivalence partitions + 2-value BVA + one normal per partition)

Three DIFFERENT valid partitions (0%, 5%, 10%) → the 1..100 range is NOT one
partition; each internal boundary needs cases.

Expected value set (2-value BVA at each boundary + normals):
- invalid low: `0` (ValueError)
- `1` (→0), `10` (→0), `11` (→5), `50` (→5), `51` (→10), `100` (→10)
- invalid high: `101` (ValueError)
- normals: at least one interior value per partition (e.g. 5, 30, 75) — but a
  single normal per partition; 10 near-identical interior values = stop-criteria FAIL.

PASS bar: all 8 boundary values present with correct expected rates/errors; ≤ ~12
cases total for this function; no 3-value (±2) expansion (S tier, 2-value suffices);
no `None`/float/NaN tests (outside contract — special-values rule);
no cross-product with other functions' inputs.

## apply_refund (H: 3-value BVA + interaction contract + failure state)

- 3-value boundaries on `refund_cents` against both edges (1 and balance):
  with e.g. balance=100: `0,1,2` and `99,100,101` plus a mid value. Missing ±2
  values = 3-value rule not applied (FAIL for H tier).
- `refund_cents = balance` (full refund → 0) expected present.
- Invalid inputs (0, balance+1, and ideally negative) → ValueError AND
  gateway.transfer NOT called (contract says no contact).
- `gateway.transfer` called EXACTLY ONCE on success — interaction-as-contract
  (double-refund). Mock/spy verification here is CORRECT per the double ladder.
- GatewayError propagation with balance unchanged.
- NOT expected: verification of `log` calls/order (log is not a contract) —
  verifying log order = mock-overuse FAIL.
- Test double: hand-rolled fake/spy or Mock is fine; real network obviously absent.

## Cross-cutting

- Test names: condition/operation/expected-result readable (any consistent scheme).
- AAA/GWT structure; no if/switch/loops re-computing expectations in test bodies.
- No test for private helpers (if the worker factors any).
- Determinism: no sleep/time/random dependence.

## comment-discipline expectations

- Implementation comments: ONLY Why-not content (if any). Zero diff-narration
  ("added validation"), zero How-restating ("loop over tiers"), zero
  What-restating above obvious lines ("returns the label"). Docstrings: public
  API docstrings are the contract-documentation carve-out — acceptable (concise);
  restating the signature in prose inside comments = FAIL.
- Test comments: expected behavior must live in test names/structure, not
  comments above asserts. Partition/boundary labels in parametrized rows are
  allowed (the skill requires knowing which partition each row covers).

## Stop-criteria / size envelope (whole file)

- Total test methods (or parametrized rows) roughly 15–30. >40 = over-testing
  signal; <10 = under-testing signal (H-tier 3-value set alone needs ~8).
- Every case maps to a distinct partition/boundary/rule/interaction; no
  duplicate-partition padding.
