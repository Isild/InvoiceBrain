import unittest

from utils.elasticsearch import validate_sort_fields


class GetInvalidFieldsTestCase(unittest.TestCase):
    def test_detects_invalid_fields(self):
        fields_to_check = ["to tal", "amount", "inv oice"]
        allowed_fields = ["total", "invoice"]

        result = validate_sort_fields(fields_to_check, allowed_fields)
        self.assertEqual(result, False)

    def test_all_fields_valid(self):
        fields_to_check = ["total", " invoice"]
        allowed_fields = ["total", "invoice"]

        result = validate_sort_fields(fields_to_check, allowed_fields)
        self.assertEqual(result, True)

    def test_empty_fields_to_check(self):
        result = validate_sort_fields([], ["a", "b"])
        self.assertEqual(result, True)
