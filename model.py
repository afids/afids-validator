import csv, json, math
import re
from afids import Afids
from pkg_resources import parse_version

EXPECTED_LABELS = [str(x + 1) for x in range(32)]
EXPECTED_DESCS = [
        ['AC'],
        ['PC'],
        ['infracollicular sulcus', 'ICS'],
        ['PMJ'],
        ['superior interpeduncular fossa', 'SIPF'],
        ['R superior LMS', 'RSLMS'],
        ['L superior LMS', 'LSLMS'],
        ['R inferior LMS', 'RILMS'],
        ['L inferior LMS', 'LILMS'],
        ['Culmen', 'CUL'],
        ['Intermammillary sulcus', 'IMS'],
        ['R MB', 'RMB'],
        ['L MB', 'LMB'],
        ['pineal gland', 'PG'],
        ['R LV at AC', 'RLVAC'],
        ['L LV at AC', 'LLVAC'],
        ['R LV at PC', 'RLVPC'],
        ['L LV at PC', 'LLVPC'],
        ['Genu of CC', 'GENU'],
        ['Splenium of CC', 'SPLE'],
        ['R AL temporal horn', 'RALTH'],
        ['L AL temporal horn', 'LALTH'],
        ['R superior AM temporal horn', 'RSAMTH'],
        ['L superior AM temporal horn', 'LSAMTH'],
        ['R inferior AM temporal horn', 'RIAMTH'],
        ['L inferior AM temporal horn', 'RIAMTH'],
        ['R indusium griseum origin', 'RIGO'],
        ['L indusium griseum origin', 'LIGO'],
        ['R ventral occipital horn', 'RVOH'],
        ['L ventral occipital horn', 'LVOH'],
        ['R olfactory sulcal fundus', 'ROSF'],
        ['L olfactory sulcal fundus', 'LOSF']]

EXPECTED_MAP = dict(zip(EXPECTED_LABELS, EXPECTED_DESCS))

class InvalidFileError(Exception):
    """Exception raised when a file to be parsed is invalid.

    Attributes:
        message -- explanation of why the file is invalid
    """

    def __init__(self, message):
        self.message = message

def _skip_first(seq, n):
    """ Internal function to skip rows from beginning """
    for i, item in enumerate(seq):
        if i >= n:
            yield item

def parse_fcsv_field(row, key, label=None, parsed_coord=None):
    try:
        if parsed_coord == 0 or parsed_coord == "RAS":
            value = str(-float(row[key]))
        else:
            value = row[key]

        if value is None:
            if label:
                raise InvalidFileError('Row {label} has no value {key}'
                    .format(label=label, key=key))
            else:
                raise InvalidFileError('Row has no value {key}'
                    .format(key=key))
        return value
    except KeyError:
        if label:
            raise InvalidFileError('Row {label} has no value {key}'
                    .format(label=label, key=key))
        else:
            raise InvalidFileError('Row has no value {key}'
                .format(key=key))

def parse_fcsv_float(value, field, label):
    parsed_value = None
    try:
        parsed_value = float(value)
    except ValueError:
        raise InvalidFileError('{field} in row {label} is not a real number'
                .format(field=field, label=label))

    if not math.isfinite(parsed_value):
        raise InvalidFileError('{field} in row {label} is not finite'
                .format(field=field, label=label))

    return parsed_value

def csv_to_afids(in_csv):
    """ Parse .fcsv / .csv files and write to AFIDs object """
    # Start by checking file version
    version_line = in_csv.readline()
    coord_line = in_csv.readline()
    
    # Assume versions always in form x.y
    parsed_version = None
    try:
        parsed_version = re.findall("\d+\.\d+", version_line)[0]
        parsed_coord = re.split("\s", coord_line)[-2]
    except IndexError:
        raise InvalidFileError("Missing or invalid header in fiducial file")
        
    if parse_version(parsed_version) < parse_version("4.6"):
        raise InvalidFileError("Markups fiducial file version {parsed_version} too low"
                               .format(parsed_version=parsed_version))
        
    in_csv.seek(0, 0)
    
    # Some fields irrelevant, but know they should be there
    fields = ('id', 'x', 'y', 'z', 'ow', 'ox', 'oy', 'oz', 'vis', 'sel', 'lock', 'label', 'desc', 'associatedNodeID')
    
    csv_reader = csv.DictReader(in_csv, fields)
    
    # Read csv file and dump to AFIDs object
    afids = Afids()
     
    expected_label = 1
    for row in _skip_first(csv_reader, 3):
        if expected_label > 32:
            raise InvalidFileError("Too many rows")
            
        row_label = parse_fcsv_field(row, 'label')

        expected_label += 1
        row_desc = parse_fcsv_field(row, 'desc', row_label)
        if not any(x.lower() == row_desc.lower() for x in EXPECTED_MAP[row_label]):
            raise InvalidFileError('Row label {row_label} does not '
                'match row description {row_desc}'
                .format(row_label=row_label, row_desc=row_desc)) 
                
        # Ensure the full FID name is used
        row_desc = EXPECTED_MAP[row_label][0]

        row_x = parse_fcsv_field(row, 'x', row_label, parsed_coord)
        parse_fcsv_float(row_x, 'x', row_label)
        row_y = parse_fcsv_field(row, 'y', row_label, parsed_coord)
        parse_fcsv_float(row_y, 'y', row_label)
        row_z = parse_fcsv_field(row, 'z', row_label, parsed_coord)
        parse_fcsv_float(row_z, 'z', row_label)

        missing_fields = 0
        for value in row.values():
            if value is None:
                # The fcsv is missing values
                missing_fields += 1

        num_columns = len(row) - missing_fields
        if num_columns != 14:
            raise InvalidFileError('Incorrect number of columns '
                    '({num_columns}) in row {row_label}'
                    .format(num_columns=num_columns, row_label=row_label))
        
        row_positions = [row_x, row_y, row_z]
        
        afids.add_fiducial(row_label, row_desc, row_positions)
    
    # Check for too few rows
    if len(afids.fiducials) < 32:
        raise InvalidFileError('Too few rows')

    return afids
        
def parse_json_key(in_json, key, label=None, parsed_coord=None):
    try:
        in_json = in_json["markups"][0]["controlPoints"] 
        
        if key == "position" and (parsed_coord == 0 or parsed_coord == "RAS"):
            value = in_json[label][key]
            value = [-value[0], -value[1], value[2]]
            
        else:
            value = in_json[label][key]

        if value is None:
            if label:
                raise InvalidFileError('Fiducial {label} has no value {key}'
                    .format(label=label, key=key))
            else:
                raise InvalidFileError('Fiducial has no value {key}'
                    .format(key=key))
        return value
    except KeyError:
        if label:
            raise InvalidFileError('Fiducial {label} has no value {key}'
                    .format(label=label, key=key))
        else:
            raise InvalidFileError('Fiducial has no value {key}'
                .format(key=key))

def json_to_afids(in_json):
    """ Parse .json files and write to AFIDs object """
    # Start by checking file is of correct type
    if not in_json["markups"][0]["type"] == "Fiducial":
        raise InvalidFileError("Not fiducial markup file")
    
    # Read json file and dump to AFIDs object
    afids = Afids()
    
    expected_label = 1
    for fid in range(len(in_json["markups"][0]["controlPoints"])):
        if fid > 32:
            raise InvalidFileError("Too many rows")
            
        fid_label = parse_json_key(in_json, "label", fid)
        
        fid_desc = parse_json_key(in_json, "description", fid)
        if not any(x.lower() == fid_desc.lower() for x in EXPECTED_MAP[row_label]):
            raise InvalidFileError("Fiducial label {fid_label} does not "
                "match Fiducial description {fid_desc}"
                .format(fid_label=fid_label, fid_desc=fid_desc))
                                   
        # Ensure full FID name is used
        fid_desc = EXPECTED_MAP[fid_label][0]
        fid_position = parse_json_key(in_json, "position", fid)

        # NEED TO IMPLEMENT CHECK FOR MISSING JSON VALUES      
        afids.add_fiducial(fid_label, fid_desc, fid_position)
    
    # Check for too few rows
    if len(afids.fiducials) < 32:
        raise InvalidFileError('Too few rows')

    return afids