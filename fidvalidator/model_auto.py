import wtforms as wtf
import csv, io, json

class Average(wtf.Form):
    filename = wtf.FileField(validators=[wtf.validators.InputRequired()])


def _skip_first(seq, n):
    """ Internal function to skip rows from beginning """
    for i, item in enumerate(seq):
        if i >= n:
            yield item


def csv_to_json(in_csv):
    """ Parse .fscv / .csv files and write to json object """
    # Irrelevant fields set to None
    fields = (None, 'x', 'y', 'z', None, None, None, None, None,
              None, None, 'label', 'desc', None)

    # Read CSV
    csv_reader = csv.DictReader(io.StringIO(in_csv.read().decode('utf-8')),
                                fields)

    # Read csv file and dump to json object
    json_data = {}
    for row in _skip_first(csv_reader, 3):
        json_data[row['label']] = {'desc': row['desc'], 'x': row['x'],
                                   'y': row['y'], 'z': row['z']}

    json_data = json.dumps(json_data, sort_keys=False, indent=4,
                           separators=(',', ': '))

    return json_data
