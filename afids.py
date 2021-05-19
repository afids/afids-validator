""" Utilities to create / maintain AFIDs objects """
from collections import defaultdict
import math


EXPECTED_LABELS = [str(x + 1) for x in range(32)]
EXPECTED_DESCS = [
    ["AC"],
    ["PC"],
    ["infracollicular sulcus", "ICS"],
    ["PMJ"],
    ["superior interpeduncular fossa", "SIPF"],
    ["R superior LMS", "RSLMS"],
    ["L superior LMS", "LSLMS"],
    ["R inferior LMS", "RILMS"],
    ["L inferior LMS", "LILMS"],
    ["Culmen", "CUL"],
    ["Intermammillary sulcus", "IMS"],
    ["R MB", "RMB"],
    ["L MB", "LMB"],
    ["pineal gland", "PG"],
    ["R LV at AC", "RLVAC"],
    ["L LV at AC", "LLVAC"],
    ["R LV at PC", "RLVPC"],
    ["L LV at PC", "LLVPC"],
    ["Genu of CC", "GENU"],
    ["Splenium of CC", "SPLE"],
    ["R AL temporal horn", "RALTH"],
    ["L AL temporal horn", "LALTH"],
    ["R superior AM temporal horn", "RSAMTH"],
    ["L superior AM temporal horn", "LSAMTH"],
    ["R inferior AM temporal horn", "RIAMTH"],
    ["L inferior AM temporal horn", "RIAMTH"],
    ["R indusium griseum origin", "RIGO"],
    ["L indusium griseum origin", "LIGO"],
    ["R ventral occipital horn", "RVOH"],
    ["L ventral occipital horn", "LVOH"],
    ["R olfactory sulcal fundus", "ROSF"],
    ["L olfactory sulcal fundus", "LOSF"],
]
EXPECTED_MAP = dict(zip(EXPECTED_LABELS, EXPECTED_DESCS))


def tree():
    """Create a tree structure"""
    return defaultdict(tree)


class Afids:
    """Class representing a complete set of AFIDs."""

    def __init__(self, coordinate_system="LPS", no_of_fiducials=0):
        """Initialize tree structure to store fiducial point info"""
        self.fiducials = tree()
        self.coordinate_system = coordinate_system
        self.no_of_fiducials = no_of_fiducials

    def add_fiducial(self, label, description, positions):
        """Add fiducial to tree"""
        self.fiducials[str(label)]["description"] = description
        self.set_fiducial_positions(label, positions)

        # Add to the fiducial count
        self.no_of_fiducials += 1

    def get_fiducial_description(self, label):
        """Extract fiducial description"""
        return self.fiducials[str(label)]["description"]

    def set_fiducial_positions(self, label, positions):
        """Set position of fiducial"""
        self.fiducials[str(label)]["positions"]["x"] = positions[0]
        self.fiducials[str(label)]["positions"]["y"] = positions[1]
        self.fiducials[str(label)]["positions"]["z"] = positions[2]

    def set_fiducial_position(self, label, dim, position):
        """Set position for single dimension of fiducial"""
        self.fiducials[str(label)]["positions"][dim] = position

    def get_fiducial_positions(self, label):
        """Get fiducial position"""
        positions = (
            self.fiducials[str(label)]["positions"]["x"],
            self.fiducials[str(label)]["positions"]["y"],
            self.fiducials[str(label)]["positions"]["z"],
        )

        return positions

    def get_fiducial_position(self, label, dim):
        """Get single dimension position of fiducial"""
        return self.fiducials[str(label)]["positions"][dim]

    def validate(self):
        """Validate that the class represents a valid AFIDs set.

        Returns
        -------
        bool
            True if the Afids set is valid.
        """
        valid = self.no_of_fiducials == 32
        valid = valid and set(self.fiducials.keys()) == set(EXPECTED_LABELS)
        for label, fiducial in self.fiducials.items():
            valid = valid and fiducial["description"].lower() in [
                expected_desc.lower() for expected_desc in EXPECTED_MAP[label]
            ]
            try:
                valid = valid and math.isfinite(
                    float(fiducial["positions"]["x"])
                )
                valid = valid and math.isfinite(
                    float(fiducial["positions"]["y"])
                )
                valid = valid and math.isfinite(
                    float(fiducial["positions"]["z"])
                )
            except ValueError:
                valid = False
            except KeyError:
                valid = False
        return valid
