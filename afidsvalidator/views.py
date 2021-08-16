"""Route requests with Flask."""

import os
from datetime import datetime, timezone

from flask import render_template, request, jsonify, Blueprint, current_app
import numpy as np
import wtforms as wtf

from afidsvalidator.model import (
    db,
    csv_to_afids,
    json_to_afids,
    InvalidFileError,
    EXPECTED_DESCS,
    HumanFiducialSet,
)
from afidsvalidator.visualizations import (
    generate_3d_scatter,
    generate_histogram,
)


validator = Blueprint("validator", __name__, template_folder="templates")


class Average(wtf.Form):
    """Form for selecting and submitting a file."""

    filename = wtf.FileField(validators=[wtf.validators.InputRequired()])
    submit = wtf.SubmitField(label="Submit")


# TO BE DEPECRATED
def allowed_file(filename):
    """Does filename have the right extension?"""
    file_ext = filename.rsplit(".", 1)[1]

    return (
        file_ext,
        "." in filename
        and file_ext in current_app.config["ALLOWED_EXTENSIONS"],
    )


# Routes to web pages / application
# Homepage
@validator.route("/")
def index():
    """Render the static index page."""
    return render_template("index.html")


# Contact
@validator.route("/contact.html")
def contact():
    """Render the static contact page."""
    return render_template("contact.html")


# Login
@validator.route("/login.html")
def login():
    """Render the static login page."""
    return render_template("login.html")


# Validator
@validator.route("/validator.html", methods=["GET", "POST"])
def validate():
    """Present the validator form, or validate an AFIDs set."""
    form = Average(request.form)

    result = ""
    distances = []
    labels = []
    template_afids = None

    # Set all dropdown choices
    form_choices = os.listdir(current_app.config["AFIDS_DIR"])
    form_choices = [choice.capitalize() for choice in form_choices]
    form_choices.sort()

    # Get time stamp
    timestamp = str(
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    )

    if not (request.method == "POST" and request.files):
        return render_template(
            "validator.html",
            form=form,
            form_choices=form_choices,
            result=result,
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
            form_choices=form_choices,
            result=result,
            template_afids=template_afids,
            index=[],
            labels=labels,
            distances=distances,
        )

    try:
        if upload_ext in current_app.config["ALLOWED_EXTENSIONS"][:2]:
            user_afids = csv_to_afids(upload.read().decode("utf-8"))
        else:
            user_afids = json_to_afids(upload.read().decode("utf-8"))
    except InvalidFileError as err:
        result = f"Invalid file: {err.message} ({timestamp})"
        return render_template(
            "validator.html",
            form=form,
            form_choices=form_choices,
            result=result,
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

    fid_species = request.form["fid_species"]
    fid_species = fid_species.lower()
    fid_template = request.form["fid_template"]

    if fid_template == "Validate file structure":
        return render_template(
            "validator.html",
            form=form,
            form_choices=form_choices,
            result=result,
            template_afids=template_afids,
            index=[],
            labels=labels,
            distances=distances,
        )

    result = f"{result}<br>{fid_template} selected"
    # Need to pull from correct folder when more templates are added
    template_file_path = f"{current_app.config['AFIDS_DIR']}/{fid_species.lower()}/tpl-{fid_template}_afids.fcsv"

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
        form_choices=form_choices,
        result=result,
        template_afids=template_afids,
        index=list(range(len(EXPECTED_DESCS))),
        labels=labels,
        distances=distances,
        timestamp=timestamp,
        scatter_html=generate_3d_scatter(template_afids, user_afids),
        histogram_html=generate_histogram(template_afids, user_afids),
    )


@validator.route("/validator/<species>")
def get_templates(species):
    """Get templates corresponding to specific species"""
    return jsonify(
        ["Validate file structure"]
        + [
            species_templates[4:].split("_")[0]
            for species_templates in os.listdir(
                f"{current_app.config['AFIDS_DIR']}/{species.lower()}"
            )
            if "tpl" in species_templates
        ]
    )


@validator.route("/getall")
def get_all():
    """Dump all AFIDs sets in the database."""
    fiducial_sets = HumanFiducialSet.query.all()
    serialized_fset = []
    for fset in fiducial_sets:
        serialized_fset.append(fset.serialize())
    return render_template("db.html", serialized_fset=serialized_fset)
