import unittest

from src.importer import import_user
from src.users import normalize_and_save_user


class UserTests(unittest.TestCase):
    def test_import_normalizes_and_persists_user(self):
        store = {}
        result = import_user(
            {"id": " u-1 ", "email": " Test@Example.COM ", "name": " Ada   Lovelace "},
            store,
        )

        self.assertEqual(
            result,
            {"id": "u-1", "email": "test@example.com", "name": "Ada Lovelace"},
        )
        self.assertEqual(store["u-1"], result)

    def test_old_function_returns_normalized_user(self):
        store = {}
        result = normalize_and_save_user(
            {"id": " u-2 ", "email": " TWO@Example.COM ", "name": " Grace   Hopper "},
            store,
        )

        self.assertEqual(result["email"], "two@example.com")
        self.assertIn("u-2", store)


if __name__ == "__main__":
    unittest.main()
