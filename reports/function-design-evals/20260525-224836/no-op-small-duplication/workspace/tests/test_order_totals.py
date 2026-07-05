import unittest

from src.order_totals import subtotal_cents, total_cents


class OrderTotalTests(unittest.TestCase):
    def test_us_order_over_threshold_gets_free_shipping(self):
        lines = [
            {"sku": "BOOK", "unit_cents": 2500, "quantity": 2},
            {"sku": "PEN", "unit_cents": 300, "quantity": 1},
        ]
        self.assertEqual(subtotal_cents(lines), 5300)
        self.assertEqual(total_cents(lines, "US"), 5300)

    def test_ca_order_pays_shipping(self):
        lines = [
            {"sku": "BOOK", "unit_cents": 2500, "quantity": 2},
            {"sku": "PEN", "unit_cents": 300, "quantity": 1},
        ]
        self.assertEqual(subtotal_cents(lines), 5300)
        self.assertEqual(total_cents(lines, "CA"), 6200)


if __name__ == "__main__":
    unittest.main()
