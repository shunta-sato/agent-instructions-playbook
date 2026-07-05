import unittest

from src.accounts import build_account_record, build_customer_profile
from src.service import dashboard_profile


ACCOUNT = {
    "id": "acct-1",
    "first_name": "Ada",
    "last_name": "Lovelace",
    "private_note": "vip",
}


class AccountTests(unittest.TestCase):
    def test_internal_profile(self):
        self.assertEqual(
            build_customer_profile(ACCOUNT),
            {"id": "acct-1", "display_name": "Ada Lovelace"},
        )

    def test_dashboard_profile_still_works(self):
        self.assertEqual(dashboard_profile(ACCOUNT), {"id": "acct-1", "name": "Ada Lovelace"})

    def test_public_adapter_preserves_old_record_shape(self):
        self.assertEqual(
            build_account_record(ACCOUNT, include_private=True),
            {"id": "acct-1", "name": "Ada Lovelace", "private_note": "vip"},
        )


if __name__ == "__main__":
    unittest.main()
