# Failure Learning Record

Retrospective ID: R-20260727-retrospective-v1-shipping

## Trigger and scope

The completion claim for this wave's review-fix round was rejected twice
(round-1 and round-2 contract reviews both concluded no-submit) before
recovery — the rejected-completion-claim trigger. Scope: the review-fix
process of the failure-retrospective v1 change itself; no product code.

## Evidence sources

The three-round workflow-contract review report
(`reports/workflow-contract-review/20260727-failure-retrospective-v1.md`,
probe tables per round), the run ledger records 9c423e4c / 1ebcb5a5 /
eedb3e47, and the regression test added with the final fix.

## Attempt sequence

| Attempt | Hypothesis / approach | Evidence sought | Result | Failure class | What changed next |
|---|---|---|---|---|---|
| A1 | Scope closure rules 5.1/5.2 to a learning's optional attempt_refs (the F7 fix) | Unit suite + round-2 re-verification | rejected | verification | Round-2 re-ran the ORIGINAL probes and found F16: unresolvable refs silenced both rules (fail-open) |
| A2 | Amend to fail closed: unknown-ref findings + record-level fallback | Round-3 probe re-runs + full chain | succeeded | verification | n/a — accepted |

## Failed invariants and earliest signals

Failed invariant (A1): a closure-rule scoping mechanism must never let a
wrong reference disable the rule it scopes. Earliest signal: visible at
fix-authoring time — the `if r in by_id` guard discards without reporting;
a re-probe of the original F7 payload with a bad ref would have caught it
before submission. Preventability: preventable.

## Contrast with the final or current attempt

A2 differs from A1 in exactly one property: unresolvable references
produce findings and re-engage the record-level correlation instead of
silently narrowing the scope to nothing. The regression test asserts both
halves (the finding AND the re-engaged rule), so a future refactor cannot
silence the rule while keeping the finding.

## Learning claims

L1 (cross-project-reusable, model-evaluable, causal confidence confirmed):
a review fix can reopen the exact hole it closes in a more deniable form;
re-verification after fixes must re-run the original adversarial probes,
not re-read the diff. Two of this change's three blocking findings were
introduced or left by fixes; only probe re-runs caught them, across two
independent rounds — that repetition, not the final success alone, is what
confirms the causal claim.

## Promotion decisions

Existing-skill absorption: absorbed (skills considered:
receiving-code-review, failure-retrospective, quality-gate). The review
contract already mandates re-verification after fixes; the delta is the
re-probe-not-re-read practice, carried by this pack and the review
report's worked example. No new-skill-candidate. Enforceability is
model-evaluable (whether a re-verification re-ran probes is a judgment),
so closure rule 5.1 does not demand a lint; no wiki entry because the
learning is cross-project, not project-specific.

## Rejected non-lessons

"The reviewer should be more careful" — banned vague action, and wrong:
the reviewer's probe re-runs are what WORKED. "Add more review rounds" —
rounds were not the mechanism; probe re-execution was.

## Remaining unknowns

Whether the re-probe practice holds when the original review carried no
executable probes (documented as a does-not-apply-when bound).

## Closure

Disposition: amend-current-work — the fix was amended (A2) and accepted
(integrate-as-is, Decision submit). Retention: existing-skill (absorbed;
worked example in the review report) + retrospective-only (this pack).
Covers attempts A1, A2 and learning L1.
