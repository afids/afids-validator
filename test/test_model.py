"""Test models"""

import unittest

from afidsvalidator import model
from afidsvalidator.model import HumanFiducialSet

# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring


class TestHumanFiducialSet(unittest.TestCase):
    def test_empty_afids(self):
        test_afids = model.HumanFiducialSet()
        self.assertFalse(test_afids.validate())

    def test_valid_afids(self):
        test_afids = model.HumanFiducialSet()
        for descs in model.EXPECTED_MAP.values():
            test_afids.add_fiducial(descs[-1], ["0", "1", "2"])
        self.assertTrue(test_afids.validate())


class TestFcsvValidation(unittest.TestCase):
    # Test fcsv
    def test_valid_fcsv(self):
        with open("test/resources/valid.fcsv", "r", encoding="utf-8") as fcsv:
            afids = model.csv_to_afids(fcsv.read())
        self.assertTrue(afids.validate())

    def test_valid_fcsv_flip(self):
        with open(
            "test/resources/valid_flip.fcsv", "r", encoding="utf-8"
        ) as fcsv:
            fcsv_afids = model.csv_to_afids(fcsv.read())
        self.assertTrue(fcsv_afids.validate())

        self.assertEqual(
            fcsv_afids.AC_x,
            -0.07077182344203692,
        )
        self.assertEqual(fcsv_afids.AC_y, 0.2548674381652525)

    def test_valid_nhp(self):
        with open(
            "test/resources/valid_nhp.fcsv", "r", encoding="utf-8"
        ) as fcsv:
            self.assertTrue(model.csv_to_afids(fcsv.read()).validate())

    def test_invalid_version(self):
        with open(
            "test/resources/invalid_version.fcsv", "r", encoding="utf-8"
        ) as fcsv:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.csv_to_afids(fcsv.read())

        self.assertEqual(
            custom_message.exception.message,
            "Markups fiducial file version 3.5 too low",
        )

    def test_invalid_content(self):
        with open(
            "test/resources/invalid_content.fcsv", "r", encoding="utf-8"
        ) as fcsv:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.csv_to_afids(fcsv.read())

        self.assertEqual(
            custom_message.exception.message,
            "Missing or invalid header in fiducial file",
        )

        with open(
            "test/resources/invalid_content_valid_header.fcsv",
            "r",
            encoding="utf-8",
        ) as fcsv:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.csv_to_afids(fcsv.read())

        self.assertEqual(
            custom_message.exception.message, "Row has no value label"
        )

    def test_too_few_rows(self):
        with open(
            "test/resources/too_few_rows.fcsv", "r", encoding="utf-8"
        ) as fcsv:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.csv_to_afids(fcsv.read())

        self.assertEqual(custom_message.exception.message, "Too few rows")

    def test_too_many_rows(self):
        with open(
            "test/resources/too_many_rows.fcsv", "r", encoding="utf-8"
        ) as fcsv:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.csv_to_afids(fcsv.read())

        self.assertEqual(custom_message.exception.message, "Too many rows")

    def test_too_few_columns(self):
        with open(
            "test/resources/too_few_columns.fcsv", "r", encoding="utf-8"
        ) as fcsv:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.csv_to_afids(fcsv.read())

        self.assertEqual(
            custom_message.exception.message,
            "Incorrect number of columns (13) in row 2",
        )

    def test_too_many_columns(self):
        with open(
            "test/resources/too_many_columns.fcsv", "r", encoding="utf-8"
        ) as fcsv:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.csv_to_afids(fcsv.read())

        self.assertEqual(
            custom_message.exception.message,
            "Incorrect number of columns (15) in row 2",
        )

    def test_incorrect_desc(self):
        with open(
            "test/resources/incorrect_desc.fcsv", "r", encoding="utf-8"
        ) as fcsv:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.csv_to_afids(fcsv.read())

        self.assertEqual(
            custom_message.exception.message,
            "Row label 2 does not match row description dummy",
        )

    def test_invalid_coord(self):
        with open(
            "test/resources/invalid_coord.fcsv", "r", encoding="utf-8"
        ) as fcsv:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.csv_to_afids(fcsv.read())

        self.assertEqual(
            custom_message.exception.message, "z in row 2 is not a real number"
        )

    def test_infinite_coord(self):
        with open(
            "test/resources/infinite_coord.fcsv", "r", encoding="utf-8"
        ) as fcsv:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.csv_to_afids(fcsv.read())

        self.assertEqual(
            custom_message.exception.message, "z in row 2 is not finite"
        )

    def test_missing_row(self):
        with open(
            "test/resources/missing_row_10.fcsv", "r", encoding="utf-8"
        ) as fcsv:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.csv_to_afids(fcsv.read())

        self.assertEqual(custom_message.exception.message, "Too few rows")


class TestJsonValidation(unittest.TestCase):
    # Test json
    def test_valid(self):
        with open(
            "test/resources/valid.json", "r", encoding="utf-8"
        ) as json_file:
            self.assertTrue(model.json_to_afids(json_file.read()).validate())

    def test_valid_flip(self):
        with open(
            "test/resources/valid_flip.json", "r", encoding="utf-8"
        ) as json_file:
            json_afids = model.json_to_afids(json_file.read())
        self.assertTrue(json_afids.validate())

        self.assertEqual(
            json_afids.AC_x,
            0.07077182344203692,
        )
        self.assertEqual(
            json_afids.AC_y,
            -0.2548674381652525,
        )

    def test_valid_nhp(self):
        with open(
            "test/resources/valid_nhp.json", "r", encoding="utf-8"
        ) as json_file:
            self.assertTrue(model.json_to_afids(json_file.read()).validate())

    def test_valid_misordered(self):
        with open(
            "test/resources/valid_misordered.json", "r", encoding="utf-8"
        ) as json_file:
            self.assertTrue(model.json_to_afids(json_file.read()).validate())

    def test_invalid_content(self):
        with open(
            "test/resources/invalid_content.json", "r", encoding="utf-8"
        ) as json_file:
            with self.assertRaises(model.InvalidFileError):
                model.json_to_afids(json_file.read())

    def test_too_few_rows(self):
        with open(
            "test/resources/too_few_rows.json", "r", encoding="utf-8"
        ) as json_file:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.json_to_afids(json_file.read())

        self.assertEqual(custom_message.exception.message, "Too few fiducials")

    def test_too_many_rows(self):
        with open(
            "test/resources/too_many_rows.json", "r", encoding="utf-8"
        ) as json_file:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.json_to_afids(json_file.read())

        self.assertEqual(
            custom_message.exception.message, "Too many fiducials"
        )

    def test_too_few_coords(self):
        with open(
            "test/resources/too_few_coords.json", "r", encoding="utf-8"
        ) as json_file:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.json_to_afids(json_file.read())

        self.assertEqual(
            custom_message.exception.message,
            "Fiducial AC does not have three coordinates",
        )

    def test_incorrect_desc(self):
        with open(
            "test/resources/incorrect_desc.json", "r", encoding="utf-8"
        ) as json_file:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.json_to_afids(json_file.read())

        self.assertEqual(
            custom_message.exception.message,
            "Fiducial label 2 does not match fiducial description dummy",
        )

    def test_invalid_coord(self):
        with open(
            "test/resources/invalid_coord.json", "r", encoding="utf-8"
        ) as json_file:
            json_lines = json_file.readlines()

        with self.assertRaises(model.InvalidFileError) as custom_message:
            model.json_to_afids("".join(json_lines))
        self.assertEqual(
            custom_message.exception.message,
            "z (dummy) in fiducial 2 is not a real number",
        )

        invalid_coords = ["[0.3, 0.4]", '{"z": 0.3}', "true", "false", "null"]

        errors = ["[0.3, 0.4]", "{'z': 0.3}", "True", "False", "None"]

        for invalid_coord, error in zip(invalid_coords, errors):
            json_lines[28] = f'"position": [0.1, 0.2, {invalid_coord}],'
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.json_to_afids("".join(json_lines))
            self.assertEqual(
                custom_message.exception.message,
                f"z ({error}) in fiducial 2 is not a real number",
            )

    def test_missing_row(self):
        with open(
            "test/resources/missing_row_10.json", "r", encoding="utf-8"
        ) as json_file:
            with self.assertRaises(model.InvalidFileError) as custom_message:
                model.json_to_afids(json_file.read())

        self.assertEqual(custom_message.exception.message, "Too few fiducials")


class TestDBreadandwrite(unittest.TestCase):
    def test_add_read_and_validate(self):
        test_afids = HumanFiducialSet()
        for descs in model.EXPECTED_DESCS:
            test_afids.add_fiducial(descs[-1], ["0", "1", "2"])
        self.assertTrue(test_afids.validate())


if __name__ == "__main__":
    unittest.main()
