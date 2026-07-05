import unittest

from src.helpers import build_order_lines
from src.order_totals import subtotal_cents, total_cents


class OrderTotalTests(unittest.TestCase):
    def test_us_order_over_threshold_gets_free_shipping(self):
        lines = build_order_lines()
        self.assertEqual(subtotal_cents(lines), 5300)
        self.assertEqual(total_cents(lines, "US"), 5300)

    def test_ca_order_pays_shipping(self):
        lines = build_order_lines()
        self.assertEqual(subtotal_cents(lines), 5300)
        self.assertEqual(total_cents(lines, "CA"), 6200)


if __name__ == "__main__":
    unittest.main()
