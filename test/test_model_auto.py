import unittest
from fidvalidator import model_auto

class TestFcsvValidation(unittest.TestCase):
    def test_valid(self):
        fcsv_json = model_auto.csv_to_json('test/resources/test_afids.fcsv')
        self.assertEqual(model_auto.validate_afids_json(fcsv_json), {'valid': True})

if __name__ == '__main__':
    unittest.main()

