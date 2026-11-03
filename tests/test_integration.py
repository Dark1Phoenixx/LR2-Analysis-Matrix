from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.input_module import InputDataError, validate_request
from src.integration import IntegrationError, run, run_file
from src.processing_module import count_positive_elements
from src.worker import handle


REQUEST = {"protocol_version": 1, "payload": {"rows": 2, "columns": 3}}


class InputTests(unittest.TestCase):
    def test_accepts_positive_integer_dimensions(self):
        self.assertEqual(validate_request(REQUEST), REQUEST)

    def test_rejects_missing_dimension(self):
        with self.assertRaisesRegex(InputDataError, "columns"):
            validate_request({"protocol_version": 1, "payload": {"rows": 2}})

    def test_rejects_non_positive_dimension(self):
        for value in (0, -1):
            with self.subTest(value=value), self.assertRaisesRegex(InputDataError, "положительным"):
                validate_request({"protocol_version": 1, "payload": {"rows": value, "columns": 2}})

    def test_rejects_bool_and_float_dimensions(self):
        for value in (True, 1.5):
            with self.subTest(value=value), self.assertRaisesRegex(InputDataError, "целым"):
                validate_request({"protocol_version": 1, "payload": {"rows": value, "columns": 2}})

    def test_rejects_incompatible_version(self):
        with self.assertRaisesRegex(InputDataError, "версия протокола"):
            validate_request({"protocol_version": 99, "payload": {"rows": 2, "columns": 3}})

    def test_rejects_boolean_protocol_version(self):
        with self.assertRaisesRegex(InputDataError, "версия протокола"):
            validate_request({"protocol_version": True, "payload": {"rows": 2, "columns": 3}})


class ProcessingTests(unittest.TestCase):
    def test_count_positive_elements_directly(self):
        # Test driver for the lower-level processing module (ascending strategy).
        self.assertEqual(count_positive_elements(2, 3), 5)

    def test_one_by_one_matrix_has_no_positive_elements(self):
        self.assertEqual(count_positive_elements(1, 1), 0)


class IntegrationTests(unittest.TestCase):
    def test_worker_response_for_two_by_three_matrix(self):
        response = run(REQUEST)
        self.assertEqual(response["status"], "ok")
        self.assertEqual(response["data"], {"rows": 2, "columns": 3, "positive_count": 5})

    def test_file_protocol_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "request.json"
            output_path = Path(directory) / "response.json"
            input_path.write_text('{"protocol_version":1,"payload":{"rows":2,"columns":3}}', encoding="utf-8")
            response = run_file(input_path, output_path)
            self.assertEqual(response["data"]["positive_count"], 5)
            self.assertEqual(output_path.exists(), True)

    def test_timeout_is_reported(self):
        with patch("src.integration.subprocess.run", side_effect=subprocess.TimeoutExpired("worker", 0.01)):
            with self.assertRaisesRegex(IntegrationError, "таймаут"):
                run(REQUEST, timeout=0.01)

    def test_unavailable_worker_is_reported(self):
        with patch("src.integration.subprocess.run", side_effect=OSError("worker missing")):
            with self.assertRaisesRegex(IntegrationError, "недоступен"):
                run(REQUEST)

    def test_missing_response_is_reported(self):
        class Completed:
            returncode = 0
            stdout = ""
            stderr = ""

        with patch("src.integration.subprocess.run", return_value=Completed()):
            with self.assertRaisesRegex(IntegrationError, "не создал"):
                run(REQUEST)

    def test_worker_rejects_bad_request(self):
        with self.assertRaisesRegex(InputDataError, "положительным"):
            handle({"protocol_version": 1, "payload": {"rows": 0, "columns": 3}})


if __name__ == "__main__":
    unittest.main()
