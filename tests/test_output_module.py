import tempfile
import unittest
from pathlib import Path

from src.output_module import format_result, read_message, write_message


class OutputModuleTests(unittest.TestCase):
    def test_utf8_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "message.json"
            message = {"error": "Ошибка"}
            write_message(path, message)
            self.assertEqual(read_message(path), message)
            self.assertIn("Ошибка", path.read_text(encoding="utf-8"))

    def test_rejects_json_array(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "array.json"
            path.write_text("[]", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "объектом"):
                read_message(path)

    def test_formats_result(self):
        result = {"data": {"rows": 2, "columns": 3, "positive_count": 5}}
        self.assertEqual(format_result(result), "Размер матрицы: 2 x 3\nПоложительных элементов: 5")
