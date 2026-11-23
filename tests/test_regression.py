"""Keep fixed response-contract and import regressions from returning."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src.integration import IntegrationError, run
from src.output_module import write_message

REQUEST = {"protocol_version": 1, "payload": {"rows": 2, "columns": 3}}
ROOT = Path(__file__).resolve().parents[1]


class RegressionTests(unittest.TestCase):
    def check_worker_reply(self, **overrides):
        response = {
            "protocol_version": 1,
            "status": "ok",
            "data": {"rows": 2, "columns": 3, "positive_count": 5},
        }
        response.update(overrides)

        def reply(command, **kwargs):
            write_message(command[-1], response)
            return SimpleNamespace(returncode=0)

        with patch("src.integration.subprocess.run", side_effect=reply):
            return run(REQUEST)

    def test_response_rejects_bool_and_float_versions(self):
        for version in (True, 1.0):
            with self.subTest(version=version), self.assertRaisesRegex(IntegrationError, "Версия"):
                self.check_worker_reply(protocol_version=version)

    def test_response_rejects_missing_result_fields(self):
        with self.assertRaisesRegex(IntegrationError, "данных"):
            self.check_worker_reply(data={"rows": 2, "columns": 3})

    def test_response_rejects_wrong_dimensions_and_impossible_count(self):
        for rows, columns, count in ((3, 2, 5), (2, 3, 7), (2, 3, -1), (2, 3, True)):
            with self.subTest(rows=rows, columns=columns, count=count):
                with self.assertRaisesRegex(IntegrationError, "данных"):
                    self.check_worker_reply(data={"rows": rows, "columns": columns, "positive_count": count})

    def test_main_import_does_not_read_stdin(self):
        result = subprocess.run(
            [sys.executable, "-c", "import src.main"],
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env={**os.environ, "PYTHONUTF8": "1"},
            timeout=5,
            check=False,
        )
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))

    def test_cli_leaves_no_output_for_invalid_input(self):
        with tempfile.TemporaryDirectory() as directory:
            request = Path(directory) / "bad.json"
            response = Path(directory) / "response.json"
            request.write_text("{", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "src.integration", str(request), "--output", str(response)],
                cwd=ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env={**os.environ, "PYTHONUTF8": "1"},
                timeout=5,
                check=False,
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Ошибка интеграции", result.stderr)
            self.assertFalse(response.exists())
