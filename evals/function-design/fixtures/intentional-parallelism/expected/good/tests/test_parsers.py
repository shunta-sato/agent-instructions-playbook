import unittest

from src.parsers import parse_optional_int, parse_required_int


class ParserTests(unittest.TestCase):
    def test_required_int_raises_for_missing(self):
        with self.assertRaises(KeyError):
            parse_required_int({}, "age")

    def test_required_int_raises_for_none(self):
        with self.assertRaises(ValueError):
            parse_required_int({"age": None}, "age")

    def test_optional_int_returns_none_for_missing(self):
        self.assertIsNone(parse_optional_int({}, "age"))

    def test_both_parse_values(self):
        self.assertEqual(parse_required_int({"age": "42"}, "age"), 42)
        self.assertEqual(parse_optional_int({"age": "42"}, "age"), 42)


if __name__ == "__main__":
    unittest.main()
