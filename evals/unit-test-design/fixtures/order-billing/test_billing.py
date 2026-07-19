"""Unit tests for billing.py, sized per this repository's unit-test-design
playbook (risk-tiered: E/S/H, equivalence partitions + boundary values,
stop criteria in the design reference).

Risk classification:
- sku_label: E-tier (pure formatting, no validation contract) -> one
  specified-behavior test.
- volume_discount_rate: H-tier (billing calculation feeding money
  downstream) -> 3-value domain boundaries + a test for each rate-changing
  tier boundary, covering every specified result.
- apply_refund: H-tier (moves real money, explicit "exactly once" and
  "no partial commit" contract) -> 3-value refund_cents boundaries, the
  "no contact on invalid input" interaction contract, and GatewayError
  propagation with an attempted-exactly-once check.
"""

import unittest

from billing import GatewayError, apply_refund, sku_label, volume_discount_rate


class FakeGateway:
    """Deterministic test double for the payment gateway.

    Records transfer() calls so tests can verify the "exactly once" and
    "no contact on invalid input" interaction contract from spec.md.
    Logging content/order is explicitly not part of the contract, so
    log() just accepts calls without recording anything tests assert on.
    """

    def __init__(self, raises=None):
        self.transfer_calls = []
        self._raises = raises

    def transfer(self, amount_cents):
        self.transfer_calls.append(amount_cents)
        if self._raises is not None:
            raise self._raises

    def log(self, message):
        pass


class SkuLabelTests(unittest.TestCase):
    def test_sku_label_formats_code_and_name(self):
        self.assertEqual(sku_label("SKU-1", "Widget"), "SKU-1: Widget")


class VolumeDiscountRateTests(unittest.TestCase):
    def test_valid_quantities_return_expected_rate(self):
        # (quantity, expected_rate). Covers: 3-value lower domain boundary
        # (1, 2 alongside the invalid 0 below), the 10/11 and 50/51
        # tier-changing boundaries (result differs across partitions), and
        # 3-value upper domain boundary (99, 100 alongside invalid 101).
        cases = [
            (1, 0),
            (2, 0),
            (10, 0),
            (11, 5),
            (50, 5),
            (51, 10),
            (99, 10),
            (100, 10),
        ]
        for quantity, expected_rate in cases:
            with self.subTest(quantity=quantity):
                self.assertEqual(volume_discount_rate(quantity), expected_rate)

    def test_invalid_quantities_raise_value_error(self):
        # 3-value boundary neighbors of the domain edges: 0 (just below 1),
        # 101 (just above 100).
        for quantity in (0, 101):
            with self.subTest(quantity=quantity):
                with self.assertRaises(ValueError):
                    volume_discount_rate(quantity)


class ApplyRefundTests(unittest.TestCase):
    def test_valid_refunds_call_gateway_once_and_return_new_balance(self):
        # balance_cents fixed at 100. (refund_cents, expected_new_balance).
        # Covers: 3-value lower boundary (1, 2), a normal mid value (50),
        # and 3-value upper boundary (99, 100 = full refund).
        cases = [
            (1, 99),
            (2, 98),
            (50, 50),
            (99, 1),
            (100, 0),
        ]
        for refund_cents, expected_balance in cases:
            with self.subTest(refund_cents=refund_cents):
                gateway = FakeGateway()
                result = apply_refund(100, refund_cents, gateway)
                self.assertEqual(result, expected_balance)
                self.assertEqual(gateway.transfer_calls, [refund_cents])

    def test_invalid_refunds_raise_without_contacting_gateway(self):
        # balance_cents fixed at 100. 3-value boundary neighbors of the
        # domain edges: 0 (just below the lower bound 1), 101 (just above
        # the upper bound = balance_cents).
        for refund_cents in (0, 101):
            with self.subTest(refund_cents=refund_cents):
                gateway = FakeGateway()
                with self.assertRaises(ValueError):
                    apply_refund(100, refund_cents, gateway)
                self.assertEqual(gateway.transfer_calls, [])

    def test_gateway_error_propagates_and_transfer_attempted_exactly_once(self):
        gateway = FakeGateway(raises=GatewayError("transfer declined"))
        with self.assertRaises(GatewayError):
            apply_refund(100, 1, gateway)
        # Not retried, and no second/duplicate transfer attempt.
        self.assertEqual(gateway.transfer_calls, [1])


if __name__ == "__main__":
    unittest.main()
