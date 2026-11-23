import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.output_module import read_message, write_message
from src.worker import main


class WorkerTests(unittest.TestCase):
    def test_cli_handles_valid_and_invalid_requests(self):
        with tempfile.TemporaryDirectory() as directory:
            request = Path(directory) / "request.json"
            response = Path(directory) / "response.json"
            args = ["worker.py", "--request", str(request), "--response", str(response)]
            for rows, code, status in ((2, 0, "ok"), (0, 1, "error")):
                with self.subTest(rows=rows):
                    write_message(request, {"protocol_version": 1, "payload": {"rows": rows, "columns": 3}})
                    with patch("sys.argv", args), patch("sys.stderr") as stderr:
                        self.assertEqual(main(), code)
                    result = read_message(response)
                    self.assertEqual((result["protocol_version"], result["status"]), (1, status))
                    if code == 0:
                        self.assertEqual(result["data"]["positive_count"], 5)
                        stderr.write.assert_not_called()
                    else:
                        self.assertIn("положительным", result["error"])
                        stderr.write.assert_called()
