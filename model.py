"""Handle parsing files to internal AFIDs representation."""

import io
import csv
import json
import math
import re

from pkg_resources import parse_version

from controller import db
from sqlalchemy.orm import composite

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


class FiducialPosition(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __composite_values__(self):
        return self.x, self.y, self.z

    def __repr__(self):
        return "FiducialPosition(x=%r, y=%r, z=%r)" % (self.x, self.y, self.z)

    def __eq__(self, other):
        return (
            isinstance(other, FiducialPosition)
            and other.x == self.x
            and other.y == self.y
            and other.z == self.z
        )

    def __ne__(self, other):
        return not self.__eq__(other)


class FiducialSet(db.Model):
    """SQL model for a set of AFIDs."""

    __tablename__ = "fid_db"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String)
    date = db.Column(db.Date)
    template = db.Column(db.String)
    no_of_fiducials = db.Column(db.Integer)

    AC_x = db.Column(db.Float())
    AC_y = db.Column(db.Float())
    AC_z = db.Column(db.Float())
    AC = composite(FiducialPosition, AC_x, AC_y, AC_z)

    PC_x = db.Column(db.Float())
    PC_y = db.Column(db.Float())
    PC_z = db.Column(db.Float())
    PC = composite(FiducialPosition, PC_x, PC_y, PC_z)

    ICS_x = db.Column(db.Float())
    ICS_y = db.Column(db.Float())
    ICS_z = db.Column(db.Float())
    ICS = composite(FiducialPosition, ICS_x, ICS_y, ICS_z)

    PMJ_x = db.Column(db.Float())
    PMJ_y = db.Column(db.Float())
    PMJ_z = db.Column(db.Float())
    PMJ = composite(FiducialPosition, PMJ_x, PMJ_y, PMJ_z)

    SIPF_x = db.Column(db.Float())
    SIPF_y = db.Column(db.Float())
    SIPF_z = db.Column(db.Float())
    SIPF = composite(FiducialPosition, SIPF_x, SIPF_y, SIPF_z)

    RSLMS_x = db.Column(db.Float())
    RSLMS_y = db.Column(db.Float())
    RSLMS_z = db.Column(db.Float())
    RSLMS = composite(FiducialPosition, RSLMS_x, RSLMS_y, RSLMS_z)

    LSLMS_x = db.Column(db.Float())
    LSLMS_y = db.Column(db.Float())
    LSLMS_z = db.Column(db.Float())
    LSLMS = composite(FiducialPosition, LSLMS_x, LSLMS_y, LSLMS_z)

    RILMS_x = db.Column(db.Float())
    RILMS_y = db.Column(db.Float())
    RILMS_z = db.Column(db.Float())
    RILMS = composite(FiducialPosition, RILMS_x, RILMS_y, RILMS_z)

    LILMS_x = db.Column(db.Float())
    LILMS_y = db.Column(db.Float())
    LILMS_z = db.Column(db.Float())
    LILMS = composite(FiducialPosition, LILMS_x, LILMS_y, LILMS_z)

    CUL_x = db.Column(db.Float())
    CUL_y = db.Column(db.Float())
    CUL_z = db.Column(db.Float())
    CUL = composite(FiducialPosition, CUL_x, CUL_y, CUL_z)

    IMS_x = db.Column(db.Float())
    IMS_y = db.Column(db.Float())
    IMS_z = db.Column(db.Float())
    IMS = composite(FiducialPosition, IMS_x, IMS_y, IMS_z)

    RMB_x = db.Column(db.Float())
    RMB_y = db.Column(db.Float())
    RMB_z = db.Column(db.Float())
    RMB = composite(FiducialPosition, RMB_x, RMB_y, RMB_z)

    LMB_x = db.Column(db.Float())
    LMB_y = db.Column(db.Float())
    LMB_z = db.Column(db.Float())
    LMB = composite(FiducialPosition, LMB_x, LMB_y, LMB_z)

    PG_x = db.Column(db.Float())
    PG_y = db.Column(db.Float())
    PG_z = db.Column(db.Float())
    PG = composite(FiducialPosition, PG_x, PG_y, PG_z)

    RLVAC_x = db.Column(db.Float())
    RLVAC_y = db.Column(db.Float())
    RLVAC_z = db.Column(db.Float())
    RLVAC = composite(FiducialPosition, RLVAC_x, RLVAC_y, RLVAC_z)

    LLVAC_x = db.Column(db.Float())
    LLVAC_y = db.Column(db.Float())
    LLVAC_z = db.Column(db.Float())
    LLVAC = composite(FiducialPosition, LLVAC_x, LLVAC_y, LLVAC_z)

    RLVPC_x = db.Column(db.Float())
    RLVPC_y = db.Column(db.Float())
    RLVPC_z = db.Column(db.Float())
    RLVPC = composite(FiducialPosition, RLVPC_x, RLVPC_y, RLVPC_z)

    LLVPC_x = db.Column(db.Float())
    LLVPC_y = db.Column(db.Float())
    LLVPC_z = db.Column(db.Float())
    LLVPC = composite(FiducialPosition, LLVPC_x, LLVPC_y, LLVPC_z)

    GENU_x = db.Column(db.Float())
    GENU_y = db.Column(db.Float())
    GENU_z = db.Column(db.Float())
    GENU = composite(FiducialPosition, GENU_x, GENU_y, GENU_z)

    SPLE_x = db.Column(db.Float())
    SPLE_y = db.Column(db.Float())
    SPLE_z = db.Column(db.Float())
    SPLE = composite(FiducialPosition, SPLE_x, SPLE_y, SPLE_z)

    RALTH_x = db.Column(db.Float())
    RALTH_y = db.Column(db.Float())
    RALTH_z = db.Column(db.Float())
    RALTH = composite(FiducialPosition, RALTH_x, RALTH_y, RALTH_z)

    LALTH_x = db.Column(db.Float())
    LALTH_y = db.Column(db.Float())
    LALTH_z = db.Column(db.Float())
    LALTH = composite(FiducialPosition, LALTH_x, LALTH_y, LALTH_z)

    RSAMTH_x = db.Column(db.Float())
    RSAMTH_y = db.Column(db.Float())
    RSAMTH_z = db.Column(db.Float())
    RSAMTH = composite(FiducialPosition, RSAMTH_x, RSAMTH_y, RSAMTH_z)

    LSAMTH_x = db.Column(db.Float())
    LSAMTH_y = db.Column(db.Float())
    LSAMTH_z = db.Column(db.Float())
    LSAMTH = composite(FiducialPosition, LSAMTH_x, LSAMTH_y, LSAMTH_z)

    RIAMTH_x = db.Column(db.Float())
    RIAMTH_y = db.Column(db.Float())
    RIAMTH_z = db.Column(db.Float())
    RIAMTH = composite(FiducialPosition, RIAMTH_x, RIAMTH_y, RIAMTH_z)

    LIAMTH_x = db.Column(db.Float())
    LIAMTH_y = db.Column(db.Float())
    LIAMTH_z = db.Column(db.Float())
    LIAMTH = composite(FiducialPosition, LIAMTH_x, LIAMTH_y, LIAMTH_z)

    RIGO_x = db.Column(db.Float())
    RIGO_y = db.Column(db.Float())
    RIGO_z = db.Column(db.Float())
    RIGO = composite(FiducialPosition, RIGO_x, RIGO_y, RIGO_z)

    LIGO_x = db.Column(db.Float())
    LIGO_y = db.Column(db.Float())
    LIGO_z = db.Column(db.Float())
    LIGO = composite(FiducialPosition, LIGO_x, LIGO_y, LIGO_z)

    RVOH_x = db.Column(db.Float())
    RVOH_y = db.Column(db.Float())
    RVOH_z = db.Column(db.Float())
    RVOH = composite(FiducialPosition, RVOH_x, RVOH_y, RVOH_z)

    LVOH_x = db.Column(db.Float())
    LVOH_y = db.Column(db.Float())
    LVOH_z = db.Column(db.Float())
    LVOH = composite(FiducialPosition, LVOH_x, LVOH_y, LVOH_z)

    ROSF_x = db.Column(db.Float())
    ROSF_y = db.Column(db.Float())
    ROSF_z = db.Column(db.Float())
    ROSF = composite(FiducialPosition, ROSF_x, ROSF_y, ROSF_z)

    LOSF_x = db.Column(db.Float())
    LOSF_y = db.Column(db.Float())
    LOSF_z = db.Column(db.Float())
    LOSF = composite(FiducialPosition, LOSF_x, LOSF_y, LOSF_z)

    def __init__(self):
        self.no_of_fiducials = 0

    def __repr__(self):
        return "<id {}>".format(self.id)

    # def serialize(self):
    #     """Produce a dict of each column."""
    #     serialized = {}
    #     for base in fiducial_names:
    #         exec(
    #             "serialized[%s] = self.%s.__composite_values__()"
    #             % (base, base)
    #         )
    #     return serialized

    def add_fiducial(self, desc, points):  
        for d, p in zip(desc, points):
            setattr(self, d, float(p))
        setattr(self, desc[0][:-2], FiducialPosition(getattr(self, desc[0]),
                                                     getattr(self, desc[1]), 
                                                     getattr(self, desc[2])))
        self.no_of_fiducials += 1

    def validate(self):
        """Validate that the class represents a valid AFIDs set.

        Returns
        -------
        bool
            True if the Afids set is valid.
        """
        valid = self.no_of_fiducials == 32
        for label, name in EXPECTED_MAP.items():
            try:
                valid = valid and math.isfinite(getattr(self,f'{name[-1]}_x'))
                valid = valid and math.isfinite(getattr(self,f'{name[-1]}_y'))
                valid = valid and math.isfinite(getattr(self,f'{name[-1]}_z'))
            except ValueError:
                valid = False
            except KeyError:
                valid = False
        return valid

class InvalidFileError(Exception):
    """Exception raised when a file to be parsed is invalid.

    Attributes:
        message -- explanation of why the file is invalid
    """

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


def _skip_first(seq, num):
    """ Internal function to skip rows from beginning """
    for i, item in enumerate(seq):
        if i >= num:
            yield item


def parse_fcsv_field(row, key, label=None, parsed_coord=None):
    """Parse one field from an fcsv file."""
    try:
        if not key == "z" and parsed_coord in ["0", "RAS"]:
            value = str(-float(row[key]))
        else:
            value = row[key]

        if value is None:
            if label:
                raise InvalidFileError(f"Row {label} has no value {key}")
            raise InvalidFileError(f"Row has no value {key}")
        return value
    except KeyError as no_key:
        if label:
            raise InvalidFileError(
                f"Row {label} has no value {key}"
            ) from no_key
        raise InvalidFileError(f"Row has no value {key}") from no_key


def parse_fcsv_float(value, field, label):
    """Parse a string value that should be a real float."""
    parsed_value = None
    try:
        parsed_value = float(value)
    except ValueError as unparsable:
        raise InvalidFileError(
            f"{field} in row {label} is not a real number"
        ) from unparsable

    if not math.isfinite(parsed_value):
        raise InvalidFileError(f"{field} in row {label} is not finite")


def csv_to_afids(in_csv):
    """Parse .fcsv / .csv files and write to AFIDs object

    Parameters
    ----------
    in_csv : str
        The fcsv to be parsed.

    Returns
    -------
    Afids
        Valid Afids object with coordinates derived from the fcsv.
    """

    # Assume versions always in form x.y
    parsed_version = None
    try:
        parsed_version = re.findall(r"\d+\.\d+", in_csv.splitlines()[0])[0]
        parsed_coord = re.split(r"\s", in_csv.splitlines()[1])[-1]
    except IndexError as no_header:
        raise InvalidFileError(
            "Missing or invalid header in fiducial file"
        ) from no_header

    if parse_version(parsed_version) < parse_version("4.6"):
        raise InvalidFileError(
            f"Markups fiducial file version {parsed_version} too low"
        )

    # Some fields irrelevant, but know they should be there
    fields = (
        "id",
        "x",
        "y",
        "z",
        "ow",
        "ox",
        "oy",
        "oz",
        "vis",
        "sel",
        "lock",
        "label",
        "desc",
        "associatedNodeID",
    )

    in_csv = io.StringIO(in_csv)
    csv_reader = csv.DictReader(in_csv, fields)

    # Read csv file and dump to AFIDs object
    afids = FiducialSet()

    expected_label = 1
    for row in _skip_first(csv_reader, 3):
        if expected_label > 32:
            raise InvalidFileError("Too many rows")

        row_label = parse_fcsv_field(row, "label")

        # Check if label is numerical
        if not row_label.isdigit():
            raise InvalidFileError(
                f"Row label {row_label} is invalid for fiducial {expected_label}"
            )

        expected_label += 1
        row_desc = parse_fcsv_field(row, "desc", row_label)

        # Check to see if row description is not empty
        if not isinstance(row_desc, str):
            raise InvalidFileError(
                f"Row description {row_desc} is invalid for {row_label}"
            )

        if not any(
            x.lower() == row_desc.lower() for x in EXPECTED_MAP[row_label]
        ):
            raise InvalidFileError(
                f"Row label {row_label} does not match "
                f"row description {row_desc}"
            )

        # Ensure the full FID name is used
        row_desc = EXPECTED_MAP[row_label][-1]

        row_x = parse_fcsv_field(row, "x", row_label, parsed_coord)
        parse_fcsv_float(row_x, "x", row_label)
        row_y = parse_fcsv_field(row, "y", row_label, parsed_coord)
        parse_fcsv_float(row_y, "y", row_label)
        row_z = parse_fcsv_field(row, "z", row_label, parsed_coord)
        parse_fcsv_float(row_z, "z", row_label)

        num_columns = len(row) - len(
            [value for value in row.values() if value is None]
        )
        if num_columns != 14:
            raise InvalidFileError(
                f"Incorrect number of columns ({num_columns}) "
                f"in row {row_label}"
            )

        row_descriptors = [f"{row_desc}_x", f"{row_desc}_y", f"{row_desc}_z"]
        afids.add_fiducial(row_descriptors, [row_x, row_y, row_z])

    # Check for too few rows
    if afids.no_of_fiducials < 32:
        raise InvalidFileError("Too few rows")

    return afids


def parse_json_key(in_json, key, label=None, parsed_coord=None):
    """Parse a key from a JSON file."""
    try:
        in_json = in_json["markups"][0]["controlPoints"]

        if key == "position" and (parsed_coord in ["0", "RAS"]):
            value = in_json[label][key]
            value = [-value[0], -value[1], value[2]]

        else:
            value = in_json[label][key]

        if value is None:
            if label:
                raise InvalidFileError(f"Fiducial {label} has no value {key}")
            raise InvalidFileError(f"Fiducial has no value {key}")
        return value
    except KeyError as no_key:
        if label:
            raise InvalidFileError(
                f"Fiducial {label} has no value {key}"
            ) from no_key
        raise InvalidFileError(f"Fiducial has no value {key}") from no_key


def json_to_afids(in_json):
    """Parse .json files and write to AFIDs object

    Parameters
    ----------
    in_json : str
        AFIDs JSON to be parsed

    Returns
    -------
    Afids
        Valid Afids object with coordinates from the JSON.
    """

    try:
        in_json = json.loads(in_json)
    except json.JSONDecodeError as err:
        raise InvalidFileError(
            f"Invalid JSON file: {err.msg} at line "
            f"{err.lineno}, column {err.colno}."
        ) from err

    # Start by checking file is of correct type
    if not in_json["markups"][0]["type"] == "Fiducial":
        raise InvalidFileError("Not fiducial markup file")

    # Read json file and dump to AFIDs object
    afids = FiducialSet()
    fid_coord = in_json["markups"][0]["coordinateSystem"]

    # Check for too many or too few fiducials
    num_fids = len(in_json["markups"][0]["controlPoints"])
    if num_fids > 32:
        raise InvalidFileError("Too many fiducials")
    if num_fids < 32:
        raise InvalidFileError("Too few fiducials")

    for fid in range(0, num_fids):
        fid_label = parse_json_key(in_json, "label", fid, fid_coord)
        if str(fid_label) not in EXPECTED_MAP:
            raise InvalidFileError(f"Fiducial label {fid_label} invalid.")
        fid_desc = parse_json_key(in_json, "description", fid, fid_coord)
        if not any(
            x.lower() == fid_desc.lower() for x in EXPECTED_MAP[str(fid_label)]
        ):
            raise InvalidFileError(
                f"Fiducial label {fid_label} does not match "
                f"fiducial description {fid_desc}"
            )

        # Ensure full FID name is used
        fid_desc = EXPECTED_MAP[fid_label][-1]
        fid_position = parse_json_key(in_json, "position", fid, fid_coord)

        if len(fid_position) != 3:
            raise InvalidFileError(
                f"Fiducial {fid_desc} does not have three coordinates"
            )

        for coord_label, coord in zip(["x", "y", "z"], fid_position):
            if (not isinstance(coord, (float, int))) or isinstance(
                coord, bool
            ):
                raise InvalidFileError(
                    f"{coord_label} ({coord}) in fiducial {fid_label} is not "
                    "a real number"
                )

        fid_descriptors = [f"{fid_desc}_x", f"{fid_desc}_y", f"{fid_desc}_z"]
        afids.add_fiducial(fid_descriptors, fid_position)

    return afids
