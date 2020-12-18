""" Utilities to create / maintain AFIDs objects """
from collections import defaultdict


def tree():
    """ Create a tree structure """
    return defaultdict(tree)


class Afids:
    def __init__(self, coordinate_system="LPS", no_of_fiducials=0):
        """ Initialize tree structure to store fiducial point info """
        self.fiducials = tree()
        self.coordinate_system = coordinate_system
        self.no_of_fiducials = no_of_fiducials

    def add_fiducial(self, label, description, positions):
        """ Add fiducial to tree """
        self.fiducials[str(label)]["description"] = description
        self.set_fiducial_positions(label, positions)

        # Add to the fiducial count
        self.no_of_fiducials += 1

    def get_fiducial_description(self, label):
        """ Extract fiducial description """
        return self.fiducials[str(label)]["description"]

    def set_fiducial_positions(self, label, positions):
        """ Set position of fiducial """
        self.fiducials[str(label)]["positions"]["x"] = positions[0]
        self.fiducials[str(label)]["positions"]["y"] = positions[1]
        self.fiducials[str(label)]["positions"]["z"] = positions[2]

    def set_fiducial_position(self, label, dim, position):
        """ Set position for single dimension of fiducial """
        self.fiducials[str(label)]["positions"][dim] = position

    def get_fiducial_positions(self, label):
        """ Get fiducial position """
        positions = (
            self.fiducials[str(label)]["positions"]["x"],
            self.fiducials[str(label)]["positions"]["y"],
            self.fiducials[str(label)]["positions"]["z"],
        )

        return positions

    def get_fiducial_position(self, label, dim):
        """ Get single dimension position of fiducial """
        return self.fiducials[str(label)]["positions"][dim]

    def validate(self):
        # TO BE CREATED
        return None
