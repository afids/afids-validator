"""Route requests with Flask."""

import os
import io
from datetime import datetime, timezone

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import wtforms as wtf

from model import csv_to_afids, InvalidFileError


app = Flask(__name__)

app.config.from_object(os.environ["APP_SETTINGS"])
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class FiducialSet(db.Model):
    """SQL model for a set of AFIDs."""

    __tablename__ = "fid_db"

    id = db.Column(db.Integer, primary_key=True)
    c = [
        "AC",
        "PC",
        "ICS",
        "PMJ",
        "SIPF",
        "RSLMS",
        "LSLMS",
        "RILMS",
        "LILMS",
        "CUL",
        "IMS",
        "RMB",
        "LMB",
        "PG",
        "RLVAC",
        "LLVAC",
        "RLVPC",
        "LLVPC",
        "GENU",
        "SPLE",
        "RALTH",
        "LALTH",
        "RSAMTH",
        "LSAMTH",
        "RIAMTH",
        "LIAMTH",
        "RIGO",
        "LIGO",
        "RVOH",
        "LVOH",
        "ROSF",
        "LOSF",
    ]

    for base in c:
        exec("%s_x = %s" % (base, "db.Column(db.Float())"))
        exec("%s_y = %s" % (base, "db.Column(db.Float())"))
        exec("%s_z = %s" % (base, "db.Column(db.Float())"))

    def __repr__(self):
        return "<id {}>".format(self.id)

    def serialize(self):
        """Produce a dict of each column."""
        serialized = {
            "AC_x": self.AC_x,
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
            "LOSF_z": self.LOSF_z,
        }

        return serialized


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
ALLOWED_EXTENSIONS = set(["fcsv", "csv", "json"])


def allowed_file(filename):
    """Does filename have the right extension?"""
    return "." in filename and filename.rsplit(".", 1)[1] in ALLOWED_EXTENSIONS


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

    if not (upload and allowed_file(upload.filename)):
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
        user_afids = csv_to_afids(
            io.StringIO(upload.stream.read().decode("utf-8"))
        )
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

    result = f"Valid file ({timestamp})"

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
        template_afids = csv_to_afids(template_file)

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
