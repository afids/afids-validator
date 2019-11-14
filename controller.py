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

@app.route('/manual', methods=['GET', 'POST'])
def index():
    form = InputForm(request.form)
    if request.method == 'POST' and form.validate():
        AC_result = calc(4.1493909375, 5.678821875, 1.4795320625, form.AC_x.data, form.AC_y.data, form.AC_z.data)
        PC_result = calc(3.230568125, -19.9064125, -4.8756628125, form.PC_x.data, form.PC_y.data, form.PC_z.data)
        inf_result = calc(2.7960728125, -28.60988125, -16.037834375, form.inf_x.data, form.inf_y.data, form.inf_z.data)
        pmj_result = calc(3.421190625, -13.23296875, 20.471746875, form.pmj_x.data, form.pmj_y.data, form.pmj_z.data)
        sup_inc_fos_result = calc(3.7356490625, -7.0098490625, -8.73979625, form.sup_inc_fos_x.data, form.sup_inc_fos_y.data, form.sup_inc_fos_z.data)
        r_s_LMS_result = calc(15.00718125, -18.92895, -11.42105, form.r_s_LMS_x.data, form.r_s_LMS_y.data, form.r_s_LMS_z.data)
        l_s_LMS_result = calc(-8.9887453125, -18.22670625, -11.611440625, form.l_s_LMS_x.data, form.l_s_LMS_y.data, form.l_s_LMS_z.data)
        r_i_LMS_result = calc(12.9510625, -19.957878125, -22.0481875, form.r_i_LMS_x.data, form.r_i_LMS_y.data, form.r_i_LMS_z.data)
        l_i_LMS_result = calc(-6.58012, -18.918334375, -21.962928125, form.l_i_LMS_x.data, form.l_i_LMS_y.data, form.l_i_LMS_z.data)
        culmen_result = calc(1.9017196875, -45.484784375, -8.999916875, form.culmen_x.data, form.culmen_y.data, form.culmen_z.data)
        inter_sulc_result = calc(4.1352415625, -0.979683125, -10.888861875, form.inter_sulc_x.data, form.inter_sulc_y.data, form.inter_sulc_z.data)
        r_mb_result = calc(6.2714584375, -1.11439859375, -10.123704375, form.r_mb_x.data, form.r_mb_y.data, form.r_mb_z.data)
        l_mb_result = calc(2.0448515625, -1.0498715, -10.1120240625, form.l_mb_x.data, form.l_mb_y.data, form.l_mb_z.data)
        pineal_gland_result = calc(2.71287806451613, -25.8692322580645, -4.8119764516129, form.pineal_gland_x.data, form.pineal_gland_y.data, form.pineal_gland_z.data)
        R_LV_AC_result = calc(18.5991193548387, -1.43247861290323, 27.0781129032258, form.R_LV_AC_x.data, form.R_LV_AC_y.data, form.R_LV_AC_z.data)
        L_LV_AC_result = calc(-10.3797935483871, -0.49853207416129, 26.8744612903226, form.L_LV_AC_x.data, form.L_LV_AC_y.data, form.L_LV_AC_z.data)
        R_LV_PC_result = calc(19.942035483871, -27.043164516129, 20.7925064516129, form.R_LV_PC_x.data, form.R_LV_PC_y.data, form.R_LV_PC_z.data)
        L_LV_PC_result = calc(-14.210164516129, -25.8379516129032, 20.1862161290323, form.L_LV_PC_x.data, form.L_LV_PC_y.data, form.L_LV_PC_z.data)
        Genu_CC_result = calc(5.71588387096774, 30.3565935483871, 17.8990612903226, form.Genu_CC_x.data, form.Genu_CC_y.data, form.Genu_CC_z.data)
        Splenium_result = calc(2.77803741935484, -33.2722419354839, -1.48662096774194, form.Splenium_x.data, form.Splenium_y.data, form.Splenium_z.data)
        R_AL_th_result = calc(34.5893322580645, 4.67491564516129, -19.1329580645161, form.R_AL_th_x.data, form.R_AL_th_y.data, form.R_AL_th_z.data)
        L_AL_th_result = calc(-26.4258033333333, 5.573503, -18.5154666666667, form.L_AL_th_x.data, form.L_AL_th_y.data, form.L_AL_th_z.data)
        R_sup_AM_result = calc(20.0146677419355, -2.76956322580645, -12.6547741935484, form.R_sup_AM_x.data, form.R_sup_AM_y.data, form.R_sup_AM_z.data)
        L_sup_AM_result = calc(-12.7199, -1.5710084516129, -13.342735483871, form.L_sup_AM_x.data, form.L_sup_AM_y.data, form.L_sup_AM_z.data)
        R_inf_AM_result = calc(23.7998322580645, 5.47109629032258, -20.4116451612903, form.R_inf_AM_x.data, form.R_inf_AM_y.data, form.R_inf_AM_z.data)
        L_inf_AM_result = calc(-15.4023451612903, 6.27700967741935, -20.3798290322581, form.L_inf_AM_x.data, form.L_inf_AM_y.data, form.L_inf_AM_z.data)
        R_ind_gri_result = calc(16.3600566666667, -36.32495, -4.74025133333333, form.R_ind_gri_x.data, form.R_ind_gri_y.data, form.R_ind_gri_z.data)
        L_ind_gri_result = calc(-12.6529866666667, -36.9170033333333, -5.394859, form.L_ind_gri_x.data, form.L_ind_gri_y.data, form.L_ind_gri_z.data)
        R_vent_occ_result = calc(17.9502032258065, -72.2104290322581, -15.9509193548387, form.R_vent_occ_x.data, form.R_vent_occ_y.data, form.R_vent_occ_z.data)
        L_vent_occ_result = calc(-17.3203, -72.2444096774194, -16.6694870967742, form.L_vent_occ_x.data, form.L_vent_occ_y.data, form.L_vent_occ_z.data)
        R_olf_sulc_result = calc(16.6454870967742, 21.8877451612903, 1.22183009677419, form.R_olf_sulc_x.data, form.R_olf_sulc_y.data, form.R_olf_sulc_z.data)
        L_olf_sulc_result = calc(-6.78613258064516, 22.1233483870968, -0.0616581741935484, form.L_olf_sulc_x.data, form.L_olf_sulc_y.data, form.L_olf_sulc_z.data)

    else:
        AC_result = 0
        PC_result = 0
        inf_result = 0
        pmj_result = 0
        sup_inc_fos_result = 0
        r_s_LMS_result = 0
        l_s_LMS_result = 0
        r_i_LMS_result = 0
        l_i_LMS_result = 0
        culmen_result = 0
        inter_sulc_result = 0
        r_mb_result = 0
        l_mb_result = 0
        pineal_gland_result = 0
        R_LV_AC_result = 0
        L_LV_AC_result = 0
        R_LV_PC_result = 0
        L_LV_PC_result = 0
        Genu_CC_result = 0
        Splenium_result = 0
        R_AL_th_result = 0
        L_AL_th_result = 0
        R_sup_AM_result = 0
        L_sup_AM_result = 0
        R_inf_AM_result = 0
        L_inf_AM_result = 0
        R_ind_gri_result = 0
        L_ind_gri_result = 0
        R_vent_occ_result = 0
        L_vent_occ_result = 0
        R_olf_sulc_result = 0
        L_olf_sulc_result = 0

    return render_template("view_plain2.html", form=form,
        AC_result=AC_result,
        PC_result=PC_result,
        inf_result=inf_result,
        pmj_result=pmj_result,
        sup_inc_fos_result=sup_inc_fos_result,
        r_s_LMS_result=r_s_LMS_result,
        l_s_LMS_result=l_s_LMS_result,
        r_i_LMS_result=r_i_LMS_result,
        l_i_LMS_result=l_i_LMS_result,
        culmen_result=culmen_result,
        inter_sulc_result=inter_sulc_result,
        r_mb_result=r_mb_result,
        l_mb_result=l_mb_result,
        pineal_gland_result=pineal_gland_result,
        R_LV_AC_result=R_LV_AC_result,
        L_LV_AC_result=L_LV_AC_result,
        R_LV_PC_result=R_LV_PC_result,
        L_LV_PC_result=L_LV_PC_result,
        Genu_CC_result=Genu_CC_result,
        Splenium_result=Splenium_result,
        R_AL_th_result=R_AL_th_result,
        L_AL_th_result=L_AL_th_result,
        R_sup_AM_result=R_sup_AM_result,
        L_sup_AM_result=L_sup_AM_result,
        R_inf_AM_result=R_inf_AM_result,
        L_inf_AM_result=L_inf_AM_result,
        R_ind_gri_result=R_ind_gri_result,
        L_ind_gri_result=L_ind_gri_result,
        R_vent_occ_result=R_vent_occ_result,
        L_vent_occ_result=L_vent_occ_result,
        R_olf_sulc_result=R_olf_sulc_result,
        L_olf_sulc_result=L_olf_sulc_result)
    # need to complete this list

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

    dir_contents = os.listdir(AFIDS_DIR)
    fid_templates = [' ']
    for d in dir_contents:
        if 'sub' in d:
            fid_templates.append(d[4:])

    if not request.method == 'POST':
        result = '<br>'.join([result, msg])

        return render_template("view.html", form=form, result=result,
            fid_templates=fid_templates, template_data_j=template_data_j,
            index=index, labels=labels, distances=distances)

    if not request.files:
        result = '<br>'.join([result, msg])

        return render_template("view.html", form=form, result=result,
            fid_templates=fid_templates, template_data_j=template_data_j,
            index=index, labels=labels, distances=distances)

    upload = request.files[form.filename.name]


    if not (upload and allowed_file(upload.filename)):
        result = "invalid file: extension not allowed"
        result = '<br>'.join([result, msg])

        return render_template("view.html", form=form, result=result,
            fid_templates=fid_templates, template_data_j=template_data_j,
            index=index, labels=labels, distances=distances)

    try:
        user_data = csv_to_json(io.StringIO(upload.stream.read().decode('utf-8')))
    except InvalidFcsvError as err:
        result = 'invalid file: {err_msg}'.format(err_msg=err.message)
        return render_template("view.html", form=form, result=result,
            fid_templates=fid_templates, template_data_j=template_data_j,
            index=index, labels=labels, distances=distances)

    result = 'valid file'
    user_data_j = json.loads(user_data)

    fid_template = request.form['fid_template']

    if fid_template == ' ':
        result = "valid file"
        result = '<br>'.join([result, msg])

        return render_template("view.html", form=form, result=result,
            fid_templates=fid_templates, template_data_j=template_data_j,
            index=index, labels=labels, distances=distances)

    msg = fid_template + ' selected'

    template_file_path = os.path.join(os.path.join(AFIDS_DIR,
                                        'sub-' + str(fid_template)),
                                        'sub-' + str(fid_template) +
                                        '_afids.fcsv')

    template_file = open(template_file_path, 'r')

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



flx.assets.associate_asset(__name__, 'https://d3js.org/d3.v4.min.js')
flx.assets.associate_asset(__name__, 'https://unpkg.com/d3-3d/build/d3-3d.min.js')

with open('./afids-examples/sub-MNI2009cAsym/sub-MNI2009cAsym_afids.fcsv') as MNI:
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
