"""Model-agnostic LLM interface for the AFIDs guided learning mode.

Configure via environment variables:
  LLM_API_KEY   — API key (required)
  LLM_BASE_URL  — Base URL of any OpenAI-compatible endpoint
                  Defaults to https://api.openai.com/v1
                  Examples:
                    Anthropic : https://api.anthropic.com/v1
                    Ollama    : http://localhost:11434/v1
                    Together  : https://api.together.xyz/v1
  LLM_MODEL     — Model name. Defaults to gpt-4o
                  Examples: claude-sonnet-4-6, llama3, mistral
"""

from __future__ import annotations

import os
from typing import Generator

from afidsvalidator.landmark_info import LANDMARK_INFO

# ── Ordered landmark list (matches FCSV / AFIDs protocol order) ───────────────
LANDMARK_ORDER: list[str] = list(LANDMARK_INFO.keys())

# ── System prompt ─────────────────────────────────────────────────────────────
_LANDMARK_BLOCK = "\n\n".join(
    f"**{abbrev} — {info['full_name']}**\n"
    f"Description: {info['description']}\n"
    f"Key features on MRI: {info['key_features']}\n"
    f"Common mistakes: {info['common_mistakes']}"
    for abbrev, info in LANDMARK_INFO.items()
)

SYSTEM_PROMPT = f"""You are an expert neuroanatomy tutor embedded inside the \
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
   - End with one practical tip to avoid the most common mistake listed in \
the protocol definition below.
   - Tone: encouraging, clear, expert but not condescending.

2. PLACEMENT FEEDBACK (when the user has placed a fiducial)
   You will receive: the placed coordinate (RAS mm), the reference coordinate \
(RAS mm), the Euclidean distance, quality, directional offset, AND the \
current viewer settings (zoom, resolution, contrast window).
   Steps:
   a) Open with a one-line verdict naming the distance \
(e.g. "Not quite — 17.3 mm off." or "Excellent — 0.8 mm!").
   b) Reason anatomically about what the user likely clicked instead, drawing \
on the landmark description and common_mistakes below.
   c) Use anatomical directions freely to orient them \
("too posterior", "slightly superior to the genu", etc.).
   d) VIEWER RECOMMENDATION — always check the viewer settings and advise \
the user specifically:
      • If zoom ≤ 1.5 and error > 3 mm → suggest zooming in ("+/− buttons \
or scroll) for better precision.
      • If resolution is 2mm and error > 4 mm → suggest switching to 1mm \
resolution (the RES button) to reveal finer anatomical detail.
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

GENERAL RULES:
- Use millimetres (mm) for distances when reporting accuracy scores.
- Anatomical directional language is encouraged ("too posterior", "slightly \
superior to that", "lateral to the midline") — this is how anatomy is taught.
- NEVER tell the user to "set the cursor to [x, y, z]" or give raw coordinate \
values as instructions. Teach anatomy and visual landmarks, not number lookup.
- Do not use excessive markdown — this renders in a simple chat pane.
- Never fabricate landmark positions. If unsure, say so.
- Be encouraging. Neuroanatomy is hard; normalise difficulty while \
maintaining precision.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AFIDs PROTOCOL — ALL 32 LANDMARK DEFINITIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{_LANDMARK_BLOCK}
"""


# ── Client factory ────────────────────────────────────────────────────────────
def _get_client():
    """Return an OpenAI-compatible client built from env vars."""
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "The 'openai' package is required for guided learning. "
            "Install it with:  poetry add openai"
        ) from exc

    return OpenAI(
        api_key=os.environ.get("LLM_API_KEY", ""),
        base_url=os.environ.get(
            "LLM_BASE_URL", "https://api.openai.com/v1"
        ),
    )


def _get_model() -> str:
    return os.environ.get("LLM_MODEL", "gpt-4o")


# ── Message builders ──────────────────────────────────────────────────────────
def build_intro_messages(abbrev: str) -> list[dict]:
    """Return the messages list that triggers a landmark introduction."""
    info = LANDMARK_INFO.get(abbrev, {})
    full_name = info.get("full_name", abbrev)
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Please introduce landmark {abbrev} ({full_name}). "
                f"Tell me what it is anatomically and how to find it on the "
                f"MNI152NLin2009cAsym T1w MRI in the viewer. "
                f"I will then click to place my marker."
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
) -> list[dict]:
    """Append a placement result to history and return the full messages list."""
    base = history if history else [{"role": "system", "content": SYSTEM_PROMPT}]

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
        if viewer_parts else ""
    )

    content = (
        f"I placed my fiducial for {abbrev} ({full_name})."
        f"{coord_str}\n"
        f"Distance from reference: {distance_mm:.1f} mm ({verdict})."
        f"{viewer_str}\n\n"
        f"Please give anatomical feedback and — based on the viewer settings "
        f"above — tell me whether I should adjust my zoom or switch to a "
        f"higher resolution to place this landmark more precisely."
    )
    return base + [{"role": "user", "content": content}]


def build_question_messages(
    history: list[dict],
    question: str,
) -> list[dict]:
    """Append a user question to history and return the full messages list."""
    base = history if history else [{"role": "system", "content": SYSTEM_PROMPT}]
    return base + [{"role": "user", "content": question}]


# ── Streaming ─────────────────────────────────────────────────────────────────
def stream_chat(messages: list[dict]) -> Generator[str, None, None]:
    """Yield text chunks from the LLM for the given messages."""
    # Always ensure the system prompt is first
    if not messages or messages[0].get("role") != "system":
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    client = _get_client()
    stream = client.chat.completions.create(
        model=_get_model(),
        messages=messages,
        stream=True,
        max_tokens=512,
        temperature=0.65,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content
