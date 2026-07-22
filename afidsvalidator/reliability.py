"""Per-landmark rater-reliability prior for the guided-learning tutor.

Loads ``rater_reliability.json`` — the distribution of trained-rater anatomical
fiducial localization error (AFLE) for each of the 32 AFIDs, computed from the
afids-data multi-rater release by ``compute_reliability.py`` — and exposes it in
three forms the tutor and validator use:

* :func:`percentile` — how precise a learner's placement is relative to the
  trained-rater distribution for that landmark, as a "you vs. the experts"
  metric where **higher is better** (e.g. 90 = more precise than 90% of trained
  raters);
* :func:`band` — a coarse, human-readable classification of that percentile;
* :func:`difficulty` and :func:`expected` — how hard the landmark is for humans,
  used to calibrate feedback ("1 mm on the AC is poor; 1 mm on the indusium
  griseum origin is expert-level").

Everything degrades gracefully to ``None`` when a landmark is absent from the
prior, so callers can fall back to the global fixed thresholds.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_JSON = Path(__file__).parent / "rater_reliability.json"

# Percentile anchors stored per landmark, plus the implicit (0 mm → 0th pct).
_ANCHORS = [
    (0.0, 0.0),
    ("p10", 10),
    ("p25", 25),
    ("p50", 50),
    ("p75", 75),
    ("p90", 90),
]


@lru_cache(maxsize=1)
def _data() -> dict:
    try:
        return json.loads(_JSON.read_text())
    except (OSError, ValueError):
        return {"global": {}, "landmarks": {}}


def stats(abbrev: str) -> dict | None:
    """Return the raw reliability record for *abbrev*, or None."""
    return _data().get("landmarks", {}).get(abbrev)


def expected(abbrev: str) -> tuple[float, float] | None:
    """Return (median, p75) trained-rater AFLE in mm for *abbrev*."""
    s = stats(abbrev)
    return (s["p50"], s["p75"]) if s else None


def difficulty(abbrev: str) -> str | None:
    """Coarse human-difficulty tier from the trained-rater median AFLE."""
    s = stats(abbrev)
    if not s:
        return None
    med = s["p50"]
    if med < 0.5:
        return "high-reliability"
    if med < 0.9:
        return "moderate"
    return "difficult"


def _error_percentile(abbrev: str, distance_mm: float) -> int | None:
    """Percentile of *distance_mm* within the trained-rater AFLE distribution.

    0 = better (more precise) than essentially all trained raters; 90+ = at or
    beyond the least precise trained-rater placements for this landmark. Linear
    interpolation between stored percentile anchors; extrapolated above p90.

    This is the raw error rank (lower = more precise). Callers should use the
    public :func:`percentile`, which inverts it into an intuitive precision
    percentile where higher = better.
    """
    s = stats(abbrev)
    if not s:
        return None
    pts = [(v if isinstance(v, float) else s[v], p) for v, p in _ANCHORS]
    for (x0, p0), (x1, p1) in zip(pts, pts[1:]):
        if distance_mm <= x1:
            if x1 == x0:
                return int(p1)
            frac = (distance_mm - x0) / (x1 - x0)
            return int(round(p0 + frac * (p1 - p0)))
    # above p90 → extrapolate toward 99
    p90 = s["p90"]
    over = (distance_mm - p90) / (p90 if p90 > 0 else 1.0)
    return int(min(99, round(90 + 9 * over)))


def percentile(abbrev: str, distance_mm: float) -> int | None:
    """Precision percentile of *distance_mm* vs. the trained-rater distribution.

    **Higher is better**: the percentage of trained-rater placements this
    learner is at least as precise as. 90 = more precise than 90% of trained
    raters (a tight placement); 10 = more precise than only 10% (a loose one).
    Inverts :func:`_error_percentile` so the number matches the everyday reading
    of "90th percentile = great." Clamped to 1..99.
    """
    ep = _error_percentile(abbrev, distance_mm)
    if ep is None:
        return None
    return max(1, min(99, 100 - ep))


_BAND_LABELS = {
    "expert": "better than the typical trained rater",
    "proficient": "within trained-rater range",
    "edge": "at the edge of trained-rater range",
    "outside": "outside trained-rater range",
}


def band(abbrev: str, distance_mm: float) -> dict | None:
    """Classify *distance_mm* against the trained-rater distribution.

    Returns ``{key, label, percentile, median, p75, p90, difficulty}`` or None.
    """
    s = stats(abbrev)
    if not s:
        return None
    if distance_mm <= s["p50"]:
        key = "expert"
    elif distance_mm <= s["p75"]:
        key = "proficient"
    elif distance_mm <= s["p90"]:
        key = "edge"
    else:
        key = "outside"
    return {
        "key": key,
        "label": _BAND_LABELS[key],
        "percentile": percentile(abbrev, distance_mm),
        "median": s["p50"],
        "p75": s["p75"],
        "p90": s["p90"],
        "difficulty": difficulty(abbrev),
    }


def feedback_line(abbrev: str, distance_mm: float) -> str | None:
    """One sentence of rater-calibrated context for the tutor's feedback prompt."""
    b = band(abbrev, distance_mm)
    if not b:
        return None
    return (
        f"Rater-calibration for {abbrev}: across trained raters in the AFIDs "
        f"multi-rater dataset, median placement error for this landmark is "
        f"{b['median']:.2f} mm (75th pct {b['p75']:.2f} mm, 90th pct "
        f"{b['p90']:.2f} mm); it is a {b['difficulty']} landmark. The learner's "
        f"{distance_mm:.1f} mm is {b['label']} — more precise than about "
        f"{b['percentile']}% of trained raters. "
        f"Use this to calibrate praise/correction to how hard this landmark "
        f"actually is — do not quote these raw numbers unless helpful."
    )


def intro_line(abbrev: str) -> str | None:
    """Difficulty context for the tutor's landmark introduction prompt."""
    s = stats(abbrev)
    if not s:
        return None
    d = difficulty(abbrev)
    return (
        f"Difficulty context for {abbrev}: trained raters place this landmark to "
        f"a median of {s['p50']:.2f} mm (a {d} landmark in the AFIDs multi-rater "
        f"dataset). If it is difficult, briefly set that expectation."
    )
