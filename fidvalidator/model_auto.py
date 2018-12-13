import wtforms as wtf
import csv, json

class Average(wtf.Form):
    filename = wtf.FileField(validators=[wtf.validators.InputRequired()])


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
        json_data[row['label']] = {'desc': row['desc'], 'x': row['x'],
                                   'y': row['y'], 'z': row['z']}
    csv_file.close()

    json_data = json.dumps(json_data, sort_keys=False, indent=4,
                           separators=(',', ': '))

    return json_data
