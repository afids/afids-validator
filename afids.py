""" Utilities to create / maintain AFIDs objects """
from collections import defaultdict

def tree():
    """ Create a tree structure """
    return(defaultdict(tree))

class Afids:    
    def __init__(self, coordinate_system="LPS"):
        # Tree structure to store fiducial point info
        self.fiducials = tree()       

        self.coordinate_system = coordinate_system

    def set_coordinate_system(self, coordinate_system):
        self.coordinate_system = coordinate_system

    def get_coordinate_system(self):
        return(self.coordinate_system)

    def add_fiducial(self, label, description, positions):
        self.fiducials[str(label)]["description"] = description
        self.fiducials[str(label)]["positions"]["x"] = positions[0]
        self.fiducials[str(label)]["positions"]["y"] = positions[1]
        self.fiducials[str(label)]["positions"]["z"] = positions[2]

    def get_fiducial_description(self, label):
        return(self.fiducials[str(label)]["description"])

    def set_fiducial_positions(self, label, positions):
        self.fiducials[str(label)]["positions"]["x"] = positions[0]
        self.fiducials[str(label)]["positions"]["y"] = positions[1]
        self.fiducials[str(label)]["positions"]["z"] = positions[2]

    def set_fiducial_position(self, label, dim, position):
        self.fiducials[str(label)]["positions"][dim] = position

    def get_fiducial_positions(self, label):
        positions = (self.fiducials[str(label)]["positions"]["x"],
                     self.fiducials[str(label)]["positions"]["y"],
                     self.fiducials[str(label)]["positions"]["z"])
        
        return positions

    def get_fiducial_position(self, label, dim):
        return(self.fiducials[str(label)]["positions"][dim])
