"""Test templates"""

import unittest
from pathlib import Path

from afidsvalidator import model


class TestTemplates(unittest.TestCase):
    """A test for the provided template validity"""

    def test_human_templates(self):
        """Test that each human template is valid."""
        for template_file in Path(
            "afidsvalidator/afids-templates/human"
        ).iterdir():
            with self.subTest(template_file=template_file):
                with open(template_file, "r", encoding="utf-8") as fcsv:
                    afids = model.csv_to_afids(fcsv.read())
                self.assertTrue(afids.validate())
