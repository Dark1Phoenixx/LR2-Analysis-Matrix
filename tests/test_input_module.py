import unittest

from src.input_module import InputDataError, validate_request


class InputModuleTests(unittest.TestCase):
    def test_version_condition_combinations(self):
        # (not int, bool, != 1): all six realizable combinations.
        cases = (
            (1, True),
            (2, False),
            (True, False),
            (False, False),
            (1.0, False),
            ("1", False),
        )
        for version, accepted in cases:
            with self.subTest(version=version):
                request = {"protocol_version": version, "payload": {"rows": 1, "columns": 1}}
                if accepted:
                    self.assertEqual(validate_request(request), request)
                else:
                    with self.assertRaisesRegex(InputDataError, "версия"):
                        validate_request(request)

    def test_rejects_non_object_request(self):
        with self.assertRaisesRegex(InputDataError, "Запрос"):
            validate_request([])

    def test_rejects_non_object_payload(self):
        with self.assertRaisesRegex(InputDataError, "payload"):
            validate_request({"protocol_version": 1, "payload": None})

    def test_dimension_boundaries_in_each_field(self):
        for field in ("rows", "columns"):
            for value in (-1, 0, 1, 2):
                with self.subTest(field=field, value=value):
                    payload = {"rows": 1, "columns": 1}
                    payload[field] = value
                    request = {"protocol_version": 1, "payload": payload}
                    if value >= 1:
                        self.assertEqual(validate_request(request)["payload"], payload)
                    else:
                        with self.assertRaisesRegex(InputDataError, field):
                            validate_request(request)
