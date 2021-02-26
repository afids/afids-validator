import unittest

import afids


class TestAfidsValidation(unittest.TestCase):
    def test_valid_afids(self):
        test_afids = afids.Afids()
        for label, descs in afids.EXPECTED_MAP.items():
            test_afids.add_fiducial(label, descs[0], ["0", "1", "2"])
        self.assertTrue(test_afids.validate())

    def test_empty_afids(self):
        test_afids = afids.Afids()
        self.assertFalse(test_afids.validate())
