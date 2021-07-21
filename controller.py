"""Route requests with Flask."""

import os
from datetime import datetime, timezone
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import numpy as np
import wtforms as wtf

from model import (
    csv_to_afids,
    json_to_afids,
    InvalidFileError,
    db,
    app,
    EXPECTED_DESCS,
    HumanFiducialSet,
)
from visualizations import generate_3d_scatter, generate_histogram


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

    return (
        file_ext,
        "." in filename and file_ext in ALLOWED_EXTENSIONS,
    )


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
        db.session.add(user_afids)
        db.session.commit()
        print("Fiducial set added")
    else:
        print("DB option unchecked, user data not saved")

    for desc in EXPECTED_DESCS:
        distances.append(
            "{:.5f}".format(
                np.linalg.norm(
                    np.array(
                        [
                            getattr(
                                template_afids, desc[-1]
                            ).__composite_values__()
                        ]
                    )
                    - np.array(
                        [getattr(user_afids, desc[-1]).__composite_values__()]
                    )
                )
            )
        )
        labels.append(desc[-1])

    return render_template(
        "validator.html",
        form=form,
        result=result,
        human_templates=human_templates,
        template_afids=template_afids,
        index=list(range(len(EXPECTED_DESCS))),
        labels=labels,
        distances=distances,
        timestamp=timestamp,
        scatter_html=generate_3d_scatter(template_afids, user_afids),
        histogram_html=generate_histogram(template_afids, user_afids),
    )


@app.route("/getall")
def get_all():
    """Dump all AFIDs sets in the database."""
    fiducial_sets = HumanFiducialSet.query.all()
    serialized_fset = []
    for fset in fiducial_sets:
        serialized_fset.append(fset.serialize())
    return render_template("db.html", serialized_fset=serialized_fset)


if __name__ == "__main__":
    app.run(debug=True)
