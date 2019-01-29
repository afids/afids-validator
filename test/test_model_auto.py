import unittest
from fidvalidator import model_auto

class TestFcsvValidation(unittest.TestCase):
    def test_valid(self):
        fcsv_json = model_auto.csv_to_json('test/resources/valid.fcsv')

    def test_invalid_version(self):
        with self.assertRaises(model_auto.InvalidFcsvError) as cm:
            fcsv_json = model_auto.csv_to_json(
                    'test/resources/invalid_version.fcsv')

        self.assertEqual(cm.exception.message,
            'Markups fiducial file version 3.5 too low')

    def test_too_few_rows(self):
        with self.assertRaises(model_auto.InvalidFcsvError) as cm:
            fcsv_json = model_auto.csv_to_json(
                    'test/resources/too_few_rows.fcsv')

        self.assertEqual(cm.exception.message, 'Too few rows')

    def test_too_many_rows(self):
        with self.assertRaises(model_auto.InvalidFcsvError) as cm:
            fcsv_json = model_auto.csv_to_json(
                    'test/resources/too_many_rows.fcsv')

        self.assertEqual(cm.exception.message, 'Too many rows')

    def test_too_few_columns(self):
        with self.assertRaises(model_auto.InvalidFcsvError) as cm:
            fcsv_json = model_auto.csv_to_json(
                    'test/resources/too_few_columns.fcsv')

        self.assertEqual(cm.exception.message,
                'Incorrect number of columns (13) in row 2')

    def test_too_many_columns(self):
        with self.assertRaises(model_auto.InvalidFcsvError) as cm:
            fcsv_json = model_auto.csv_to_json(
                    'test/resources/too_many_columns.fcsv')

        self.assertEqual(cm.exception.message,
                'Incorrect number of columns (15) in row 2')

    def test_incorrect_desc(self):
        with self.assertRaises(model_auto.InvalidFcsvError) as cm:
            fcsv_json = model_auto.csv_to_json(
                    'test/resources/incorrect_desc.fcsv')

        self.assertEqual(cm.exception.message,
                'Row label 2 does not match row description dummy')

    def test_invalid_coord(self):
        with self.assertRaises(model_auto.InvalidFcsvError) as cm:
            fcsv_json = model_auto.csv_to_json(
                    'test/resources/invalid_coord.fcsv')

        self.assertEqual(cm.exception.message,
                'z in row 2 is not a real number')

    def test_infinite_coord(self):
        with self.assertRaises(model_auto.InvalidFcsvError) as cm:
            fcsv_json = model_auto.csv_to_json(
                    'test/resources/infinite_coord.fcsv')

        self.assertEqual(cm.exception.message,
                'z in row 2 is not finite')

    def test_missing_row(self):
        with self.assertRaises(model_auto.InvalidFcsvError) as cm:
            fcsv_json = model_auto.csv_to_json(
                    'test/resources/missing_row_10.fcsv')

        self.assertEqual(cm.exception.message, 'Row label 11 out of order')

if __name__ == '__main__':
    unittest.main()

