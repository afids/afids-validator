import unittest
from fidvalidator import model_auto

class TestFcsvValidation(unittest.TestCase):
    def test_valid(self):
        fcsv_json = model_auto.csv_to_json('test/resources/valid.fcsv')

    def test_too_few_rows(self):
        with self.assertRaises(model_auto.InvalidFcsvError) as cm:
            fcsv_json = model_auto.csv_to_json(
                    'test/resources/too_few_rows.fcsv')

        self.assertEqual(cm.exception.message, 'Incorrect number of rows.')

    def test_too_few_columns(self):
        with self.assertRaises(model_auto.InvalidFcsvError) as cm:
            fcsv_json = model_auto.csv_to_json(
                    'test/resources/too_few_columns.fcsv')

        self.assertEqual(cm.exception.message,
                'Incorrect number of columns (13) in row 2')

    def test_missing_row(self):
        with self.assertRaises(model_auto.InvalidFcsvError) as cm:
            fcsv_json = model_auto.csv_to_json(
                    'test/resources/missing_row_10.fcsv')

        self.assertEqual(cm.exception.message, 'Row label 11 out of order')

if __name__ == '__main__':
    unittest.main()

