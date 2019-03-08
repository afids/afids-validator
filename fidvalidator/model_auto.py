import wtforms as wtf
import csv, json, math

EXPECTED_LABELS = [str(x + 1) for x in range(32)]
EXPECTED_DESCS = [
        'AC',
        'PC',
        'infracollicular sulcus',
        'PMJ',
        'superior interpeduncular fossa',
        'R superior LMS',
        'L superior LMS',
        'R inferior LMS',
        'L inferior LMS',
        'culmen',
        'intermammillary sulcus',
        'R MB',
        'L MB',
        'pineal gland',
        'R LV at AC',
        'L LV at AC',
        'R LV at PC',
        'L LV at PC',
        'genu of CC',
        'splenium',
        'R AL temporal horn',
        'L AL temporal horn',
        'R superior AM temporal horn',
        'L superior AM temporal horn',
        'R inferior AM temporal horn',
        'L inferior AM temporal horn',
        'R indusium griseum origin',
        'L indusium griseum origin',
        'R ventral occipital horn',
        'L ventral occipital horn',
        'R olfactory sulcal fundus',
        'L olfactory sulcal fundus']

EXPECTED_MAP = dict(zip(EXPECTED_LABELS, EXPECTED_DESCS))

class Average(wtf.Form):
    filename = wtf.FileField(validators=[wtf.validators.InputRequired()])

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

def parse_fcsv_field(row, key, label=None):
    try:
        return row[key]
    except KeyError:
        if label:
            return InvalidFcsvError('Row {label} has no {key} value')
        else:
            return InvalidFcsvError('Row has no {key} value')

def parse_fcsv_float(value, field, label):
    parsed_value = None
    try:
        parsed_value = float(value)
    except ValueError:
        raise InvalidFcsvError('{field} in row {label} is not a real number')

    if not math.isfinite(parsed_value):
        raise InvalidFcsvError('{field} in row {label} is not finite')

    return parsed_value


def csv_to_json(in_csv):
    """ Parse .fscv / .csv files and write to json object """
    
    # Read CSV
    json_data = {}

    # Start by checking the file version
    version_line = in_csv.readline()

    # Assuming versions are always in the form x.y
    parsed_version = None
    try:
        parsed_version = float(version_line[-4:])
    except ValueError:
        raise InvalidFcsvError('Invalid Markups fiducial file version')

    if parsed_version < 4.6:
        raise InvalidFcsvError('Markups fiducial file version ' +
                '{parsed_version} too low')

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

        if row_label != str(expected_label):
            raise InvalidFcsvError('Row label {row_label} out of order')
        expected_label += 1

        row_desc = parse_fcsv_field(row, 'desc', row_label)

        if EXPECTED_MAP[row_label] != row_desc:
            raise InvalidFcsvError('Row label {row_label} does not ' +
                'match row description {row_desc}')

        row_x = parse_fcsv_field(row, 'x', row_label)
        row_x_float = parse_fcsv_float(row_x, 'x', row_label)
        
        row_y = parse_fcsv_field(row, 'y', row_label)
        row_y_float = parse_fcsv_float(row_y, 'y', row_label)
        
        row_z = parse_fcsv_field(row, 'z', row_label)
        row_z_float = parse_fcsv_float(row_z, 'z', row_label)

        missing_fields = 0
        for value in row.values():
            if value is None:
                # The fcsv is missing values
                missing_fields += 1

        num_columns = len(row) - missing_fields
        if num_columns != 14:
            raise InvalidFcsvError('Incorrect number of columns '
                    '({num_columns}) in row {row_label}')

        json_data[row_label] = {'desc': row_desc, 'x': row_x, 'y': row_y,
                                'z': row_z}

    if len(json_data) < 32:
        # Incorrect number of rows
        raise InvalidFcsvError('Too few rows')

    json_data = json.dumps(json_data, sort_keys=False, indent=4,
                           separators=(',', ': '))

    return json_data

