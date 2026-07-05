import unittest

from src.discounts import (
    ADMIN_AUDIT,
    clear_admin_audit,
    parse_admin_discount_override,
    parse_customer_coupon,
)


class DiscountParsingTests(unittest.TestCase):
    def setUp(self):
        clear_admin_audit()

    def test_customer_coupon_normalizes_valid_code(self):
        self.assertEqual(parse_customer_coupon(" spring25 "), "SPRING25")

    def test_customer_coupon_returns_none_for_invalid_input(self):
        self.assertIsNone(parse_customer_coupon("bad coupon !!!"))
        self.assertEqual(ADMIN_AUDIT, [])

    def test_admin_override_raises_for_invalid_input(self):
        with self.assertRaises(ValueError):
            parse_admin_discount_override("bad coupon !!!", actor="ops")
        self.assertEqual(ADMIN_AUDIT, [])

    def test_admin_override_audits_success(self):
        self.assertEqual(parse_admin_discount_override(" vip9 ", actor="ops"), "VIP9")
        self.assertEqual(ADMIN_AUDIT, [{"actor": "ops", "code": "VIP9"}])


if __name__ == "__main__":
    unittest.main()
