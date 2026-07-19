# Blind behavioral validation — order-billing fixture (2026-07-19)

## Protocol

A Sonnet playbook-worker received ONLY `spec.md` and the instruction to follow the
repository playbook. No skill names were mentioned in the brief. The judge's oracle
(`oracle.md`) was held outside the worktree until judging completed. Worker run:
`20260719T015223Z-unit_test_single_case-d9e2ac96` (accepted). The produced
`billing.py` / `test_billing.py` are kept exactly as the worker delivered them —
including the deviations noted below — so this directory records what the skills
actually produced, not a cleaned-up version.

## Routing result (from the worker's report)

dev-workflow → project-structure → **unit-test-design** → implementation-economy →
observability → structure watch → quality-gate. Both target skills were reached
blind; **comment-discipline** governed comment decisions via the dev-workflow
branch line.

## Judgment against the oracle

| Oracle item | Result |
| --- | --- |
| `sku_label` classified E | PASS (E; see finding F2 on the dedicated test) |
| `volume_discount_rate` tier | Worker chose H via the billing category; the oracle's S call was WRONG against the policy (discount/rate math is listed under money/billing). Oracle corrected. |
| `apply_refund` classified H | PASS |
| S/H boundary sets present and correct | PASS with finding F1: 3-value applied only at the outer domain edges (1, 100 → 0,1,2 / 99,100,101); internal tier boundaries 10/11 and 50/51 got 2-value treatment despite the H classification |
| No `None`/float/NaN tests outside contract | PASS (none present) |
| No cross-product, no duplicate-partition padding | PASS (19 cases, envelope 15–30) |
| Full refund (`refund == balance`) present | PASS (100 → 0) |
| Invalid refund → ValueError without gateway contact | PASS (transfer_calls asserted empty) |
| `transfer` exactly-once as interaction contract | PASS (asserted `[refund_cents]`, not call-count-free) |
| GatewayError propagation, no retry | PASS |
| No verification of `log` content/order | PASS (fake accepts and discards; a Why-not comment explains the choice) |
| Test names condition/operation/result; AAA; no test logic | PASS (subTest parametrization with partition labels — explicitly allowed) |
| Comment discipline: no How/What restating comments | PASS (zero inline implementation comments; docstrings are contract documentation, the carve-out; row labels state which partition/boundary each case covers, which the skill requires) |
| Determinism (no sleep/time/random) | PASS |

## Findings → actions

- **F1 (fixed in the skill)**: the H rule "3-value boundaries" was applied only at the
  outer domain edges. The reference now states the tier's boundary treatment applies
  at EVERY identified boundary, result-changing internal boundaries included.
- **F2 (fixed in the skill)**: the worker wrote one dedicated test for the E-tier
  unit. The reference now states the E default action explicitly: record the
  classification, add no dedicated test unless a special-value trigger applies.
- **F3 (oracle corrected, no skill change)**: the oracle originally classified
  `volume_discount_rate` as S; the policy's own money/billing category covers
  rate/discount math, so the worker's H was right. A tier tie-break line was added
  to the reference so the next reader does not waver the other way.
- **Observation (no action)**: the worker did not add a mid-partition normal value
  for the 11–50 and 51–100 partitions (boundary members cover the partitions). The
  policy requires one normal value per examined range, which is satisfied; the
  stricter per-partition reading in the oracle's first draft was not policy text.
- **Observation (no action)**: the observability skill triggered on the external
  `gateway.transfer` call and the worker used the interface's existing `log` hook on
  the success path — spec-permitted, not asserted on by tests, consistent with the
  interaction-contract rule.
