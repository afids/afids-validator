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
    csvFile = open(in_file, 'r')
    csvReader = csv.DictReader(csvFile, fields)

    # Read csv file and dump to json object
    jsonData = {}
    for row in _skip_first(csvReader, 3):
        jsonData[row['desc']] = {'label': row['label'], 'x': row['x'],
                                 'y': row['y'], 'z': row['z']}
    csvFile.close()

    jsonData = json.dumps(jsonData, sort_keys=False, indent=4,
                          separators=(',', ': '))

    return jsonData
