from flask import Flask, render_template, request
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import os

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


if __name__ == '__main__':
    app.run(debug=True)
