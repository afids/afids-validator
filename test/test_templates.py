from pathlib import Path
import unittest

from afidsvalidator import model


class TestTemplates(unittest.TestCase):
    def test_human_templates(self):
        for template_file in Path(
            "afidsvalidator/afids-templates/human"
        ).iterdir():
            with self.subTest(template_file=template_file):
                with open(template_file, "r", encoding="utf-8") as fcsv:
                    afids = model.csv_to_afids(fcsv.read())
                self.assertTrue(afids.validate())
