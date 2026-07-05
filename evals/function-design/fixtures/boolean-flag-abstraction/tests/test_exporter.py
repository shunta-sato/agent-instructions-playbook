import unittest

from src.jobs import customer_export, tax_export


INVOICE = {
    "id": "inv-1",
    "customer": "Ada",
    "total": 1000,
    "tax": 80,
    "notes": "manual review",
}


class ExporterTests(unittest.TestCase):
    def test_customer_export(self):
        self.assertEqual(
            customer_export(INVOICE),
            {"id": "inv-1", "customer": "Ada", "total": 1000},
        )

    def test_tax_export(self):
        self.assertEqual(
            tax_export(INVOICE),
            {"id": "inv-1", "customer": "Ada", "total": 1000, "tax": 80},
        )


if __name__ == "__main__":
    unittest.main()
