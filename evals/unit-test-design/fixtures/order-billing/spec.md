# Fixture spec — order-billing (unit-test-design behavioral validation)

Implement a small Python module `billing.py` and its unit tests `test_billing.py`
in this fixture directory, per this spec. Python 3, stdlib only, tests runnable
with `python3 -m unittest test_billing` from the fixture directory.

## 1. `sku_label(sku_code: str, name: str) -> str`

Returns `f"{sku_code}: {name}"`. Pure formatting; no validation contract (callers
guarantee non-empty strings).

## 2. `volume_discount_rate(quantity: int) -> int`

Returns the discount rate in percent for an order line.

- Valid domain: `1 <= quantity <= 100`. Outside it, raise `ValueError`.
- `1..10` → `0`
- `11..50` → `5`
- `51..100` → `10`

The function receives `int` only (typed callers; `None`/float inputs are not part
of the contract).

## 3. `apply_refund(balance_cents: int, refund_cents: int, gateway) -> int`

Refunds money via a payment gateway and returns the new balance.

- Valid domain: `1 <= refund_cents <= balance_cents`. Outside it, raise `ValueError`
  WITHOUT contacting the gateway.
- On a valid refund: call `gateway.transfer(refund_cents)` **exactly once** (a
  duplicate transfer would double-refund real money), then return
  `balance_cents - refund_cents`.
- If `gateway.transfer` raises `GatewayError` (define it in `billing.py`), let the
  exception propagate; the returned/observable balance state must be unchanged
  (the function must not have committed anything before the transfer).
- `gateway` also exposes `log(message: str)`; logging content/order is NOT part of
  the contract.

Amounts are integer cents. This function moves real money.

## Deliverables

- `billing.py` — the module above.
- `test_billing.py` — unit tests for this module, designed and sized per this
  repository's playbook.

Follow the repository playbook for how to route, design, and verify this work.
