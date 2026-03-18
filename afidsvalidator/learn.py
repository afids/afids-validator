"""Guided learning mode — LLM-assisted landmark placement on MRI.

Routes
------
GET  /learn                 Render the guided learning page
GET  /learn/nifti           Serve MNI152NLin2009cAsym T1w NIfTI
                            (downloads from TemplateFlow and caches locally
                            on first request)
GET  /learn/references      JSON — all 32 reference coords in RAS mm
POST /learn/check           JSON — compute error for a placed coordinate
POST /learn/intro           Stream — LLM introduction for a landmark
POST /learn/feedback        Stream — LLM feedback after placement
POST /learn/chat            Stream — LLM answer to a free-text question
"""

from __future__ import annotations

import json
import math
import urllib.request
from pathlib import Path

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    render_template,
    request,
    stream_with_context,
)

from afidsvalidator.landmark_info import LANDMARK_INFO
from afidsvalidator.llm import (
    build_feedback_messages,
    build_intro_messages,
    build_question_messages,
    stream_chat,
)

learn = Blueprint("learn", __name__, template_folder="templates")

# ── Template constants ────────────────────────────────────────────────────────
TEMPLATE_NAME = "tpl-MNI152NLin2009cAsym"

# TemplateFlow public S3 — 1 mm isotropic T1w for MNI152NLin2009cAsym

FCSV_PATH = (
    Path(__file__).parent
    / "afids-templates"
    / "human"
    / f"{TEMPLATE_NAME}_afids.fcsv"
)

# Ordered list of landmark abbreviations (matches AFIDs protocol / FCSV order)
LANDMARK_ORDER: list[str] = list(LANDMARK_INFO.keys())


# ── Helpers ───────────────────────────────────────────────────────────────────
def _load_references() -> dict[str, list[float]]:
    """Parse FCSV and return {abbrev: [x, y, z]} in RAS mm.

    FCSV CoordinateSystem=0 in this codebase means RAS, which is the same
    space NiiVue reports when loading a standard neuroimaging NIfTI.
    """
    refs: dict[str, list[float]] = {}
    with open(FCSV_PATH) as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            parts = line.strip().split(",")
            if len(parts) < 13:
                continue
            try:
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                abbrev = parts[12]  # 'desc' column holds the abbreviation
                refs[abbrev] = [x, y, z]
            except (ValueError, IndexError):
                continue
    return refs



def _stream_llm(messages: list[dict]) -> Response:
    """Return a streaming plain-text Flask response from the LLM."""

    def generate():
        try:
            for chunk in stream_chat(messages):
                yield chunk
        except Exception as exc:  # noqa: BLE001
            yield f"\n\n[Tutor unavailable — {exc}]"

    return Response(
        stream_with_context(generate()),
        mimetype="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Transfer-Encoding": "chunked",
        },
    )


# ── Routes ────────────────────────────────────────────────────────────────────
@learn.route("/learn")
def learn_page():
    landmarks = [
        {
            "abbrev": abbrev,
            "full_name": LANDMARK_INFO[abbrev]["full_name"],
        }
        for abbrev in LANDMARK_ORDER
    ]
    return render_template(
        "learn.html",
        landmarks=landmarks,
        template_name=TEMPLATE_NAME,
    )


def _nifti_url_for_res(res: str) -> str:
    return (
        "https://templateflow.s3.amazonaws.com/tpl-MNI152NLin2009cAsym/"
        f"tpl-MNI152NLin2009cAsym_res-{res}_T1w.nii.gz"
    )


def _nifti_cache_path_for_res(res: str) -> Path:
    cache_dir = Path(current_app.instance_path) / "brain_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{TEMPLATE_NAME}_res-{res}_T1w.nii.gz"


@learn.route("/learn/nifti")
def serve_nifti():
    """Serve MNI152NLin2009cAsym T1w NIfTI.

    ?res=02  (default) — 2 mm isotropic, ~1.7 MB, fast
    ?res=01            — 1 mm isotropic, ~9 MB, high detail

    Downloads from TemplateFlow on first request, then serves from cache.
    """
    res = request.args.get("res", "02")
    if res not in ("01", "02"):
        res = "02"

    cache = _nifti_cache_path_for_res(res)

    if not cache.exists():
        url = _nifti_url_for_res(res)
        current_app.logger.info("Downloading res-%s from TemplateFlow …", res)
        try:
            urllib.request.urlretrieve(url, cache)
        except Exception as exc:  # noqa: BLE001
            current_app.logger.error("TemplateFlow download failed: %s", exc)
            return jsonify({"error": str(exc)}), 502

    file_size = cache.stat().st_size

    def generate():
        with open(cache, "rb") as fh:
            while True:
                chunk = fh.read(65_536)
                if not chunk:
                    break
                yield chunk

    return Response(
        stream_with_context(generate()),
        mimetype="application/octet-stream",
        headers={
            "Content-Length": str(file_size),
            "Content-Disposition": f'inline; filename="{cache.name}"',
            "Cache-Control": "public, max-age=86400",
            "Access-Control-Allow-Origin": "*",
        },
    )


@learn.route("/learn/references")
def get_references():
    """Return all 32 reference coordinates (RAS mm) as JSON."""
    refs = _load_references()
    landmarks = [
        {
            "abbrev": abbrev,
            "full_name": LANDMARK_INFO[abbrev]["full_name"],
            "coords": refs.get(abbrev, [0.0, 0.0, 0.0]),
        }
        for abbrev in LANDMARK_ORDER
        if abbrev in refs
    ]
    return jsonify({"template": TEMPLATE_NAME, "landmarks": landmarks})


@learn.route("/learn/check", methods=["POST"])
def check_placement():
    """Compute Euclidean distance and directional error for a placement.

    Request JSON
    ------------
    { "landmark": "AC", "coords": [x, y, z] }   ← RAS mm from NiiVue

    Response JSON
    -------------
    { landmark, distance_mm, user_coords, ref_coords, directions, quality }
    """
    data = request.get_json(force=True)
    abbrev: str = data.get("landmark", "")
    user: list[float] = data.get("coords", [])

    if len(user) != 3:
        return jsonify({"error": "coords must be [x, y, z]"}), 400

    refs = _load_references()
    ref = refs.get(abbrev)
    if ref is None:
        return jsonify({"error": f"Unknown landmark: {abbrev!r}"}), 400

    dx = user[0] - ref[0]
    dy = user[1] - ref[1]
    dz = user[2] - ref[2]
    distance = math.sqrt(dx**2 + dy**2 + dz**2)

    # RAS: +x right, +y anterior, +z superior
    THRESHOLD = 0.5  # mm — suppress tiny directional components
    directions: list[str] = []
    if abs(dx) >= THRESHOLD:
        directions.append(
            f"{'right' if dx > 0 else 'left'} by {abs(dx):.1f} mm"
        )
    if abs(dy) >= THRESHOLD:
        directions.append(
            f"{'anterior' if dy > 0 else 'posterior'} by {abs(dy):.1f} mm"
        )
    if abs(dz) >= THRESHOLD:
        directions.append(
            f"{'superior' if dz > 0 else 'inferior'} by {abs(dz):.1f} mm"
        )

    if distance < 1.0:
        quality = "excellent"
    elif distance < 2.0:
        quality = "good"
    elif distance < 4.0:
        quality = "fair"
    else:
        quality = "needs_work"

    return jsonify(
        {
            "landmark": abbrev,
            "distance_mm": round(distance, 2),
            "user_coords": user,
            "ref_coords": ref,
            "directions": directions,
            "quality": quality,
        }
    )


@learn.route("/learn/intro", methods=["POST"])
def stream_intro():
    """Stream an LLM introduction for a landmark.

    Request JSON: { "landmark": "AC" }
    """
    data = request.get_json(force=True)
    abbrev: str = data.get("landmark", "")
    messages = build_intro_messages(abbrev)
    return _stream_llm(messages)


@learn.route("/learn/feedback", methods=["POST"])
def stream_feedback():
    """Stream LLM feedback after a placement.

    Request JSON
    ------------
    {
      "landmark": "AC",
      "distance_mm": 2.4,
      "quality": "fair",
      "history": [ {role, content}, … ]
    }
    Note: directional error vectors are intentionally excluded so the LLM
    teaches anatomy rather than coordinate navigation.
    """
    data = request.get_json(force=True)
    messages = build_feedback_messages(
        history=data.get("history", []),
        abbrev=data.get("landmark", ""),
        distance_mm=float(data.get("distance_mm", 0)),
        quality=data.get("quality", ""),
        user_coords=data.get("user_coords"),
        ref_coords=data.get("ref_coords"),
        directions=data.get("directions", []),
        viewer_state=data.get("viewer_state"),
    )
    return _stream_llm(messages)


@learn.route("/learn/chat", methods=["POST"])
def stream_chat_route():
    """Stream an LLM answer to a free-text question.

    Request JSON
    ------------
    {
      "question": "What does the AC look like on T2?",
      "history": [ {role, content}, … ]
    }
    """
    data = request.get_json(force=True)
    messages = build_question_messages(
        history=data.get("history", []),
        question=data.get("question", ""),
    )
    return _stream_llm(messages)
