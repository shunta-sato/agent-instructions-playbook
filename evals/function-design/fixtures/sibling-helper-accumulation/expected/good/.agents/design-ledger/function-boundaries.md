# Function Boundary Design Ledger

## Decision type
- replaced abstraction

## Scope
- Module/files: `src/money.py`, `src/billing.py`
- Date: 2026-05-25

## Decision
- Old abstraction(s): `format_invoice_total`, `format_refund_total`, `format_credit_total`
- New abstraction(s): `format_money`
- Keep parallel? no

## Reasoning
- Concept boundaries: all removed helpers expressed the same money-formatting concept.
- Invariant ownership: currency suffix and cent conversion belong to `format_money`.
- Side-effect profile: pure formatting only.
- Error behavior: unchanged numeric formatting behavior.
- Future divergence expectation: low; call sites differ by billing kind, not formatting rule.

## Guardrails
- Do not reintroduce: per-kind money-formatting siblings or vague common/helper/util functions.
- Merge allowed only if the currency and rounding behavior remains shared.
- Adapter removal condition: not applicable.

## Verification evidence
- Commands: `python3 -m unittest discover -s tests`
- Results: pass
