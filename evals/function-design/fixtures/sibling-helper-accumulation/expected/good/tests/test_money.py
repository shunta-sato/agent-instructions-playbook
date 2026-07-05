import unittest

from src.billing import credit_line, invoice_line, refund_line, subscription_line
from src.money import format_money


class MoneyTests(unittest.TestCase):
    def test_format_money(self):
        self.assertEqual(format_money(1234), "$12.34 USD")

    def test_all_lines_format_money(self):
        self.assertEqual(invoice_line(1234), {"kind": "invoice", "total": "$12.34 USD"})
        self.assertEqual(refund_line(500), {"kind": "refund", "total": "$5.00 USD"})
        self.assertEqual(credit_line(990), {"kind": "credit", "total": "$9.90 USD"})
        self.assertEqual(subscription_line(2500), {"kind": "subscription", "total": "$25.00 USD"})


if __name__ == "__main__":
    unittest.main()
