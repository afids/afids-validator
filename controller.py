"""Route requests with Flask."""

import os
from datetime import datetime, timezone

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import wtforms as wtf

# from model import csv_to_afids, json_to_afids, InvalidFileError
from visualizations import generate_3d_scatter, generate_histogram

app = Flask(__name__)

app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Average(wtf.Form):
    """Form for selecting and submitting a file."""

    filename = wtf.FileField(validators=[wtf.validators.InputRequired()])
    submit = wtf.SubmitField(label="Submit")


# Relative path of directory for uploaded files
UPLOAD_DIR = "uploads/"
AFIDS_HUMAN_DIR = "afids-templates/human/"

app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
app.secret_key = "MySecretKey"

if not os.path.isdir(UPLOAD_DIR):
    os.mkdir(UPLOAD_DIR)

# Allowed file types for file upload
ALLOWED_EXTENSIONS = ["fcsv", "csv", "json"]


## TO BE DEPECRATED
def allowed_file(filename):
    """Does filename have the right extension?"""
    file_ext = filename.rsplit(".", 1)[1]

    return file_ext, "." in filename and file_ext in ALLOWED_EXTENSIONS


# Routes to web pages / application
# Homepage
@app.route("/")
def index():
    """Render the static index page."""
    return render_template("index.html")


# Contact
@app.route("/contact.html")
def contact():
    """Render the static contact page."""
    return render_template("contact.html")


# Login
@app.route("/login.html")
def login():
    """Render the static login page."""
    return render_template("login.html")


# Validator
@app.route("/validator.html", methods=["GET", "POST"])
def validator():
    """Present the validator form, or validate an AFIDs set."""
    form = Average(request.form)

    result = ""
    distances = []
    labels = []
    template_afids = None

    # Identify all human templates
    human_templates = []
    for human_dir in os.listdir(AFIDS_HUMAN_DIR):
        if "tpl" in human_dir:
            human_dir = human_dir[4:]
        human_templates.append(human_dir.split("_")[0])

    timestamp = str(
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    )

    if not request.method == "POST":
        return render_template(
            "validator.html",
            form=form,
            result=result,
            human_templates=human_templates,
            template_afids=template_afids,
            index=[],
            labels=labels,
            distances=distances,
        )

    if not request.files:
        return render_template(
            "validator.html",
            form=form,
            result=result,
            human_templates=human_templates,
            template_afids=template_afids,
            index=[],
            labels=labels,
            distances=distances,
        )

    upload = request.files[form.filename.name]
    upload_ext, file_check = allowed_file(upload.filename)

    if not (upload and file_check):
        result = f"Invalid file: extension not allowed ({timestamp})"

        return render_template(
            "validator.html",
            form=form,
            result=result,
            human_templates=human_templates,
            template_afids=template_afids,
            index=[],
            labels=labels,
            distances=distances,
        )

    try:
        if upload_ext in ALLOWED_EXTENSIONS[:2]:
            user_afids = csv_to_afids(upload.read().decode("utf-8"))
        else:
            user_afids = json_to_afids(upload.read().decode("utf-8"))
    except InvalidFileError as err:
        result = f"Invalid file: {err.message} ({timestamp})"
        return render_template(
            "validator.html",
            form=form,
            result=result,
            human_templates=human_templates,
            template_afids=template_afids,
            index=[],
            labels=labels,
            distances=distances,
        )

    if user_afids.validate():
        result = f"Valid file ({timestamp})"
    else:
        result = (
            f"Invalid AFIDs set, please double check your file ({timestamp})"
        )

    fid_template = request.form["fid_template"]

    if fid_template == "Validate file structure":
        return render_template(
            "validator.html",
            form=form,
            result=result,
            human_templates=human_templates,
            template_afids=template_afids,
            index=[],
            labels=labels,
            distances=distances,
        )

    result = f"{result}<br>{fid_template} selected"

    # Need to pull from correct folder when more templates are added
    if fid_template in human_templates:
        template_file_path = os.path.join(
            AFIDS_HUMAN_DIR, f"tpl-{fid_template}_afids.fcsv"
        )

    with open(template_file_path, "r") as template_file:
        template_afids = csv_to_afids(template_file.read())

    if request.form.get("db_checkbox"):
        db.session.add(
            FiducialSet(
                AC_x=user_afids.get_fiducial_position(1, "x"),
                AC_y=user_afids.get_fiducial_position(1, "y"),
                AC_z=user_afids.get_fiducial_position(1, "z"),
                PC_x=user_afids.get_fiducial_position(2, "x"),
                PC_y=user_afids.get_fiducial_position(2, "y"),
                PC_z=user_afids.get_fiducial_position(2, "z"),
                ICS_x=user_afids.get_fiducial_position(3, "x"),
                ICS_y=user_afids.get_fiducial_position(3, "y"),
                ICS_z=user_afids.get_fiducial_position(3, "z"),
                PMJ_x=user_afids.get_fiducial_position(4, "x"),
                PMJ_y=user_afids.get_fiducial_position(4, "y"),
                PMJ_z=user_afids.get_fiducial_position(4, "z"),
                SIPF_x=user_afids.get_fiducial_position(5, "x"),
                SIPF_y=user_afids.get_fiducial_position(5, "y"),
                SIPF_z=user_afids.get_fiducial_position(5, "z"),
                RSLMS_x=user_afids.get_fiducial_position(6, "x"),
                RSLMS_y=user_afids.get_fiducial_position(6, "y"),
                RSLMS_z=user_afids.get_fiducial_position(6, "z"),
                LSLMS_x=user_afids.get_fiducial_position(7, "x"),
                LSLMS_y=user_afids.get_fiducial_position(7, "y"),
                LSLMS_z=user_afids.get_fiducial_position(7, "z"),
                RILMS_x=user_afids.get_fiducial_position(8, "x"),
                RILMS_y=user_afids.get_fiducial_position(8, "y"),
                RILMS_z=user_afids.get_fiducial_position(8, "z"),
                LILMS_x=user_afids.get_fiducial_position(9, "x"),
                LILMS_y=user_afids.get_fiducial_position(9, "y"),
                LILMS_z=user_afids.get_fiducial_position(9, "z"),
                CUL_x=user_afids.get_fiducial_position(10, "x"),
                CUL_y=user_afids.get_fiducial_position(10, "y"),
                CUL_z=user_afids.get_fiducial_position(10, "z"),
                IMS_x=user_afids.get_fiducial_position(11, "x"),
                IMS_y=user_afids.get_fiducial_position(11, "y"),
                IMS_z=user_afids.get_fiducial_position(11, "z"),
                RMB_x=user_afids.get_fiducial_position(12, "x"),
                RMB_y=user_afids.get_fiducial_position(12, "y"),
                RMB_z=user_afids.get_fiducial_position(12, "z"),
                LMB_x=user_afids.get_fiducial_position(13, "x"),
                LMB_y=user_afids.get_fiducial_position(13, "y"),
                LMB_z=user_afids.get_fiducial_position(13, "z"),
                PG_x=user_afids.get_fiducial_position(14, "x"),
                PG_y=user_afids.get_fiducial_position(14, "y"),
                PG_z=user_afids.get_fiducial_position(14, "z"),
                RLVAC_x=user_afids.get_fiducial_position(15, "x"),
                RLVAC_y=user_afids.get_fiducial_position(15, "y"),
                RLVAC_z=user_afids.get_fiducial_position(15, "z"),
                LLVAC_x=user_afids.get_fiducial_position(16, "x"),
                LLVAC_y=user_afids.get_fiducial_position(16, "y"),
                LLVAC_z=user_afids.get_fiducial_position(16, "z"),
                RLVPC_x=user_afids.get_fiducial_position(17, "x"),
                RLVPC_y=user_afids.get_fiducial_position(17, "y"),
                RLVPC_z=user_afids.get_fiducial_position(17, "z"),
                LLVPC_x=user_afids.get_fiducial_position(18, "x"),
                LLVPC_y=user_afids.get_fiducial_position(18, "y"),
                LLVPC_z=user_afids.get_fiducial_position(18, "z"),
                GENU_x=user_afids.get_fiducial_position(19, "x"),
                GENU_y=user_afids.get_fiducial_position(19, "y"),
                GENU_z=user_afids.get_fiducial_position(19, "z"),
                SPLE_x=user_afids.get_fiducial_position(20, "x"),
                SPLE_y=user_afids.get_fiducial_position(20, "y"),
                SPLE_z=user_afids.get_fiducial_position(20, "z"),
                RALTH_x=user_afids.get_fiducial_position(21, "x"),
                RALTH_y=user_afids.get_fiducial_position(21, "y"),
                RALTH_z=user_afids.get_fiducial_position(21, "z"),
                LALTH_x=user_afids.get_fiducial_position(22, "x"),
                LALTH_y=user_afids.get_fiducial_position(22, "y"),
                LALTH_z=user_afids.get_fiducial_position(22, "z"),
                RSAMTH_x=user_afids.get_fiducial_position(23, "x"),
                RSAMTH_y=user_afids.get_fiducial_position(23, "y"),
                RSAMTH_z=user_afids.get_fiducial_position(23, "z"),
                LSAMTH_x=user_afids.get_fiducial_position(24, "x"),
                LSAMTH_y=user_afids.get_fiducial_position(24, "y"),
                LSAMTH_z=user_afids.get_fiducial_position(24, "z"),
                RIAMTH_x=user_afids.get_fiducial_position(25, "x"),
                RIAMTH_y=user_afids.get_fiducial_position(25, "y"),
                RIAMTH_z=user_afids.get_fiducial_position(25, "z"),
                LIAMTH_x=user_afids.get_fiducial_position(26, "x"),
                LIAMTH_y=user_afids.get_fiducial_position(26, "y"),
                LIAMTH_z=user_afids.get_fiducial_position(26, "z"),
                RIGO_x=user_afids.get_fiducial_position(27, "x"),
                RIGO_y=user_afids.get_fiducial_position(27, "y"),
                RIGO_z=user_afids.get_fiducial_position(27, "z"),
                LIGO_x=user_afids.get_fiducial_position(28, "x"),
                LIGO_y=user_afids.get_fiducial_position(28, "y"),
                LIGO_z=user_afids.get_fiducial_position(28, "z"),
                RVOH_x=user_afids.get_fiducial_position(29, "x"),
                RVOH_y=user_afids.get_fiducial_position(29, "y"),
                RVOH_z=user_afids.get_fiducial_position(29, "z"),
                LVOH_x=user_afids.get_fiducial_position(30, "x"),
                LVOH_y=user_afids.get_fiducial_position(30, "y"),
                LVOH_z=user_afids.get_fiducial_position(30, "z"),
                ROSF_x=user_afids.get_fiducial_position(31, "x"),
                ROSF_y=user_afids.get_fiducial_position(31, "y"),
                ROSF_z=user_afids.get_fiducial_position(31, "z"),
                LOSF_x=user_afids.get_fiducial_position(32, "x"),
                LOSF_y=user_afids.get_fiducial_position(32, "y"),
                LOSF_z=user_afids.get_fiducial_position(32, "z"),
            )
        )
        db.session.commit()
        print("Fiducial set added")
    else:
        print("DB option unchecked, user data not saved")

    for element in range(1, template_afids.no_of_fiducials + 1):
        distances.append(
            "{:.5f}".format(
                np.linalg.norm(
                    np.array(
                        [
                            float(pos)
                            for pos in template_afids.get_fiducial_positions(
                                element
                            )
                        ]
                    )
                    - np.array(
                        [
                            float(pos)
                            for pos in user_afids.get_fiducial_positions(
                                element
                            )
                        ]
                    )
                )
            )
        )
        labels.append(template_afids.get_fiducial_description(element))

    return render_template(
        "validator.html",
        form=form,
        result=result,
        human_templates=human_templates,
        template_afids=template_afids,
        index=list(range(template_afids.no_of_fiducials)),
        labels=labels,
        distances=distances,
        timestamp=timestamp,
        scatter_html=generate_3d_scatter(template_afids, user_afids),
        histogram_html=generate_histogram(template_afids, user_afids),
    )


@app.route("/getall")
def get_all():
    """Dump all AFIDs sets in the database."""
    fiducial_sets = FiducialSet.query.all()
    serialized_fset = []
    for fset in fiducial_sets:
        serialized_fset.append(fset.serialize())
    return render_template("db.html", serialized_fset=serialized_fset)


if __name__ == "__main__":
    app.run(debug=True)
