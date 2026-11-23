import unittest

from src.processing_module import count_positive_elements, process


class ProcessingModuleTests(unittest.TestCase):
    def test_sign_changes_down_column(self):
        # sin(0) = 0; sin(1..3) > 0; sin(4) < 0.
        self.assertEqual(count_positive_elements(5, 1), 3)

    def test_result_for_rectangular_matrix(self):
        self.assertEqual(process(2, 3), {"rows": 2, "columns": 3, "positive_count": 5})
