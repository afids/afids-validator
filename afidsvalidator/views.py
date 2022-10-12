"""Route requests with Flask."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import wtforms as wtf
from flask import (
    Blueprint,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
)
from flask_login import current_user, logout_user

from afidsvalidator.model import (
    EXPECTED_DESCS,
    FiducialFiletype,
    HumanFiducialSet,
    InvalidFileError,
    csv_to_afids,
    db,
    json_to_afids,
)
from afidsvalidator.visualizations import (
    generate_3d_scatter,
    generate_histogram,
)

validator = Blueprint("validator", __name__, template_folder="templates")


class Average(wtf.Form):
    # pylint: disable=too-few-public-methods
    """Form for selecting and submitting a file."""

    filename = wtf.FileField(validators=[wtf.validators.InputRequired()])
    submit = wtf.SubmitField(label="Submit")


# Routes to web pages / application
# Homepage
@validator.route("/")
def index():
    """Render the static index page."""
    return render_template("index.html", current_user=current_user)


# Contact
@validator.route("/contact.html")
def contact():
    """Render the static contact page."""
    return render_template("contact.html", current_user=current_user)


# Login
@validator.route("/login.html")
def login():
    """Render the static login page."""
    return render_template("login.html", current_user=current_user)


@validator.route("/logout.html")
def logout():
    """Log out user and render the index."""
    logout_user()
    return redirect("/")


@dataclass
class PlacementReport:
    """Dataclass for reporting fiducial placement error."""

    labels: list[str]
    distances: list[float]
    scatter_html: str
    histogram_html: str

    @classmethod
    def from_afids(cls, user_afids, template_afids):
        """Calculate report variables from two sets of afids."""
        distances = []
        labels = []
        for desc in EXPECTED_DESCS:
            distance = np.linalg.norm(
                np.array(
                    [getattr(template_afids, desc[-1]).__composite_values__()]
                )
                - np.array(
                    [getattr(user_afids, desc[-1]).__composite_values__()]
                )
            )
            distances.append(f"{distance:.5f}")
            labels.append(desc[-1])
        scatter_html = generate_3d_scatter(template_afids, user_afids)
        histogram_html = generate_histogram(template_afids, user_afids)
        return cls(labels, distances, scatter_html, histogram_html)


def render_validator(form, result="", placement_report=None):
    """Render the validator page."""
    form_choices = sorted(
        [
            choice.capitalize()
            for choice in os.listdir(current_app.config["AFIDS_DIR"])
        ]
    )
    if placement_report:
        placement_dict = {
            "table_zip": zip(
                placement_report.labels, placement_report.distances
            ),
            "scatter_html": placement_report.scatter_html,
            "histogram_html": placement_report.histogram_html,
        }
    else:
        placement_dict = {}
    return render_template(
        "app.html",
        form=form,
        form_choices=form_choices,
        result=result,
        current_user=current_user,
        timestamp=str(
            datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
        ),
        **placement_dict,
    )


# Validator
# pylint: disable=no-member
@validator.route("/app.html", methods=["GET", "POST"])
def validate():
    """Present the validator form, or validate an AFIDs set."""
    form = Average(request.form)

    if not (request.method == "POST" and request.files):
        return render_validator(form)

    upload = request.files[form.filename.name]

    try:
        filetype = FiducialFiletype.from_extension(
            Path(upload.filename).suffix
        )
        if filetype is FiducialFiletype.CSV_LIKE:
            user_afids = csv_to_afids(upload.read().decode("utf-8"))
        elif filetype is FiducialFiletype.JSON_LIKE:
            user_afids = json_to_afids(upload.read().decode("utf-8"))
    except ValueError:
        return render_validator(form, result="Unsupported file extension")
    except InvalidFileError as err:
        return render_validator(
            form,
            result=f"Invalid file: {err.message}",
        )

    if user_afids.validate():
        result = "Valid file"
    else:
        return render_validator(
            form, result="Invalid AFIDs set, please double check your file"
        )

    fid_template = request.form["fid_template"]

    if fid_template == "Validate file structure":
        return render_validator(form, result=result)

    result = f"{result}<br>{fid_template} selected"

    # Need to pull from correct folder when more templates are added
    with open(
        Path(current_app.config["AFIDS_DIR"])
        / request.form["fid_species"].lower()
        / f"tpl-{fid_template}_afids.fcsv",
        "r",
        encoding="utf-8",
    ) as template_file:
        template_afids = csv_to_afids(template_file.read())

    if request.form.get("db_checkbox"):
        if current_user.is_authenticated:
            user_afids.afids_user_id = current_user.id
        db.session.add(user_afids)
        db.session.commit()
        print("Fiducial set added")
    else:
        print("DB option unchecked, user data not saved")

    return render_validator(
        form,
        result=result,
        placement_report=PlacementReport.from_afids(
            user_afids, template_afids
        ),
    )


@validator.route("/validator/<species>")
def get_templates(species):
    """Get templates corresponding to specific species"""
    return jsonify(
        ["Validate file structure"]
        + sorted(
            [
                species_templates[4:].split("_")[0]
                for species_templates in os.listdir(
                    f"{current_app.config['AFIDS_DIR']}/{species.lower()}"
                )
                if "tpl" in species_templates
            ],
            key=str.lower,
        )
    )


@validator.route("/getall")
def get_all():
    """Dump all AFIDs sets in the database."""
    fiducial_sets = HumanFiducialSet.query.all()
    serialized_fset = []
    for fset in fiducial_sets:
        serialized_fset.append(fset.serialize())
    return render_template("db.html", serialized_fset=serialized_fset)
