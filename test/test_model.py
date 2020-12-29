import unittest
import json
import model

class TestFcsvValidation(unittest.TestCase):
    # Test fcsv
    def test_valid_fcsv(self):
        with open("test/resources/valid.fcsv", "r") as fcsv:
            model.csv_to_afids(fcsv)

    def test_valid_fcsv_flip(self):
        with open("test/resources/valid_flip.fcsv", "r") as fcsv:
            fcsv_afids = model.csv_to_afids(fcsv)

        self.assertEqual(float(fcsv_afids.get_fiducial_position(1, "x")), 
                -0.07077182344203692)
        self.assertEqual(float(fcsv_afids.get_fiducial_position(1, "y")), 
                0.2548674381652525)

    def test_valid_nhp(self):
        with open("test/resources/valid_nhp.fcsv", "r") as fcsv:
            model.csv_to_afids(fcsv)

    def test_invalid_version(self):
        with open("test/resources/invalid_version.fcsv", "r") as fcsv:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.csv_to_afids(fcsv)

        self.assertEqual(cm.exception.message,
            "Markups fiducial file version 3.5 too low")

    def test_invalid_content(self):
        with open("test/resources/invalid_content.fcsv", "r") as fcsv:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.csv_to_afids(fcsv)

        self.assertEqual(cm.exception.message,
            "Missing or invalid header in fiducial file")

        with open("test/resources/invalid_content_valid_header.fcsv",
                "r") as fcsv:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.csv_to_afids(fcsv)

        self.assertEqual(cm.exception.message,
            "Row has no value label")

    def test_too_few_rows(self):
        with open("test/resources/too_few_rows.fcsv", "r") as fcsv:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.csv_to_afids(fcsv)

        self.assertEqual(cm.exception.message, "Too few rows")

    def test_too_many_rows(self):
        with open("test/resources/too_many_rows.fcsv", "r") as fcsv:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.csv_to_afids(fcsv)

        self.assertEqual(cm.exception.message, "Too many rows")

    def test_too_few_columns(self):
        with open("test/resources/too_few_columns.fcsv", "r") as fcsv:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.csv_to_afids(fcsv)

        self.assertEqual(cm.exception.message,
                "Incorrect number of columns (13) in row 2")

    def test_too_many_columns(self):
        with open("test/resources/too_many_columns.fcsv", "r") as fcsv:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.csv_to_afids(fcsv)

        self.assertEqual(cm.exception.message,
                "Incorrect number of columns (15) in row 2")

    def test_incorrect_desc(self):
        with open("test/resources/incorrect_desc.fcsv", "r") as fcsv:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.csv_to_afids(fcsv)

        self.assertEqual(cm.exception.message,
                "Row label 2 does not match row description dummy")

    def test_invalid_coord(self):
        with open("test/resources/invalid_coord.fcsv", "r") as fcsv:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.csv_to_afids(fcsv)

        self.assertEqual(cm.exception.message,
                "z in row 2 is not a real number")

    def test_infinite_coord(self):
        with open("test/resources/infinite_coord.fcsv", "r") as fcsv:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.csv_to_afids(fcsv)

        self.assertEqual(cm.exception.message,
                "z in row 2 is not finite")

    def test_missing_row(self):
        with open("test/resources/missing_row_10.fcsv", "r") as fcsv:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.csv_to_afids(fcsv)

        self.assertEqual(cm.exception.message, "Too few rows")


class TestJsonValidation(unittest.TestCase):
    # Test json
    def test_valid(self):
        with open("test/resources/valid.json", "r") as json_file:
            model.json_to_afids(json.load(json_file))

    # NOT WORKING
    # def test_valid_json_flip(self):
    #     with open("test/resources/valid_flip.json", "r") as json_file:
    #         model.json_to_afids(json.load(json_file))

        # self.assertEqual(float(json_afids.get_fiducial_position(1, "x")), 
        #         0.07077182344203692)
        # self.assertEqual(float(json_afids.get_fiducial_position(1, "y")), 
        #         -0.2548674381652525)

    def test_valid_nhp(self):
        with open("test/resources/valid_nhp.json", "r") as json_file:
            model.json_to_afids(json.load(json_file))

    # IS VERSION A CONCERN HERE (NOT A FIELD IN JSON FILES)
    # def test_invalid_version(self):
    #     with open("test/resources/invalid_version.fcsv", "r") as fcsv:
    #         with self.assertRaises(model.InvalidFileError) as cm:
    #             model.csv_to_afids(fcsv)

    #     self.assertEqual(cm.exception.message,
    #         "Markups fiducial file version 3.5 too low")

    # def test_invalid_content_json(self):
        # # CURRENTLY FAILS WITH JSON ERROR
        # with open("test/resources/invalid_content.json", "r") as json_file:
        #     with self.assertRaises(model.InvalidFileError) as cm:
        #         model.json_to_afids(json.load(json_file))

        # self.assertEqual(cm.exception.message,
        #     "Missing or invalid header in fiducial file")

        # DON'T THINK HEADER IS AN ISSUE ANYMORE HERE?
    #     with open("test/resources/invalid_content_valid_header.fcsv",
    #             "r") as fcsv:
    #         with self.assertRaises(model.InvalidFileError) as cm:
    #             model.csv_to_afids(fcsv)

    #     self.assertEqual(cm.exception.message,
    #         "Row has no value label")

    def test_too_few_rows(self):
        with open("test/resources/too_few_rows.json", "r") as json_file:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.json_to_afids(json.load(json_file))

        self.assertEqual(cm.exception.message, "Too few rows")

    def test_too_many_rows(self):
        with open("test/resources/too_many_rows.json", "r") as json_file:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.json_to_afids(json.load(json_file))

        self.assertEqual(cm.exception.message, "Too many rows")

    # NO LONGER HAVE COLUMNS, SHOULD CHECK FOR KEYS INSTEAD?
    # def test_too_few_columns(self):
    #     with open("test/resources/too_few_columns.fcsv", "r") as fcsv:
    #         with self.assertRaises(model.InvalidFileError) as cm:
    #             model.csv_to_afids(fcsv)

    #     self.assertEqual(cm.exception.message,
    #             "Incorrect number of columns (13) in row 2")

    # def test_too_many_columns(self):
    #     with open("test/resources/too_many_columns.fcsv", "r") as fcsv:
    #         with self.assertRaises(model.InvalidFileError) as cm:
    #             model.csv_to_afids(fcsv)

    #     self.assertEqual(cm.exception.message,
    #             "Incorrect number of columns (15) in row 2")

    def test_incorrect_desc(self):
        with open("test/resources/incorrect_desc.json", "r") as json_file:
            with self.assertRaises(model.InvalidFileError) as cm:
                model.json_to_afids(json.load(json_file))

        self.assertEqual(cm.exception.message,
                "Fiducial label 2 does not match fiducial description dummy")

    # CURRENTLY THROWING JSON ERROR
    # def test_invalid_coord(self):
    #     with open("test/resources/invalid_coord.json", "r") as json_file:
    #         with self.assertRaises(model.InvalidFileError) as cm:
    #             model.json_to_afids(json.load(json_file))

    #     self.assertEqual(cm.exception.message,
    #             "z in row 2 is not a real number")

    # ALSO NOT WORKING CURRENTLY
    # def test_infinite_coord(self):
    #     with open("test/resources/infinite_coord.json", "r") as json_file:
    #         with self.assertRaises(model.InvalidFileError) as cm:
    #             model.json_to_afids(json.load(json_file))

    #     self.assertEqual(cm.exception.message,
    #             "z in row 2 is not finite")

    # Currently skips "missing" all together and checks for next
    # def test_missing_row(self):
    #     with open("test/resources/missing_row_10.json", "r") as json_file:
    #         with self.assertRaises(model.InvalidFileError) as cm:
    #             model.json_to_afids(json.load(json_file))

    #     self.assertEqual(cm.exception.message, "Too few rows")


if __name__ == "__main__":
    unittest.main()