import unittest

from src.calculations import order_total
from src.fixture_helpers import make_order_fixture


class CalculationTests(unittest.TestCase):
    def test_order_total_for_single_item(self):
        order = make_order_fixture([{"price": 200, "quantity": 3}])
        self.assertEqual(order_total(order), 600)

    def test_order_total_for_multiple_items(self):
        order = make_order_fixture(
            [
                {"price": 200, "quantity": 3},
                {"price": 50, "quantity": 2},
            ]
        )
        self.assertEqual(order_total(order), 700)


if __name__ == "__main__":
    unittest.main()
