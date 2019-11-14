from flask import Flask, render_template, request
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os

import io

import random

from flask import Flask, Response, render_template

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from matplotlib.figure import Figure

import matplotlib

import matplotlib.pyplot as plt

import numpy as np

app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Fiducial_set(db.Model):
    __tablename__ = 'fid_db'

    id = db.Column(db.Integer, primary_key=True)
    AC_x = db.Column(db.Float())
    AC_y = db.Column(db.Float())
    AC_z = db.Column(db.Float())
    PC_x = db.Column(db.Float())
    PC_y = db.Column(db.Float())
    PC_z = db.Column(db.Float())

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        return {
            'id': self.id, 
            'AC_x': self.AC_x,
            'AC_y': self.AC_y,
            'AC_z': self.AC_z,
            'PC_x': self.PC_x,
            'PC_y': self.PC_y,
            'PC_z': self.PC_z,

        }

from model_auto import Average, csv_to_json, InvalidFcsvError
from compute import calc
from model import InputForm
import io
import json

# Relative path of directory for uploaded files
UPLOAD_DIR = 'uploads/'
AFIDS_DIR = 'afids-examples/'

app.config['UPLOAD_FOLDER'] = UPLOAD_DIR
app.secret_key = 'MySecretKey'

if not os.path.isdir(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

# Allowed file types for file upload
ALLOWED_EXTENSIONS = set(['fcsv', 'csv'])
def allowed_file(filename):
    """Does filename have the right extension?"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Path to the web application
@app.route('/', methods=['GET', 'POST'])
def index2():
    form = Average(request.form)

    msg = ''
    result = ''
    index = []
    distances = []
    labels = []
    template_data_j = None

    if request.method == 'POST':
        fid_template = request.form['fid_template']
        msg = fid_template + ' selected'

        if request.files:
            upload = request.files[form.filename.name]
            template_file_path = os.path.join(os.path.join(AFIDS_DIR,
                                                'sub-' + str(fid_template)),
                                                'sub-' + str(fid_template) +
                                                '_afids.fcsv')
            template_file = open(template_file_path, 'r')

            if upload and allowed_file(upload.filename):
                try:
                    user_data = csv_to_json(io.StringIO(upload.stream.read().decode('utf-8')))
                    user_data_j = json.loads(user_data)
                    template_data = csv_to_json(template_file)
                    template_data_j = json.loads(template_data)
                    fiducial_set=Fiducial_set(
                    	AC_x = user_data_j['1']['x'],
                    	AC_y = user_data_j['1']['y'],
                    	AC_z = user_data_j['1']['z'],
                    	PC_x = user_data_j['2']['x'],
                    	PC_y = user_data_j['2']['y'],
                    	PC_z = user_data_j['2']['z'],
                    )
                    db.session.add(fiducial_set)
                    db.session.commit()
                    print("fiducial set added")

                    for element in template_data_j:
                        index.append(int(element)-1)

                        coordinate_name = template_data_j[element]['desc']

                        template_x = float(template_data_j[element]['x'])
                        template_y = float(template_data_j[element]['y'])
                        template_z = float(template_data_j[element]['z'])

                        user_x = float(user_data_j[element]['x'])
                        user_y = float(user_data_j[element]['y'])
                        user_z = float(user_data_j[element]['z'])

                        diff = calc(template_x, template_y, template_z, user_x, user_y, user_z)
                        diff = float("{0:.5f}".format(diff))

                        labels.append(coordinate_name)
                        distances.append(diff)

                        # print(labels)
                        # print(distances)
                        # print(element)

                    result = 'valid file'

                except InvalidFcsvError as err:
                    result = 'invalid file: {err_msg}'.format(
                        err_msg=err.message)

            else:
                result = "invalid file: extension not allowed"

        else:
            result = None

    dir_contents = os.listdir(AFIDS_DIR)
    fid_templates = [' ']
    for d in dir_contents:
        if 'sub' in d:
            fid_templates.append(d[4:])

    result = '<br>'.join([result, msg])

    return render_template("view.html", form=form, result=result,
        fid_templates=fid_templates, template_data_j=template_data_j,
        index=index, labels=labels, distances=distances)

@app.route("/getall")
def get_all():
    try:
        fiducial_sets=Fiducial_set.query.all()
        serialized_fset = []
        for i in range(len(fiducial_sets)):
            serialized_fset.append(fiducial_sets[i].serialize())
            print(serialized_fset[i])
        # jsonify([e.serialize() for e in fiducial_sets]), can be used instead of template

        return render_template("db.html", serialized_fset=serialized_fset)
    except Exception as e:
	    return(str(e))

labels = ['Eucllidean', 'X_error', 'Y_error', 'Z_error']

individ_values = [4.0, 3.4, 3.0, 3.5]

population_values = [4.5, 3.2, 3.4, 2.0]


x = np.arange(len(labels))  # the label locations

width = 0.35  # the width of the bars


fig, ax = plt.subplots()

rects1 = ax.bar(x - width/2, individ_values, width, label='Your errors')

rects2 = ax.bar(x + width/2, population_values, width, label='Average errors')

@app.route('/plot.png')

def plot_png():

    fig = create_figure()

    output = io.BytesIO()

    FigureCanvas(fig).print_png(output)

    return Response(output.getvalue(), mimetype='image/png')


def create_figure():

    fig = Figure()

    fig, ax = plt.subplots()

    rects1 = ax.bar(x - width/2, individ_values, width, label='Your errors')

    rects2 = ax.bar(x + width/2, population_values, width, label='Average errors')

    ax.set_ylabel('mm')

    ax.set_title('Errors by category')

    ax.set_xticks(x)

    ax.set_xticklabels(labels)

    ax.legend()

    fig.tight_layout()

    return fig


@app.route('/analytics')

def chartTest():

    return render_template('view_analytics.html')

if __name__ == '__main__':
    app.run(debug=True)
