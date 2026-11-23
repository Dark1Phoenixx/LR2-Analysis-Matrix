import unittest
from unittest.mock import patch

from src.main import main


class MainTests(unittest.TestCase):
    def test_console_handles_valid_input(self):
        with patch("builtins.input", side_effect=["2", "3"]), patch("builtins.print") as output:
            main()
        output.assert_called_once_with("Количество положительных элементов:", 5)

    def test_console_rejects_noninteger_input(self):
        with patch("builtins.input", return_value="abc"), patch("builtins.print") as output:
            main()
        output.assert_called_once_with("Ошибка: необходимо вводить целые числа")

    def test_console_rejects_nonpositive_axis(self):
        for sizes in (["0", "2"], ["2", "0"]):
            with self.subTest(sizes=sizes):
                with patch("builtins.input", side_effect=sizes), patch("builtins.print") as output:
                    main()
                output.assert_called_once_with("Размеры матрицы должны быть положительными")
