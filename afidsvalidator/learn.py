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
POST /learn/llm-status      JSON — active model + whether a key is in use
"""

from __future__ import annotations

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

from afidsvalidator import reliability
from afidsvalidator.landmark_info import LANDMARK_INFO
from afidsvalidator.llm import (
    build_feedback_messages,
    build_intro_messages,
    build_question_messages,
    resolve_model_label,
    server_has_default_key,
    stream_chat,
)
from afidsvalidator.rag import retrieve

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
                # Label column (index 11) is the 1-based landmark number;
                # use it to look up the abbreviation from the protocol order.
                label = int(parts[11])
                abbrev = LANDMARK_ORDER[label - 1]
                refs[abbrev] = [x, y, z]
            except (ValueError, IndexError):
                continue
    return refs


def _extract_llm_config(data: dict) -> dict | None:
    """Pull an optional per-request LLM override from the request body.

    The visitor's browser may send ``{"llm": {api_key, base_url, model}}`` —
    a key held only client-side (localStorage) and forwarded per request. We
    never log or persist it. Returns None when no usable override is present.
    """
    cfg = data.get("llm")
    if not isinstance(cfg, dict):
        return None
    override = {
        k: cfg.get(k)
        for k in ("api_key", "base_url", "model")
        if isinstance(cfg.get(k), str) and cfg.get(k).strip()
    }
    return override or None


def _offline_fallback(chunks: list[str], abbrev: str = "") -> str:
    """Reference text shown when no language model is reachable.

    Guarantees the learner still gets useful anatomy — the tool never
    dead-ends — while nudging them to add their own key for interactive
    tutoring.
    """
    note = (
        "The interactive AI tutor needs a language-model key. Add your own "
        "in Settings (⚙) to enable conversational tutoring. In the "
        "meantime, here is the reference material for this landmark:\n\n"
    )
    body = "\n\n".join(c for c in chunks if c).strip()
    if not body and abbrev in LANDMARK_INFO:
        info = LANDMARK_INFO[abbrev]
        body = (
            f"{abbrev} — {info['full_name']}\n"
            f"{info['description']}\n"
            f"Key features on MRI: {info['key_features']}\n"
            f"Common mistakes: {info['common_mistakes']}"
        )
    return note + (body or "Reference material is unavailable right now.")


def _stream_llm(
    messages: list[dict],
    llm_config: dict | None = None,
    fallback: str | None = None,
) -> Response:
    """Return a streaming plain-text Flask response from the LLM.

    If the model cannot be reached before producing any output and a
    *fallback* is provided, the fallback text is streamed instead so the
    learner is never left with a dead tutor.
    """

    def generate():
        produced = False
        try:
            for chunk in stream_chat(messages, llm_config=llm_config):
                produced = True
                yield chunk
        except Exception as exc:  # noqa: BLE001
            if not produced and fallback:
                yield fallback
            else:
                yield f"\n\n[Tutor interrupted — {exc}]"

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
            # Where this placement sits within the trained-rater distribution
            # for THIS landmark (from the AFIDs multi-rater dataset). None when
            # the landmark is absent from the reliability prior.
            "rater": reliability.band(abbrev, distance),
        }
    )


@learn.route("/learn/intro", methods=["POST"])
def stream_intro():
    """Stream an LLM introduction for a landmark.

    Request JSON: { "landmark": "AC" }
    """
    data = request.get_json(force=True)
    abbrev: str = data.get("landmark", "")
    info = LANDMARK_INFO.get(abbrev, {})
    query = (
        f"{abbrev} {info.get('full_name', '')} MRI anatomy placement protocol"
    )
    chunks = retrieve(query, landmark_hint=abbrev, top_k=3)
    messages = build_intro_messages(
        abbrev,
        context_chunks=chunks,
        rater_context=reliability.intro_line(abbrev),
    )
    return _stream_llm(
        messages,
        llm_config=_extract_llm_config(data),
        fallback=_offline_fallback(chunks, abbrev),
    )


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
    abbrev: str = data.get("landmark", "")
    directions: list[str] = data.get("directions", [])
    info = LANDMARK_INFO.get(abbrev, {})
    query = (
        f"{abbrev} {info.get('full_name', '')} placement error "
        + " ".join(directions)
    )
    chunks = retrieve(query, landmark_hint=abbrev, top_k=3)
    messages = build_feedback_messages(
        history=data.get("history", []),
        abbrev=abbrev,
        distance_mm=float(data.get("distance_mm", 0)),
        quality=data.get("quality", ""),
        user_coords=data.get("user_coords"),
        ref_coords=data.get("ref_coords"),
        directions=directions,
        viewer_state=data.get("viewer_state"),
        context_chunks=chunks,
        rater_context=reliability.feedback_line(
            abbrev, float(data.get("distance_mm", 0))
        ),
    )
    return _stream_llm(
        messages,
        llm_config=_extract_llm_config(data),
        fallback=_offline_fallback(chunks, abbrev),
    )


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
    question: str = data.get("question", "")
    chunks = retrieve(question, top_k=4)
    messages = build_question_messages(
        history=data.get("history", []),
        question=question,
        context_chunks=chunks,
    )
    return _stream_llm(
        messages,
        llm_config=_extract_llm_config(data),
        fallback=_offline_fallback(chunks),
    )


@learn.route("/learn/llm-status", methods=["POST"])
def llm_status():
    """Report the model that will answer, given an optional client override.

    Request JSON: { "llm": {api_key, base_url, model} }  (all optional)
    Response JSON: { model, using_own_key, shared_default_available }

    Lets the UI show the active model and whether the visitor is running on
    their own key or the shared default tutor. No key is stored or logged.
    """
    data = request.get_json(force=True, silent=True) or {}
    override = _extract_llm_config(data) or {}
    return jsonify(
        {
            "model": resolve_model_label(override),
            "using_own_key": bool(override.get("api_key")),
            "shared_default_available": server_has_default_key(),
        }
    )
