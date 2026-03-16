"""Route requests with Flask."""

from __future__ import annotations

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
    generate_radar_chart,
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
    template_root = Path(current_app.root_path) / "afids-templates"
    species_templates = {}
    for species_dir in sorted(template_root.iterdir()):
        if not species_dir.is_dir():
            continue
        templates = sorted(
            f.name[4:].split("_")[0]
            for f in species_dir.iterdir()
            if f.name.startswith("tpl")
        )
        species_templates[species_dir.name.capitalize()] = templates
    total_templates = sum(len(t) for t in species_templates.values())
    return render_template(
        "index.html",
        current_user=current_user,
        species_templates=species_templates,
        total_templates=total_templates,
        n_species=len(species_templates),
    )


# Contact
@validator.route("/contact.html")
def contact():
    """Render the static contact page."""
    return render_template("contact.html", current_user=current_user)


# Login
@validator.route("/login.html")
def login():
    """Render the static login page."""
    client_id = current_app.config.get("ORCID_OAUTH_CLIENT_ID", "")
    orcid_configured = bool(client_id) and client_id not in (
        "dev",
        "dev-placeholder",
        "from-orcid",
    )
    return render_template(
        "login.html",
        current_user=current_user,
        orcid_configured=orcid_configured,
    )


@validator.route("/logout.html")
def logout():
    """Log out user and render the index."""
    logout_user()
    return redirect("/")


def _direction_label(dx, dy, dz, threshold=0.1):
    """Convert LPS error components into anatomical direction language.

    In the tool's internal LPS representation:
      dx > 0 → too far Left,      dx < 0 → too far Right
      dy > 0 → too far Posterior, dy < 0 → too far Anterior
      dz > 0 → too far Superior,  dz < 0 → too far Inferior

    Parameters
    ----------
    dx, dy, dz : float
        Error components (user − template) in LPS space.
    threshold : float
        Components smaller than this (mm) are suppressed.

    Returns
    -------
    str
        Human-readable directional error, e.g. "2.1mm posterior, 1.4mm left".
    """
    axes = [
        (dx, "left", "right"),
        (dy, "posterior", "anterior"),
        (dz, "superior", "inferior"),
    ]
    parts = []
    for value, pos_label, neg_label in axes:
        if abs(value) >= threshold:
            direction = pos_label if value > 0 else neg_label
            parts.append(f"{abs(value):.1f}mm {direction}")
    return ", ".join(parts) if parts else "< 0.1mm"


def _session_summary(labels, float_distances):
    """Compute summary statistics for a validation session."""
    mean = float(np.mean(float_distances))
    sd = float(np.std(float_distances))
    worst_idx = int(np.argmax(float_distances))
    best_idx = int(np.argmin(float_distances))
    return {
        "mean": f"{mean:.2f}",
        "sd": f"{sd:.2f}",
        "worst_label": labels[worst_idx],
        "worst_dist": f"{float_distances[worst_idx]:.2f}",
        "best_label": labels[best_idx],
        "best_dist": f"{float_distances[best_idx]:.2f}",
        "n_within_1mm": sum(1 for d in float_distances if d < 1.0),
        "n_within_2mm": sum(1 for d in float_distances if d < 2.0),
        "total": len(float_distances),
    }


@dataclass
class PlacementReport:
    """Dataclass for reporting fiducial placement error."""

    labels: list[str]
    distances: list[str]
    directions: list[str]
    summary: dict
    scatter_html: str
    histogram_html: str
    radar_html: str

    @classmethod
    def from_afids(cls, user_afids, template_afids):
        """Calculate report variables from two sets of afids."""
        distances = []
        directions = []
        labels = []

        for desc in EXPECTED_DESCS:
            label = desc[-1]
            u = getattr(user_afids, label)
            t = getattr(template_afids, label)
            dx, dy, dz = u.x - t.x, u.y - t.y, u.z - t.z
            distance = np.linalg.norm([dx, dy, dz])
            direction = _direction_label(dx, dy, dz)

            distances.append(f"{distance:.5f}")
            directions.append(direction)
            labels.append(label)

        float_distances = [float(d) for d in distances]
        summary = _session_summary(labels, float_distances)

        scatter_html = generate_3d_scatter(template_afids, user_afids)
        histogram_html = generate_histogram(template_afids, user_afids)
        radar_html = generate_radar_chart(template_afids, user_afids)
        return cls(
            labels,
            distances,
            directions,
            summary,
            scatter_html,
            histogram_html,
            radar_html,
        )


def render_validator(form, result="", placement_report=None):
    """Render the validator page."""
    form_choices = sorted(
        [
            choice.name.capitalize()
            for choice in (
                Path(current_app.root_path) / "afids-templates"
            ).iterdir()
        ]
    )
    if placement_report:
        placement_dict = {
            "table_rows": list(
                zip(
                    placement_report.labels,
                    placement_report.distances,
                    placement_report.directions,
                )
            ),
            "summary": placement_report.summary,
            "scatter_html": placement_report.scatter_html,
            "histogram_html": placement_report.histogram_html,
            "radar_html": placement_report.radar_html,
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
        Path(current_app.root_path)
        / "afids-templates"
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
                species_templates.name[4:].split("_")[0]
                for species_templates in (
                    Path(current_app.root_path)
                    / "afids-templates"
                    / species.lower()
                ).iterdir()
                if "tpl" in species_templates.name
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
