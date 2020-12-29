"""Handle parsing files to internal AFIDs representation."""

import csv
import math
import re

from pkg_resources import parse_version

from afids import Afids

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

    return parsed_value


def csv_to_afids(in_csv):
    """ Parse .fcsv / .csv files and write to AFIDs object """

    # Assume versions always in form x.y
    parsed_version = None
    try:
        parsed_version = re.findall(r"\d+\.\d+", in_csv.readline())[0]
        parsed_coord = re.split(r"\s", in_csv.readline())[-2]
    except IndexError as no_header:
        raise InvalidFileError(
            "Missing or invalid header in fiducial file"
        ) from no_header

    if parse_version(parsed_version) < parse_version("4.6"):
        raise InvalidFileError(
            f"Markups fiducial file version {parsed_version} too low"
        )

    in_csv.seek(0, 0)

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

    csv_reader = csv.DictReader(in_csv, fields)

    # Read csv file and dump to AFIDs object
    afids = Afids()

    expected_label = 1
    for row in _skip_first(csv_reader, 3):
        if expected_label > 32:
            raise InvalidFileError("Too many rows")

        row_label = parse_fcsv_field(row, "label")

        expected_label += 1
        row_desc = parse_fcsv_field(row, "desc", row_label)
        if not any(
            x.lower() == row_desc.lower() for x in EXPECTED_MAP[row_label]
        ):
            raise InvalidFileError(
                f"Row label {row_label} does not match "
                f"row description {row_desc}"
            )

        # Ensure the full FID name is used
        row_desc = EXPECTED_MAP[row_label][0]

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

        afids.add_fiducial(row_label, row_desc, [row_x, row_y, row_z])

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
    """ Parse .json files and write to AFIDs object """
    # Start by checking file is of correct type
    if not in_json["markups"][0]["type"] == "Fiducial":
        raise InvalidFileError("Not fiducial markup file")

    # Read json file and dump to AFIDs object
    afids = Afids()
    fid_coord = in_json["markups"][0]["coordinateSystem"]

    # Check for too many or too few fiducials
    num_fids = len(in_json["markups"][0]["controlPoints"])
    if num_fids > 32:
        raise InvalidFileError("Too many fiducials")
    elif num_fids < 32:
        raise InvalidFileError("Too few fiducials")

    for fid in range(0, num_fids):
        fid_label = parse_json_key(in_json, "label", fid, fid_coord)
        fid_desc = parse_json_key(in_json, "description", fid, fid_coord)
        if not any(
            x.lower() == fid_desc.lower() for x in EXPECTED_MAP[str(fid + 1)]
        ):
            raise InvalidFileError(
                f"Fiducial label {fid_label} does not match "
                f"fiducial description {fid_desc}"
            )

        # Ensure full FID name is used
        fid_desc = EXPECTED_MAP[fid_label][0]
        fid_position = parse_json_key(in_json, "position", fid, fid_coord)

        # NEED TO IMPLEMENT CHECK FOR MISSING JSON VALUES
        afids.add_fiducial(fid_label, fid_desc, fid_position)

    return afids
