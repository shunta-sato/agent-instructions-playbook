import unittest

from src.importer import import_user
from src.preview import preview_user


class UserTests(unittest.TestCase):
    def test_import_normalizes_and_persists_user(self):
        store = {}
        result = import_user(
            {"id": " u-1 ", "email": " Test@Example.COM ", "name": " Ada   Lovelace "},
            store,
        )

        self.assertEqual(store["u-1"], result)

    def test_preview_does_not_persist(self):
        result = preview_user(
            {"id": " u-3 ", "email": " THREE@Example.COM ", "name": " Katherine   Johnson "}
        )

        self.assertEqual(result["email"], "three@example.com")


if __name__ == "__main__":
    unittest.main()
