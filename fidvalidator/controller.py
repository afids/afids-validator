from flask import Flask, render_template, request
from compute import calc
from model import InputForm
import os
import io
import json
from model_auto import Average, csv_to_json, InvalidFcsvError

app = Flask(__name__)

# Relative path of directory for uploaded files
UPLOAD_DIR = 'uploads/'
AFIDS_DIR = '../afids-examples'

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

@app.route('/home', methods=['GET', 'POST'])
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
@app.route('/auto', methods=['GET', 'POST'])
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

                        print(labels)
                        print(distances)

                    result = 'valid file'

                except InvalidFcsvError as err:
                    result = 'invalid file: {err_msg}'.format(
                        err_msg=err.message)

            else:
                result = "invalid file: extension not allowed"

        else:
            result = None

    dir_contents = os.listdir('AFIDS_DIR')
    fid_templates = [' ']
    for d in dir_contents:
        if 'sub' in d:
            fid_templates.append(d[4:])

    result = '<br>'.join([result, msg])

    return render_template("view.html", form=form, result=result,
        fid_templates=fid_templates, template_data_j=template_data_j,
        index=index, labels=labels, distances=distances)


if __name__ == '__main__':
    app.run(debug=True)
