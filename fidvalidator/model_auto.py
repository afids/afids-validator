import wtforms as wtf
import csv, json

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


def csv_to_json(in_file):
    """ Parse .fscv / .csv files and write to json object """
    # Irrelevant fields set to None
    fields = (None, 'x', 'y', 'z', None, None, None, None, None,
              None, None, 'label', 'desc', None)

    # Read CSV
    csv_file = open(in_file, 'r')
    csv_reader = csv.DictReader(csv_file, fields)

    # Read csv file and dump to json object
    json_data = {}
    for row in _skip_first(csv_reader, 3):
        if len(row) != 14:
            row_label = None
            try:
                row_label = row['label']
                raise InvalidFcsvError('Incorrect number of columns in row ' +
                        f'{row_label}')
            except KeyError:
                raise InvalidFcsvError('Incorrect number of columns.')

        row_label = None
        try:
            row_label = row['label']
        except KeyError:
            raise InvalidFcsvError('Row with no label.')


        json_data[row['label']] = {'desc': row['desc'], 'x': row['x'],
                                   'y': row['y'], 'z': row['z']}
 
    csv_file.close()

    if len(json_data) != 32:
        # Incorrect number of rows
        raise InvalidFcsvError('Incorrect number of rows.')

    json_data = json.dumps(json_data, sort_keys=False, indent=4,
                           separators=(',', ': '))

    return json_data

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

def validate_afids_json(afids_json):
    """ Validate that given .fcsv data conform to AFIDs protocol """
    afids_dict = {}
    try:
        afids_dict = json.loads(afids_json)
    except json.JSONDecodeError:
        return {'valid': False, 'reason': 'Invalid JSON'}

    if not isinstance(afids_dict, dict):
        return {'valid': False, 'reason': 'Improper JSON'}

    if frozenset(afids_dict.keys()) != frozenset(EXPECTED_LABELS):
        return {'valid': False, 'reason': 'Invalid labels'}
    for expected_label in EXPECTED_LABELS:
        json_afid = afids_dict[expected_label]
        json_desc = json_afid['desc']
        
        # Is the description what it should be?
        expected_desc = EXPECTED_MAP[expected_label]
        if json_desc != expected_desc:
            return {
                    'valid': False,
                    'reason': (f'Description {json_desc} for label ' +
                        f'{expected_label} does not match expected description ' +
                        f'{expected_desc}.')}

        # Are there floats for x, y, and, z?
        if not frozenset(['x', 'y', 'z']) < frozenset(json_afid.keys()):
            return {
                    'valid': False,
                    'reason': ('At least one of x, y, or z missing in record' +
                        f'{expected_label}')}
        for direction in ['x', 'y', 'z']:
            try:
                float(json_afid[direction])
            except ValueError:
                return {
                        'valid': False,
                        'reason': (f'Direction {direction} for label' +
                            f'{expected_label} is not a real number')}

    return {'valid': True}

