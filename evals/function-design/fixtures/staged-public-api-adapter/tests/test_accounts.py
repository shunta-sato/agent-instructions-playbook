import unittest

from src.accounts import build_account_record
from src.service import dashboard_profile


ACCOUNT = {
    "id": "acct-1",
    "first_name": "Ada",
    "last_name": "Lovelace",
    "private_note": "vip",
}


class AccountTests(unittest.TestCase):
    def test_dashboard_profile(self):
        self.assertEqual(dashboard_profile(ACCOUNT), {"id": "acct-1", "name": "Ada Lovelace"})

    def test_public_record_can_include_private_note(self):
        self.assertEqual(
            build_account_record(ACCOUNT, include_private=True),
            {"id": "acct-1", "name": "Ada Lovelace", "private_note": "vip"},
        )


if __name__ == "__main__":
    unittest.main()
