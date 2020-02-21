from flask import Flask, Response, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os

import io

import random

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib
import matplotlib.pyplot as plt

import numpy as np

from flexx import flx
from pscript import RawJS
from pscript.stubs import Math, d3, window
import csv


app = Flask(__name__)

app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Fiducial_set(db.Model):
    __tablename__ = 'fid_db'

    id = db.Column(db.Integer, primary_key=True)
    coords = ["_x", "_y", "_z"]
    c = {"AC": coords,
         "PC": coords,
         "ICS": coords,
         "PMJ": coords,
         "SIPF": coords,
         "RSLMS": coords,
         "LSLMS": coords,
         "RILMS": coords,
         "LILMS": coords,
         "CUL": coords,
         "IMS": coords,
         "RMB": coords,
         "LMB": coords,
         "PG": coords,
         "RLVAC": coords,
         "LLVAC": coords,
         "RLVPC": coords,
         "LLVPC": coords,
         "GENU": coords,
         "SPLE": coords,
         "RALTH": coords,
         "LALTH": coords,
         "RSAMTH": coords,
         "LSAMTH": coords,
         "RIAMTH": coords,
         "LIAMTH": coords,
         "RIGO": coords,
         "LIGO": coords,
         "RVOH": coords,
         "LVOH": coords,
         "ROSF": coords,
         "LOSF": coords
         }

    for k,v in c.items():
        exec("%s=%s"%(k+v[0], "db.Column(db.Float())"))
        exec("%s=%s"%(k+v[1], "db.Column(db.Float())"))
        exec("%s=%s"%(k+v[2], "db.Column(db.Float())"))

    def __repr__(self):
        return '<id {}>'.format(self.id)

    def serialize(self):
        serialized = {"AC_x": self.AC_x,
                        "AC_y": self.AC_y,
                        "AC_z": self.AC_z,
                        "PC_x": self.PC_x,
                        "PC_y": self.PC_y,
                        "PC_z": self.PC_z,
                        "ICS_x": self.ICS_x,
                        "ICS_y": self.ICS_y,
                        "ICS_z": self.ICS_z,
                        "PMJ_x": self.PMJ_x,
                        "PMJ_y": self.PMJ_y,
                        "PMJ_z": self.PMJ_z,
                        "SIPF_x": self.SIPF_x,
                        "SIPF_y": self.SIPF_y,
                        "SIPF_z": self.SIPF_z,
                        "RSLMS_x": self.RSLMS_x,
                        "RSLMS_y": self.RSLMS_y,
                        "RSLMS_z": self.RSLMS_z,
                        "LSLMS_x": self.LSLMS_x,
                        "LSLMS_y": self.LSLMS_y,
                        "LSLMS_z": self.LSLMS_z,
                        "RILMS_x": self.RILMS_x,
                        "RILMS_y": self.RILMS_y,
                        "RILMS_z": self.RILMS_z,
                        "LILMS_x": self.LILMS_x,
                        "LILMS_y": self.LILMS_y,
                        "LILMS_z": self.LILMS_z,
                        "CUL_x": self.CUL_x,
                        "CUL_y": self.CUL_y,
                        "CUL_z": self.CUL_z,
                        "IMS_x": self.IMS_x,
                        "IMS_y": self.IMS_y,
                        "IMS_z": self.IMS_z,
                        "RMB_x": self.RMB_x,
                        "RMB_y": self.RMB_y,
                        "RMB_z": self.RMB_z,
                        "LMB_x": self.LMB_x,
                        "LMB_y": self.LMB_y,
                        "LMB_z": self.LMB_z,
                        "PG_x": self.PG_x,
                        "PG_y": self.PG_y,
                        "PG_z": self.PG_z,
                        "RLVAC_x": self.RLVAC_x,
                        "RLVAC_y": self.RLVAC_y,
                        "RLVAC_z": self.RLVAC_z,
                        "LLVAC_x": self.LLVAC_x,
                        "LLVAC_y": self.LLVAC_y,
                        "LLVAC_z": self.LLVAC_z,
                        "RLVPC_x": self.RLVPC_x,
                        "RLVPC_y": self.RLVPC_y,
                        "RLVPC_z": self.RLVPC_z,
                        "LLVPC_x": self.LLVPC_x,
                        "LLVPC_y": self.LLVPC_y,
                        "LLVPC_z": self.LLVPC_z,
                        "GENU_x": self.GENU_x,
                        "GENU_y": self.GENU_y,
                        "GENU_z": self.GENU_z,
                        "SPLE_x": self.SPLE_x,
                        "SPLE_y": self.SPLE_y,
                        "SPLE_z": self.SPLE_z,
                        "RALTH_x": self.RALTH_x,
                        "RALTH_y": self.RALTH_y,
                        "RALTH_z": self.RALTH_z,
                        "LALTH_x": self.LALTH_x,
                        "LALTH_y": self.LALTH_y,
                        "LALTH_z": self.LALTH_z,
                        "RSAMTH_x": self.RSAMTH_x,
                        "RSAMTH_y": self.RSAMTH_y,
                        "RSAMTH_z": self.RSAMTH_z,
                        "LSAMTH_x": self.LSAMTH_x,
                        "LSAMTH_y": self.LSAMTH_y,
                        "LSAMTH_z": self.LSAMTH_z,
                        "RIAMTH_x": self.RIAMTH_x,
                        "RIAMTH_y": self.RIAMTH_y,
                        "RIAMTH_z": self.RIAMTH_z,
                        "LIAMTH_x": self.LIAMTH_x,
                        "LIAMTH_y": self.LIAMTH_y,
                        "LIAMTH_z": self.LIAMTH_z,
                        "RIGO_x": self.RIGO_x,
                        "RIGO_y": self.RIGO_y,
                        "RIGO_z": self.RIGO_z,
                        "LIGO_x": self.LIGO_x,
                        "LIGO_y": self.LIGO_y,
                        "LIGO_z": self.LIGO_z,
                        "RVOH_x": self.RVOH_x,
                        "RVOH_y": self.RVOH_y,
                        "RVOH_z": self.RVOH_z,
                        "LVOH_x": self.LVOH_x,
                        "LVOH_y": self.LVOH_y,
                        "LVOH_z": self.LVOH_z,
                        "ROSF_x": self.ROSF_x,
                        "ROSF_y": self.ROSF_y,
                        "ROSF_z": self.ROSF_z,
                        "LOSF_x": self.LOSF_x,
                        "LOSF_y": self.LOSF_y,
                        "LOSF_z": self.LOSF_z
                        }

        return serialized

from model_auto import Average, csv_to_json, InvalidFcsvError
from compute import calc
from model import InputForm
import io
import json

# Relative path of directory for uploaded files
UPLOAD_DIR = 'uploads/'
AFIDS_HUMAN_DIR = 'afids-templates/human/'

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

# Routes to web pages / application
## Homepage
@app.route('/')
def index():
    return render_template("index.html")

## Contact
@app.route('/contact.html')
def contact():
    return render_template("contact.html")

## Login
@app.route('/login.html')
def login():
    return render_template("login.html")

# Validator
@app.route('/validator.html', methods=['GET', 'POST'])
def validator():
    form = Average(request.form)

    msg = ''
    result = ''
    index = []
    distances = []
    labels = []
    template_data_j = None
    dir_contents = os.listdir(AFIDS_HUMAN_DIR)
    fid_templates = [' ']
    for d in dir_contents:
        if 'sub' in d:
            fid_templates.append(d[4:])

    if not request.method == 'POST':
        result = '<br>'.join([result, msg])

        return render_template("validator.html", form=form, result=result,
            fid_templates=fid_templates, template_data_j=template_data_j,
            index=index, labels=labels, distances=distances)

    if not request.files:
        result = '<br>'.join([result, msg])

        return render_template("validator.html", form=form, result=result,
            fid_templates=fid_templates, template_data_j=template_data_j,
            index=index, labels=labels, distances=distances)

    upload = request.files[form.filename.name]


    if not (upload and allowed_file(upload.filename)):
        result = "invalid file: extension not allowed"
        result = '<br>'.join([result, msg])

        return render_template("validator.html", form=form, result=result,
            fid_templates=fid_templates, template_data_j=template_data_j,
            index=index, labels=labels, distances=distances)

    try:
        user_data = csv_to_json(io.StringIO(upload.stream.read().decode('utf-8')))
    except InvalidFcsvError as err:
        result = 'Invalid file: {err_msg}'.format(err_msg=err.message)
        return render_template("validator.html", form=form, result=result,
            fid_templates=fid_templates, template_data_j=template_data_j,
            index=index, labels=labels, distances=distances)

    result = 'Valid file'
    user_data_j = json.loads(user_data)

    fid_template = request.form['fid_template']

    if fid_template == ' ':
        result = "Valid file"
        result = '<br>'.join([result, msg])

        return render_template("validator.html", form=form, result=result,
            fid_templates=fid_templates, template_data_j=template_data_j,
            index=index, labels=labels, distances=distances)

    msg = fid_template + ' selected'

    template_file_path = os.path.join(AFIDS_HUMAN_DIR,
                                      'sub-' + str(fid_template))

    template_file = open(template_file_path, 'r')

    template_data = csv_to_json(template_file)
    template_data_j = json.loads(template_data)
    fiducial_set=Fiducial_set(AC_x = user_data_j['1']['x'],
                              AC_y = user_data_j['1']['y'],
                              AC_z = user_data_j['1']['z'],
                              PC_x = user_data_j['2']['x'],
                              PC_y = user_data_j['2']['y'],
                              PC_z = user_data_j['2']['z'],
                              ICS_x = user_data_j['3']['x'],
                              ICS_y = user_data_j['3']['y'],
                              ICS_z = user_data_j['3']['z'],
                              PMJ_x = user_data_j['4']['x'],
                              PMJ_y = user_data_j['4']['y'],
                              PMJ_z = user_data_j['4']['z'],
                              SIPF_x = user_data_j['5']['x'],
                              SIPF_y = user_data_j['5']['y'],
                              SIPF_z = user_data_j['5']['z'],
                              RSLMS_x = user_data_j['6']['x'],
                              RSLMS_y = user_data_j['6']['y'],
                              RSLMS_z = user_data_j['6']['z'],
                              LSLMS_x = user_data_j['7']['x'],
                              LSLMS_y = user_data_j['7']['y'],
                              LSLMS_z = user_data_j['7']['z'],
                              RILMS_x = user_data_j['8']['x'],
                              RILMS_y = user_data_j['8']['y'],
                              RILMS_z = user_data_j['8']['z'],
                              LILMS_x = user_data_j['9']['x'],
                              LILMS_y = user_data_j['9']['y'],
                              LILMS_z = user_data_j['9']['z'],
                              CUL_x = user_data_j['10']['x'],
                              CUL_y = user_data_j['10']['y'],
                              CUL_z = user_data_j['10']['z'],
                              IMS_x = user_data_j['11']['x'],
                              IMS_y = user_data_j['11']['y'],
                              IMS_z = user_data_j['11']['z'],
                              RMB_x = user_data_j['12']['x'],
                              RMB_y = user_data_j['12']['y'],
                              RMB_z = user_data_j['12']['z'],
                              LMB_x = user_data_j['13']['x'],
                              LMB_y = user_data_j['13']['y'],
                              LMB_z = user_data_j['13']['z'],
                              PG_x = user_data_j['14']['x'],
                              PG_y = user_data_j['14']['y'],
                              PG_z = user_data_j['14']['z'],
                              RLVAC_x = user_data_j['15']['x'],
                              RLVAC_y = user_data_j['15']['y'],
                              RLVAC_z = user_data_j['15']['z'],
                              LLVAC_x = user_data_j['16']['x'],
                              LLVAC_y = user_data_j['16']['y'],
                              LLVAC_z = user_data_j['16']['z'],
                              RLVPC_x = user_data_j['17']['x'],
                              RLVPC_y = user_data_j['17']['y'],
                              RLVPC_z = user_data_j['17']['z'],
                              LLVPC_x = user_data_j['18']['x'],
                              LLVPC_y = user_data_j['18']['y'],
                              LLVPC_z = user_data_j['18']['z'],
                              GENU_x = user_data_j['19']['x'],
                              GENU_y = user_data_j['19']['y'],
                              GENU_z = user_data_j['19']['z'],
                              SPLE_x = user_data_j['20']['x'],
                              SPLE_y = user_data_j['20']['y'],
                              SPLE_z = user_data_j['20']['z'],
                              RALTH_x = user_data_j['21']['x'],
                              RALTH_y = user_data_j['21']['y'],
                              RALTH_z = user_data_j['21']['z'],
                              LALTH_x = user_data_j['22']['x'],
                              LALTH_y = user_data_j['22']['y'],
                              LALTH_z = user_data_j['22']['z'],
                              RSAMTH_x = user_data_j['23']['x'],
                              RSAMTH_y = user_data_j['23']['y'],
                              RSAMTH_z = user_data_j['23']['z'],
                              LSAMTH_x = user_data_j['24']['x'],
                              LSAMTH_y = user_data_j['24']['y'],
                              LSAMTH_z = user_data_j['24']['z'],
                              RIAMTH_x = user_data_j['25']['x'],
                              RIAMTH_y = user_data_j['25']['y'],
                              RIAMTH_z = user_data_j['25']['z'],
                              LIAMTH_x = user_data_j['26']['x'],
                              LIAMTH_y = user_data_j['26']['y'],
                              LIAMTH_z = user_data_j['26']['z'],
                              RIGO_x = user_data_j['27']['x'],
                              RIGO_y = user_data_j['27']['y'],
                              RIGO_z = user_data_j['27']['z'],
                              LIGO_x = user_data_j['28']['x'],
                              LIGO_y = user_data_j['28']['y'],
                              LIGO_z = user_data_j['28']['z'],
                              RVOH_x = user_data_j['29']['x'],
                              RVOH_y = user_data_j['29']['y'],
                              RVOH_z = user_data_j['29']['z'],
                              LVOH_x = user_data_j['30']['x'],
                              LVOH_y = user_data_j['30']['y'],
                              LVOH_z = user_data_j['30']['z'],
                              ROSF_x = user_data_j['31']['x'],
                              ROSF_y = user_data_j['31']['y'],
                              ROSF_z = user_data_j['31']['z'],
                              LOSF_x = user_data_j['32']['x'],
                              LOSF_y = user_data_j['32']['y'],
                              LOSF_z = user_data_j['32']['z'])
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

    result = '<br>'.join([result, msg])

    return render_template("validator.html", form=form, result=result,
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

labels = ['Euclidean', 'X_error', 'Y_error', 'Z_error']

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



flx.assets.associate_asset(__name__, 'https://d3js.org/d3.v4.min.js')
flx.assets.associate_asset(__name__, 'https://unpkg.com/d3-3d/build/d3-3d.min.js')

with open(os.path.join(AFIDS_HUMAN_DIR, 'sub-MNI2009cAsym_afids.fcsv')) as MNI:
    rdr = csv.reader(MNI, delimiter=',')
    MNI_data = []
    for n, row in enumerate(rdr):
        if n < 3: continue;
        entry = {}
        entry['x']=row[1]
        entry['y']=row[2]
        entry['z']=row[3]
        entry['id']=row[12]
        MNI_data.append(entry)
#print(MNI_data)

class DataStore(flx.Component):
    fileuploaded=flx.IntProp(0, settable = True)

    viz_limits = [[-50, 50],[-50, 50],[-30, 30]]

    points = [{'x':0.1, 'y':0.2, 'z':0.3, 'id':'id0'},
        {'x':2.1, 'y':8.2, 'z':4.3, 'id':'id1'},
        {'x':9 , 'y':9, 'z':9, 'id':'id1'}]

    points = MNI_data

    linedata = [[{'x':1,'y':2,'z':3},{'x':3,'y':2,'z':1}],
        [{'x':4,'y':4,'z':4}, {'x':5,'y':5,'z':5}]]

class Validator(flx.Widget):
    data=flx.ComponentProp()
    def init(self):
        self._mutate_data(DataStore())
        Layout()

class Layout(flx.Widget):
    titletext = flx.StringProp('(No File Uploaded.)')
    #'[Filename of Upload] // Registered against [some reference]'
    def init(self):
        with flx.VBox(style='text-align:center'):
            flx.Label(text = lambda:str(self.titletext), style='background:#cfc;font-size:20px')
            with flx.HBox(style='background:#cfc;'):
                self.c1 = flx.CheckBox(text = "option 1", flex=1)
                self.c2 = flx.CheckBox(text = "option 2", flex=1)
                self.c3 = flx.CheckBox(text = "option 3", flex=1)
                self.zoom = flx.Slider(min = 0.1, max = 5.0, value=1.0, text=lambda:'{:.0f}%'.format(self.zoom.value * 100), flex=3)
            PointCloud(self.zoom, flex = 1)

class PointCloud(flx.Widget):

    scale = flx.FloatProp(1.0, settable=True)

    def init(self, zoom):
        self.node.id = self.id
        window.setTimeout(self.load_viz, 500) # don't know what this does
        self.zoom = zoom

    '''
    @flx.reaction
    def _resize(self):
        w, h = self.size
        if len(self.node.children) > 0:
            svg = self.node.children[0]
            svg.setAttribute('width', w)
            svg.setAttribute('height', h)
    '''

    @flx.reaction('zoom.value')
    def _scale(self, *events):
        for ev in events:
            print('caught change event:' +str(ev.new_value))
            self.changescale(ev.new_value)

    @flx.action
    def changescale(self, n):
        self._mutate_scale(n*5)
        #self.node.children[0].setAttribute('scaleattr', n*15)
        #self.svgref.updatescale(n*15)

    def load_viz(self):

        w, h = self.size
        pts = self.root.root.data.points
        linedata = self.root.root.data.linedata
        xGrid = []
        scatter = []
        yLine = []
        scale = self.scale

        origin = [400, 300]
        j = 10
        beta = 0
        alpha = 0
        mx, my, mouseX, mouseY = 0
        startAngle = Math.PI/4

        x = d3.select('#' + self.id)
        svg = RawJS('x.append("svg").attr("width", w).attr("height", h)')
        svg.call(d3.drag().on('drag', dragged).on('start', dragStart).on('end', dragEnd)).append('g')

        #drag = d3.drag().on('drag', RawJS("console.log('fff')")).on('start', RawJS("console.log('skfghsdfh')")).on('end', RawJS("console.log('asdasda')"))
        #svg.call(drag).append('g')

        color  = d3.scaleOrdinal(d3.schemeCategory20)

        key = lambda d:d.id

        grid3d = d3._3d()           \
            .shape('GRID', 20)      \
            .origin(origin)         \
            .rotateY( startAngle)   \
            .rotateX(-startAngle)   \
            .scale(scale)
        point3d = d3._3d()          \
            .x(lambda d:d.x)        \
            .y(lambda d:d.y)        \
            .z(lambda d:d.z)        \
            .origin(origin)         \
            .rotateY( startAngle)   \
            .rotateX(-startAngle)   \
            .scale(scale)
        line = d3._3d()             \
            .origin(origin)         \
            .rotateY( startAngle)   \
            .rotateX(-startAngle)   \
            .scale(scale)           \
            .shape('LINE')          \
            .x(lambda d:d.x)        \
            .y(lambda d:d.y)        \
            .z(lambda d:d.z)
        yScale3d = d3._3d()         \
            .shape('LINE_STRIP')    \
            .origin(origin)         \
            .rotateY( startAngle)   \
            .rotateX(-startAngle)   \
            .scale(scale)

        def init():
            cnt = 0
            global xGrid
            global scatter
            global yLine
            global scale

            xGrid = []
            scatter = []
            yLine = []
            for z in range(-j, j):
                for x in range(-j, j):
                    xGrid.append([x, 1, z])
                    #broken...RawJS(scatter.append({x: x, y: d3.randomUniform(0, -10)(), z: z, id: 'point_' + cnt})
                    cnt += 1
            scatter = pts;
            d3.range(-1, 11, 1).forEach(lambda d:yLine.append([-j, -d, -j]))

            data = [
                grid3d(xGrid),
                point3d(scatter),
                yScale3d([yLine]),
                line(linedata)
            ]
            RawJS("processData(data, 1000);")
        # end init

        RawJS("""
        function processData(data, tt){
            /* ----------- GRID ----------- */
            var xGrid = svg.selectAll('path.grid').data(data[0], key);
            xGrid.enter()
                .append('path')
                .attr('class', '_3d grid')
                .merge(xGrid)
                .attr('stroke', 'black')
                .attr('stroke-width', 0.3)
                .attr('fill', function(d){ return d.ccw ? 'lightgrey' : '#717171'; })
                .attr('fill-opacity', 0.9)
                .attr('d', grid3d.draw);
            xGrid.exit().remove();
            /* ----------- POINTS ----------- */
            var points = svg.selectAll('circle').data(data[1], key);
            points.enter()
                .append('circle')
                .attr('class', '_3d')
                .attr('opacity', 0)
                .attr('cx', function(d){return d.projected.x;})
                .attr('cy', function(d){return d.projected.y;})
                .merge(points)
                .transition().duration(tt)
                .attr('r', 3)
                .attr('stroke', function(d){ return d3.color(color(d.id)).darker(3); })
                .attr('fill', function(d){ return color(d.id); })
                .attr('opacity', 1)
                .attr('cx', function(d){return d.projected.x;})
                .attr('cy', function(d){return d.projected.y;});
            points.exit().remove();
            /* ----------- y-Scale ----------- */
            var yScale = svg.selectAll('path.yScale').data(data[2]);
            yScale.enter()
                .append('path')
                .attr('class', '_3d yScale')
                .merge(yScale)
                .attr('stroke', 'black')
                .attr('stroke-width', .5)
                .attr('d', yScale3d.draw)
            yScale.exit().remove()
            /* ----------- y-Scale Text ----------- */
            var yText = svg.selectAll('text.yText').data(data[2][0]);
            yText.enter()
                .append('text')
                .attr('class', '_3d yText')
                .attr('dx', '.3em')
                .merge(yText)
                .each(function(d){
                d.centroid = {x: d.rotated.x, y: d.rotated.y, z: d.rotated.z};
                })
                .attr('x', function(d){return d.projected.x;})
                .attr('y', function(d){return d.projected.y;})
                .text(function(d){ return d[1] <= 0 ? d[1] : ''; });
            yText.exit().remove()
            // ------------Lines----------------
            var lines = svg.selectAll('line').data(data[3]);
            lines.enter()
                .append('line')
                .attr('class', '_3d')
                .merge(lines)
                .attr('stroke', 'black')
                .attr('x1', function(d){return d[0].projected.x;})
                .attr('y1', function(d){return d[0].projected.y;})
                .attr('x2', function(d){return d[1].projected.x;})
                .attr('y2', function(d){return d[1].projected.y;});
            lines.exit().remove();

            d3.selectAll('._3d').sort(d3._3d().sort);
        }

        function dragStart(){
            mx = d3.event.x;
            my = d3.event.y;
            }

        function dragged(){
            mouseX = mouseX || 0;
            mouseY = mouseY || 0;
            beta   = (d3.event.x - mx + mouseX) * Math.PI / 230;
            alpha  = (d3.event.y - my + mouseY) * Math.PI / 230  * (-1);
            console.log(scale)
            var data = [
                grid3d.scale(scale).rotateY(beta + startAngle).rotateX(alpha - startAngle)(xGrid),
                point3d.scale(scale).rotateY(beta + startAngle).rotateX(alpha - startAngle)(scatter),
                yScale3d.scale(scale).rotateY(beta + startAngle).rotateX(alpha - startAngle)([yLine]),
                line.scale(scale).rotateY(beta + startAngle).rotateX(alpha - startAngle)(linedata)
            ];
            processData(data, 0);
        }

        function dragEnd(){
            mouseX = d3.event.x - mx + mouseX;
            mouseY = d3.event.y - my + mouseY;
        }
        """)

        RawJS("""
        function manipcent(d){
            d.centroid = {x: d.rotated.x, y: d.rotated.y, z: d.rotated.z}
        }
        """)
        init()
    #end

testapp = flx.App(Validator)
testapp.export("templates/pointcloud.html", link = 0)
#assets = testapp.dump('templates/pointcloud.html', link=0)

@app.route('/analytics')

def chartTest():

    return render_template('view_analytics.html')

@app.route('/pointcloud.html', methods=['GET'])
def cloud():
    return render_template("pointcloud.html")

if __name__ == '__main__':
    app.run(debug=True)
