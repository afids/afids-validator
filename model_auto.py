import wtforms as wtf
import csv, json, math
import re
import afids
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

class Average(wtf.Form):
    filename = wtf.FileField(validators=[wtf.validators.InputRequired()])
    submit = wtf.SubmitField(label='Submit')

class InvalidFcsvError(Exception):
    """Exception raised when a csv to be parsed is invalid.

    Attributes:
        message -- explanation of why the fcsv is invalid
    """

    def __init__(self, message):
        self.message = message

def _skip_first(seq, n):
    """ Internal function to skip rows from beginning """
    for i, item in enumerate(seq):
        if i >= n:
            yield item

def parse_fcsv_field(row, key, label=None, parsed_version=None):
    try:
        if parsed_version is None or parse_version(parsed_version) >= parse_version('4.11'):
            value = row[key]
        elif key == 'x' or key == 'y':
            value = str(-float(row[key]))
        else:
            value = row[key]

        if value is None:
            if label:
                raise InvalidFcsvError('Row {label} has no value {key}'
                    .format(label=label, key=key))
            else:
                raise InvalidFcsvError('Row has no value {key}'
                    .format(key=key))
        return value
    except KeyError:
        if label:
            raise InvalidFcsvError('Row {label} has no value {key}'
                    .format(label=label, key=key))
        else:
            raise InvalidFcsvError('Row has no value {key}'
                .format(key=key))

def parse_fcsv_float(value, field, label):
    parsed_value = None
    try:
        parsed_value = float(value)
    except ValueError:
        raise InvalidFcsvError('{field} in row {label} is not a real number'
                .format(field=field, label=label))

    if not math.isfinite(parsed_value):
        raise InvalidFcsvError('{field} in row {label} is not finite'
                .format(field=field, label=label))

    return parsed_value

def csv_to_afids(in_csv):
    """ Parse .fcsv / .csv files and write to AFIDs object """
    # Start by checking file version
    version_line = in_csv.readline()
    
    # Assume versions always in form x.y
    parsed_version = None
    try:
        parsed_version = re.findall("\d+\.\d+", version_line)[0]
    except IndexError:
        raise InvalidFcsvError("Missing / invalid header in fiducial file")
        
    if parse_version(parsed_version) < parse_version("4.6"):
        raise InvalidFcsvError("Markups fiducial file version {parsed_version} too low"
                               .format(parsed_version=parsed_version))
        
    in_csv.seek(0, 0)
    
    # Some fields irrelevant, but know they should be there
    fields = ('id', 'x', 'y', 'z', 'ow', 'ox', 'oy', 'oz', 'vis', 'sel', 'lock', 'label', 'desc', 'associatedNodeID')
    
    csv_reader = csv.DictReader(in_csv, fields)
    
    # Read csv file and dump to AFIDs object
    afids = Afids(coordinate_system="LPS")
    
    expected_label = 1
    for row in _skip_first(csv_reader, 3):
        if expected_label > 32:
            raise InvalidFcsvError("Too many rows")
            
        row_label = parse_fcsv_field(row, 'label')

        expected_label += 1
        row_desc = parse_fcsv_field(row, 'desc', row_label)
        if not any(x.lower() == row_desc.lower() for x in EXPECTED_MAP[row_label]):
            raise InvalidFcsvError('Row label {row_label} does not '
                .format(row_label=row_label) +
                'match row description {row_desc}'
                .format(row_desc=row_desc))

        # Ensure the full FID name is used
        row_desc = EXPECTED_MAP[row_label][0]

        row_x = parse_fcsv_field(row, 'x', row_label, parsed_version)
        parse_fcsv_float(row_x, 'x', row_label)
        row_y = parse_fcsv_field(row, 'y', row_label, parsed_version)
        parse_fcsv_float(row_y, 'y', row_label)
        row_z = parse_fcsv_field(row, 'z', row_label, parsed_version)
        parse_fcsv_float(row_z, 'z', row_label)

        missing_fields = 0
        for value in row.values():
            if value is None:
                # The fcsv is missing values
                missing_fields += 1

        num_columns = len(row) - missing_fields
        if num_columns != 14:
            raise InvalidFcsvError('Incorrect number of columns '
                    '({num_columns}) in row {row_label}'
                    .format(num_columns=num_columns, row_label=row_label))
        
        row_positions = [row_x, row_y, row_z]
        
        afids.add_fiducial(row_label, row_desc, row_positions)
    
    # Check for too few rows
    if len(afids.fiducials) < 32:
        raise InvalidFcsvError('Too few rows')

    return afids

def csv_to_json(in_csv):
    """ Parse .fscv / .csv files and write to json object """

    # Read CSV
    json_data = {}

    # Start by checking the file version
    version_line = in_csv.readline()

    # Assuming versions are always in the form x.y
    parsed_version = None
    try:
        parsed_version = re.findall("\d+\.\d+", version_line)[0]
    except IndexError:
        raise InvalidFcsvError('Missing or invalid header in fiducial file')

    if parse_version(parsed_version) < parse_version('4.6'):
        raise InvalidFcsvError('Markups fiducial file version ' +
                '{parsed_version} too low'
                .format(parsed_version=parsed_version))

    in_csv.seek(0, 0)

    # Some fields are irrelevant, but we know they should be there
    fields = ('id', 'x', 'y', 'z', 'ow', 'ox', 'oy', 'oz', 'vis',
              'sel', 'lock', 'label', 'desc', 'associatedNodeID')

    csv_reader = csv.DictReader(in_csv, fields)

    # Read csv file and dump to json object
    expected_label = 1
    for row in _skip_first(csv_reader, 3):
        if expected_label > 32:
            raise InvalidFcsvError('Too many rows')

        row_label = parse_fcsv_field(row, 'label')

        expected_label += 1
        row_desc = parse_fcsv_field(row, 'desc', row_label)
        if not any(x.lower() == row_desc.lower() for x in EXPECTED_MAP[row_label]):
            raise InvalidFcsvError('Row label {row_label} does not '
                .format(row_label=row_label) +
                'match row description {row_desc}'
                .format(row_desc=row_desc))

        # Ensure the full FID name is used
        row_desc = EXPECTED_MAP[row_label][0]

        row_x = parse_fcsv_field(row, 'x', row_label, parsed_version)
        parse_fcsv_float(row_x, 'x', row_label)
        row_y = parse_fcsv_field(row, 'y', row_label, parsed_version)
        parse_fcsv_float(row_y, 'y', row_label)
        row_z = parse_fcsv_field(row, 'z', row_label, parsed_version)
        parse_fcsv_float(row_z, 'z', row_label)

        missing_fields = 0
        for value in row.values():
            if value is None:
                # The fcsv is missing values
                missing_fields += 1

        num_columns = len(row) - missing_fields
        if num_columns != 14:
            raise InvalidFcsvError('Incorrect number of columns '
                    '({num_columns}) in row {row_label}'
                    .format(num_columns=num_columns, row_label=row_label))

        json_data[row_label] = {'desc': row_desc, 'x': row_x, 'y': row_y,
                                'z': row_z}

    if len(json_data) < 32:
        # Incorrect number of rows
        raise InvalidFcsvError('Too few rows')

    # Sort dict based on fid number
    lst = list(json_data.items())
    lst.sort(key=lambda k: int(k[0]))
    json_data = dict(lst)

    json_data = json.dumps(json_data, sort_keys=False, indent=4,
                           separators=(',', ': '))

    return json_data
