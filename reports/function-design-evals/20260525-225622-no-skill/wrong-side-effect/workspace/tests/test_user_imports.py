import unittest

from src.user_imports import (
    AUDIT_LOG,
    clear_audit_log,
    import_user,
    preview_user_import,
    update_user_from_admin,
)


def fixed_clock():
    return "2026-05-25T00:00:00Z"


class UserImportTests(unittest.TestCase):
    def setUp(self):
        clear_audit_log()

    def test_import_user_normalizes_and_persists(self):
        repository = []
        user = import_user({"email": "  ALICE@Example.COM ", "name": " Alice   Doe "}, repository, fixed_clock)

        self.assertEqual(user["email"], "alice@example.com")
        self.assertEqual(user["name"], "Alice Doe")
        self.assertEqual(user["updated_at"], "2026-05-25T00:00:00Z")
        self.assertEqual(repository, [user])
        self.assertEqual(AUDIT_LOG, [{"event": "user_imported", "email": "alice@example.com"}])

    def test_update_user_from_admin_keeps_existing_side_effects(self):
        repository = []
        user = update_user_from_admin({"email": "ROOT@example.com", "name": " Root "}, repository, fixed_clock)

        self.assertEqual(user["source"], "admin")
        self.assertEqual(repository, [user])
        self.assertEqual(len(AUDIT_LOG), 1)

    def test_preview_user_import_is_pure_normalization(self):
        repository = []
        preview = preview_user_import({"email": "  ALICE@Example.COM ", "name": " Alice   Doe "})

        self.assertEqual(preview, {"email": "alice@example.com", "name": "Alice Doe"})
        self.assertEqual(repository, [])
        self.assertEqual(AUDIT_LOG, [])
        self.assertNotIn("updated_at", preview)

    def test_invalid_email_raises(self):
        with self.assertRaises(ValueError):
            import_user({"email": "not-email", "name": "Bad"}, [], fixed_clock)


if __name__ == "__main__":
    unittest.main()
