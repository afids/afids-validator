"""Model-agnostic LLM interface for the AFIDs guided learning mode.

Configure via environment variables:
  LLM_API_KEY   — API key. If unset, defaults to local Ollama (free, no key needed).
  LLM_BASE_URL  — Base URL of any OpenAI-compatible endpoint.
                  If LLM_API_KEY is unset, defaults to http://localhost:11434/v1 (Ollama).
                  Examples:
                    OpenAI    : https://api.openai.com/v1  (needs LLM_API_KEY)
                    Anthropic : https://api.anthropic.com/v1  (needs LLM_API_KEY)
                    Groq      : https://api.groq.com/openai/v1  (needs LLM_API_KEY)
                    Together  : https://api.together.xyz/v1  (needs LLM_API_KEY)
                    Ollama    : http://localhost:11434/v1  (no key required — free)
  LLM_MODEL     — Model name.
                  Defaults to llama3.2 when using Ollama, or gpt-4o otherwise.
                  Examples (Ollama):  llama3.2, llama3.1, mistral, phi4, gemma3
                  Examples (Groq):    llama-3.3-70b-versatile, mixtral-8x7b-32768
                  Examples (OpenAI):  gpt-4o, gpt-4o-mini

Zero-config quick start (local, free):
  1. Install Ollama: https://ollama.com
  2. Run: ollama pull llama3.2
  3. Start the app — no env vars needed.

RAG context
-----------
The message builders accept an optional ``context_chunks`` list (retrieved from
the knowledge store via afidsvalidator.rag.retrieve).  When chunks are provided
they are injected into the system prompt in place of the former static landmark
block, giving the model targeted, query-specific context rather than all 32
landmark definitions on every call.

When ``context_chunks`` is None or empty the system prompt falls back to a
compact version that still carries the tutor persona and behavioural rules —
the model then relies on its pre-trained neuroanatomy knowledge.
"""

from __future__ import annotations

import os
from typing import Generator

from afidsvalidator.landmark_info import LANDMARK_INFO

# ── Ordered landmark list (matches FCSV / AFIDs protocol order) ───────────────
LANDMARK_ORDER: list[str] = list(LANDMARK_INFO.keys())

# ── Base system prompt (persona + rules, no landmark definitions) ─────────────
_SYSTEM_PROMPT_BASE = """\
You are an expert neuroanatomy tutor embedded inside the \
AFIDs Validator (https://validator.afids.io), an open-access neuroimaging \
education platform built around the Anatomical Fiducials (AFIDs) protocol \
(https://afids.github.io/afids-protocol/).

Your job is to guide users — typically graduate students, postdocs, or \
clinicians new to neuroimaging — through placing 32 precisely defined \
anatomical landmarks on a T1-weighted MRI of the MNI152NLin2009cAsym brain \
template. The viewer uses RAS coordinates (positive x = right, positive y = \
anterior, positive z = superior).

YOUR THREE MODES:

1. INTRODUCTION (when asked to introduce a landmark)
   - 3–5 sentences maximum.
   - Tell the user WHAT the structure is anatomically (what it does, why it \
matters in the AFIDs protocol and in neuroimaging normalisation).
   - Then describe WHERE to find it on this T1w MRI — which plane to use \
(axial / coronal / sagittal), what surrounding structures to anchor on, and \
what the landmark looks like on T1 contrast.
   - End with one practical tip to avoid the most common mistake for this \
landmark.
   - Tone: encouraging, clear, expert but not condescending.

2. PLACEMENT FEEDBACK (when the user has placed a fiducial)
   You will receive: the placed coordinate (RAS mm), the reference coordinate \
(RAS mm), the Euclidean distance, quality, directional offset, AND the \
current viewer settings (zoom, resolution, contrast window).
   Steps:
   a) Open with a one-line verdict naming the distance \
(e.g. "Not quite — 17.3 mm off." or "Excellent — 0.8 mm!").
   b) Reason anatomically about what the user likely clicked instead, drawing \
on the landmark description and common mistakes in the reference material below.
   c) Use anatomical directions freely to orient them \
("too posterior", "slightly superior to the genu", etc.).
   d) VIEWER RECOMMENDATION — always check the viewer settings and advise \
the user specifically:
      • If zoom ≤ 1.5 and error > 3 mm → suggest zooming in ("+/− buttons \
or scroll) for better precision.
      • If resolution is 2mm and error > 4 mm → suggest switching to 1mm \
(the RES button). 1mm is the FINEST resolution available — NEVER suggest \
0.5mm or any other value.
      • If both apply, mention both. If the placement is already excellent \
or the viewer is already optimised, skip this step.
   - 4–6 sentences total. Keep it tight.

3. QUESTION ANSWERING (when the user asks a follow-up)
   - Answer precisely, using anatomical terminology.
   - Reference MRI planes, contrast behaviour, and viewer settings where \
relevant.
   - If the question is about finding a structure, mention which plane and \
zoom/resolution would help most.
   - 2–4 sentences unless the question requires more.

VIEWER CONTROLS THAT ACTUALLY EXIST (never suggest anything else):
- Resolution: only two options, 2mm and 1mm. 1mm is the finest available. \
NEVER mention 0.5mm, sub-millimetre, or any other resolution.
- Zoom: the +/− buttons or mouse scroll; a reset-zoom button; and a \
"Go to landmark" button that jumps the crosshair near the current target.
- View: a radiological/neurological convention toggle and a sagittal flip.
- Actions: Place Fiducial, Show Reference, Next Landmark.
Do NOT invent tools, buttons, filters, overlays, measurements, or resolutions \
the viewer does not have. If the placement is already good, do not force a \
viewer suggestion.

GENERAL RULES:
- Use millimetres (mm) for distances when reporting accuracy scores.
- Anatomical directional language is encouraged ("too posterior", "slightly \
superior to that", "lateral to the midline") — this is how anatomy is taught.
- NEVER tell the user to "set the cursor to [x, y, z]" or give raw coordinate \
values as instructions. Teach anatomy and visual landmarks, not number lookup.
- Do not use excessive markdown — this renders in a simple chat pane.
- Never fabricate landmark positions. If unsure, say so.
- TONE — always warm, constructive, and encouraging, even for large errors. \
Treat a miss as a normal, expected step in learning, never as a failure. Do \
NOT use alarming or judgemental words such as "concerning", "wrong", "poor", \
"bad", "off-target", or "problem". Instead use gentle framings like "not \
quite yet", "close — let's refine this", "a spot that's easy to slip on", or \
"good instinct — the actual landmark is just nearby". Acknowledge what the \
learner did reasonably before guiding them to the correction.
- PLAIN LANGUAGE — keep the correct neuroanatomical terms (this is a real \
protocol), but make them accessible. The FIRST time you use a term, add a \
short plain-language gloss in the same breath, e.g. "the fornix — the \
arching band of fibres beneath the corpus callosum". Prefer short sentences, \
introduce one structure at a time, and never stack several unfamiliar terms \
in a row. Write for a motivated beginner who is seeing this anatomy for the \
first time, not for an expert audience. Precise and simple, not dumbed down.
- Neuroanatomy is hard; normalise the difficulty while maintaining precision.\
"""


def build_system_prompt(context_chunks: list[str] | None = None) -> str:
    """Build the full system prompt, optionally injecting retrieved context.

    When *context_chunks* is non-empty the retrieved passages are appended
    after the base rules under a labelled section.  This replaces the former
    static block that embedded all 32 landmark definitions on every call.
    """
    if not context_chunks:
        return _SYSTEM_PROMPT_BASE

    context = "\n\n".join(context_chunks)
    return (
        _SYSTEM_PROMPT_BASE
        + "\n\n"
        + "━" * 48
        + "\nREFERENCE MATERIAL (retrieved for this query)\n"
        + "━" * 48
        + "\n\n"
        + context
    )


# ── Client factory ────────────────────────────────────────────────────────────
_OLLAMA_DEFAULT_URL = "http://localhost:11434/v1"
_OPENAI_DEFAULT_URL = "https://api.openai.com/v1"


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _pick(override: dict, field: str, env: str) -> str:
    """Return the override field if set, else the environment variable."""
    return _clean(override.get(field)) or _clean(os.environ.get(env))


def _resolve_llm(override: dict | None = None):
    """Resolve an (OpenAI-compatible client, model name) pair.

    Precedence for each of api_key / base_url / model is:
        user-supplied *override* → env variable → built-in default
    This is what powers "bring your own key": a request may carry its own
    ``{api_key, base_url, model}`` (held only in the visitor's browser and
    sent per-request), and it takes priority over the server's shared default.

    When no key is available from either source we fall back to a local
    OpenAI-compatible endpoint (Ollama by default) — appropriate for
    development, and handled gracefully upstream when unreachable.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The 'openai' package is required for guided learning. "
            "Install it with:  poetry add openai"
        ) from exc

    override = override or {}
    api_key = _pick(override, "api_key", "LLM_API_KEY")
    base_url = _pick(override, "base_url", "LLM_BASE_URL")
    model = _pick(override, "model", "LLM_MODEL")

    if api_key:
        client = OpenAI(
            api_key=api_key, base_url=base_url or _OPENAI_DEFAULT_URL
        )
        return client, (model or "gpt-4o")

    # No key anywhere → local self-hosted OpenAI-compatible endpoint (Ollama).
    client = OpenAI(api_key="ollama", base_url=base_url or _OLLAMA_DEFAULT_URL)
    return client, (model or "llama3.2")


def resolve_model_label(override: dict | None = None) -> str:
    """Return the model name that *would* be used, for display in the UI."""
    override = override or {}
    model = _pick(override, "model", "LLM_MODEL")
    if model:
        return model
    has_key = _pick(override, "api_key", "LLM_API_KEY")
    return "gpt-4o" if has_key else "llama3.2"


def server_has_default_key() -> bool:
    """True when the deployment carries a shared default API key."""
    return bool(_clean(os.environ.get("LLM_API_KEY")))


# ── Message builders ──────────────────────────────────────────────────────────


def build_intro_messages(
    abbrev: str,
    context_chunks: list[str] | None = None,
    rater_context: str | None = None,
) -> list[dict]:
    """Return the messages list that triggers a landmark introduction.

    Parameters
    ----------
    abbrev:
        AFIDs landmark abbreviation (e.g. "AC").
    context_chunks:
        Retrieved knowledge chunks from ``rag.retrieve()`` to inject as
        reference material.  Pass ``None`` or ``[]`` to use the base prompt
        without additional context.
    """
    info = LANDMARK_INFO.get(abbrev, {})
    full_name = info.get("full_name", abbrev)
    rater_str = f"\n\n[{rater_context}]" if rater_context else ""
    return [
        {"role": "system", "content": build_system_prompt(context_chunks)},
        {
            "role": "user",
            "content": (
                f"Please introduce landmark {abbrev} ({full_name}). "
                f"Tell me what it is anatomically and how to find it on the "
                f"MNI152NLin2009cAsym T1w MRI in the viewer. "
                f"I will then click to place my marker.{rater_str}"
            ),
        },
    ]


def build_feedback_messages(
    history: list[dict],
    abbrev: str,
    distance_mm: float,
    quality: str,
    user_coords: list[float] | None = None,
    ref_coords: list[float] | None = None,
    directions: list[str] | None = None,
    viewer_state: dict | None = None,
    context_chunks: list[str] | None = None,
    rater_context: str | None = None,
) -> list[dict]:
    """Append a placement result to history and return the full messages list.

    The system message is always rebuilt with fresh retrieved context so the
    model has up-to-date reference material regardless of prior conversation
    state stored in *history*.
    """
    system = {"role": "system", "content": build_system_prompt(context_chunks)}
    # Strip any existing system message from history (we just rebuilt it)
    prior = [m for m in history if m.get("role") != "system"]

    info = LANDMARK_INFO.get(abbrev, {})
    full_name = info.get("full_name", abbrev)

    quality_labels = {
        "excellent": "Excellent",
        "good": "Good",
        "fair": "Fair — needs improvement",
        "needs_work": "Needs significant improvement",
    }
    verdict = quality_labels.get(quality, quality)

    coord_str = ""
    if user_coords and len(user_coords) == 3:
        coord_str += (
            f"\nPlaced at  : ({user_coords[0]:.1f}, {user_coords[1]:.1f}, "
            f"{user_coords[2]:.1f}) mm RAS"
        )
    if ref_coords and len(ref_coords) == 3:
        coord_str += (
            f"\nReference  : ({ref_coords[0]:.1f}, {ref_coords[1]:.1f}, "
            f"{ref_coords[2]:.1f}) mm RAS"
        )
    if directions:
        coord_str += f"\nOffset     : {', '.join(directions)}"

    viewer_parts = []
    if viewer_state:
        if viewer_state.get("resolution"):
            viewer_parts.append(f"resolution: {viewer_state['resolution']}")
        if viewer_state.get("zoom"):
            viewer_parts.append(f"zoom: {viewer_state['zoom']}×")
        if viewer_state.get("contrast_min") and viewer_state.get("contrast_max"):
            viewer_parts.append(
                f"contrast window: {viewer_state['contrast_min']}–"
                f"{viewer_state['contrast_max']}"
            )
    viewer_str = (
        f"\nViewer settings at placement: {', '.join(viewer_parts)}."
        if viewer_parts
        else ""
    )

    rater_str = f"\n\n[{rater_context}]" if rater_context else ""
    content = (
        f"I placed my fiducial for {abbrev} ({full_name})."
        f"{coord_str}\n"
        f"Distance from reference: {distance_mm:.1f} mm ({verdict})."
        f"{viewer_str}{rater_str}\n\n"
        f"Please give anatomical feedback and — based on the viewer settings "
        f"above — tell me whether I should adjust my zoom or switch to a "
        f"higher resolution to place this landmark more precisely."
    )
    return [system] + prior + [{"role": "user", "content": content}]


def build_question_messages(
    history: list[dict],
    question: str,
    context_chunks: list[str] | None = None,
) -> list[dict]:
    """Append a user question to history and return the full messages list.

    The system message is rebuilt with freshly retrieved context chunks so
    free-form questions benefit from the most relevant reference material.
    """
    system = {"role": "system", "content": build_system_prompt(context_chunks)}
    prior = [m for m in history if m.get("role") != "system"]
    return [system] + prior + [{"role": "user", "content": question}]


# ── Streaming ─────────────────────────────────────────────────────────────────


def stream_chat(
    messages: list[dict],
    llm_config: dict | None = None,
) -> Generator[str, None, None]:
    """Yield text chunks from the LLM for the given messages.

    *llm_config* is an optional per-request override
    (``{api_key, base_url, model}``) supplied by the visitor's browser; when
    present it takes priority over the server's shared default credentials.
    """
    # Ensure a system prompt is always first
    if not messages or messages[0].get("role") != "system":
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT_BASE}
        ] + messages

    client, model = _resolve_llm(llm_config)
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        max_tokens=512,
        temperature=0.65,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content
