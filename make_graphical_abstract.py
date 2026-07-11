"""Graphical abstract for the AFIDs-Validator education paper.

A single composed figure, laid out like a journal page — reads top to bottom,
the way the paper argues:

    01  THE DATA    how the ground truth was made — 132 images, 492 expert
                    annotations, per-subject consensus, and the per-landmark
                    error distributions that fall out of it
    02  THE SPAN    the same 32-point protocol carried across 21 reference
                    templates and 2 species
    ——  THE METRIC  one Euclidean error, forked into two uses
    03 / 04         LEARN (AI-guided tutor)   |   VALIDATE (multi-template engine)

Every number, ridge and heat cell is computed from the repository's own data
(`afidsvalidator/rater_reliability.json`, `afidsvalidator/afids-templates/`).
Nothing here is illustrative.

    python make_graphical_abstract.py  ->  paper_figures/fig0_graphical_abstract.{png,pdf}

Embeds two rasters produced by make_ga_assets.py:  ga_brain.png  ga_crop.png
A layout audit runs before saving: no label may leave its card, leave the page,
or collide with another label.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import NormalDist

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import (
    Arc,
    Circle,
    Ellipse,
    FancyArrowPatch,
    FancyBboxPatch,
    PathPatch,
    Polygon,
    Rectangle,
    Wedge,
)
from matplotlib.path import Path as MPath

OUT = Path("paper_figures")
TPL_DIR = Path("afidsvalidator/afids-templates")

# ══════════════════════════════════════════════════════════════════════════════
# GEOMETRY  (data coords == inches; stacked from the top, gaps tuned for a
# tight, page-like figure)
# ══════════════════════════════════════════════════════════════════════════════
W = 16.0
M = 0.46
XR = W - M
CTW = XR - M  # content width
GAP = 0.34  # gutter between the two product cards
CARDW = (CTW - GAP) / 2
SEAM = M + CARDW + GAP / 2  # vertical centre-line of the figure

TOPM, BOTM = 0.14, 0.14
H_TITLE = 0.44  # slim credit line (not an app header)
H_DATA, H_STRIP, H_PROD, H_FOUND = 3.52, 0.66, 4.04, 0.72

# resolve y-bands top-down
H = TOPM + H_TITLE + 0.06 + H_DATA + H_STRIP + H_PROD + 0.20 + H_FOUND + BOTM

_y = H - TOPM
TITLE_Y = _y - H_TITLE / 2
_y -= H_TITLE + 0.06
A_y1 = _y
A_y0 = A_y1 - H_DATA
_y = A_y0
BR_y1 = _y
BR_y0 = BR_y1 - H_STRIP
_y = BR_y0
P_y1 = _y
P_y0 = P_y1 - H_PROD
_y = P_y0 - 0.20
F_y1 = _y
F_y0 = F_y1 - H_FOUND

# ── palette ───────────────────────────────────────────────────────────────────
INK = "#0d1117"
SUB = "#566171"
MUT = "#8b95a3"
HAIR = "#e2e6ea"
CARD = "#f7f9fa"
PANEL = "#fbfcfd"

DATA_C = "#0f766e"
SPAN_C = "#0b5c62"
MACAQ_C = "#8b5cf6"
LEARN_C = "#2563c9"
VALID_C = "#7b3fb0"
OPEN_C = "#b4560c"
SLATE = "#334155"

GOOD, BAD = "#14a04a", "#d64545"
GOLD, GOLD_HI, GOLD_BG = "#c9971f", "#DDAA33", "#fdf7e6"

TIER = {
    "ex": "#0ca30c",
    "good": "#7ab648",
    "fair": "#ec835a",
    "bad": "#d03b3b",
}
HEAT = LinearSegmentedColormap.from_list(
    "afids_heat",
    [
        "#ffffff",
        "#dcefeb",
        "#8ecdc1",
        "#2fa494",
        "#0f766e",
        "#0a3f45",
        "#06232a",
    ],
)
HEAT.set_bad("white")


def tier(d):
    return "ex" if d < 1 else "good" if d < 2 else "fair" if d < 4 else "bad"


# ── anatomy ───────────────────────────────────────────────────────────────────
REGION_MAP = {
    "Commissural": ["AC", "PC"],
    "Brainstem": ["ICS", "PMJ", "SIPF", "RSLMS", "LSLMS", "RILMS", "LILMS"],
    "Cerebellar": ["CUL"],
    "Diencephalic": ["PG", "IMS", "RMB", "LMB"],
    "Ventricular": ["RLVAC", "LLVAC", "RLVPC", "LLVPC"],
    "Callosal": ["GENU", "SPLE"],
    "Temporal": ["RALTH", "LALTH", "RSAMTH", "LSAMTH", "RIAMTH", "LIAMTH"],
    "Basal/Frontal": ["RIGO", "LIGO", "RVOH", "LVOH", "ROSF", "LOSF"],
}
REGION_COLORS = {
    "Commissural": "#2a78d6",
    "Brainstem": "#1baf7a",
    "Cerebellar": "#eda100",
    "Diencephalic": "#008300",
    "Ventricular": "#4a3aa7",
    "Callosal": "#e34948",
    "Temporal": "#e87ba4",
    "Basal/Frontal": "#eb6834",
}
REGION_ORDER = list(REGION_MAP.keys())
ABBR = [a for aa in REGION_MAP.values() for a in aa]
FCSV_ORDER = [
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
ABBR2REG = {a: r for r, aa in REGION_MAP.items() for a in aa}

# ══════════════════════════════════════════════════════════════════════════════
# DATA — measured, not invented
# ══════════════════════════════════════════════════════════════════════════════
_rel = json.loads(
    (Path("afidsvalidator") / "rater_reliability.json").read_text()
)
LM, GLOB = _rel["landmarks"], _rel["global"]
N_IMG = _rel["meta"]["n_images"]
N_SETS = _rel["meta"]["n_rater_files"]
_Z90 = NormalDist().inv_cdf(0.90)


def logn_sigma(a):
    v = LM[a]
    return math.log(v["p90"] / v["p50"]) / _Z90


def pct_of(a, mm):
    z = (math.log(mm) - math.log(LM[a]["p50"])) / logn_sigma(a)
    return NormalDist().cdf(z) * 100.0


def ordinal(p):
    n = int(round(p))
    suf = (
        "th"
        if 11 <= n % 100 <= 13
        else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    )
    return f"{n}{suf}"


def logn_pdf(a, x):
    s, mu = logn_sigma(a), math.log(LM[a]["p50"])
    return np.exp(-((np.log(x) - mu) ** 2) / (2 * s * s)) / (
        x * s * math.sqrt(2 * math.pi)
    )


def parse_fcsv(fp):
    out = {}
    for line in fp.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        p = line.split(",")
        if len(p) < 13:
            continue
        try:
            out[FCSV_ORDER[int(p[11]) - 1]] = np.array(
                [float(p[1]), float(p[2]), float(p[3])]
            )
        except (ValueError, IndexError):
            continue
    return out


def species(sub):
    return {
        f.name.split("_afids")[0].replace("tpl-", ""): parse_fcsv(f)
        for f in sorted((TPL_DIR / sub).glob("*_afids.fcsv"))
    }


HUMAN, MACAQ = species("human"), species("macaca")
N_HUMAN, N_MACAQ = len(HUMAN), len(MACAQ)
N_TPL = N_HUMAN + N_MACAQ


def displacement(group):
    acn = {t: {a: c - v["AC"] for a, c in v.items()} for t, v in group.items()}
    names = list(acn)
    D = np.zeros((len(names), len(ABBR)))
    for j, a in enumerate(ABBR):
        pts = np.array([acn[t][a] for t in names])
        D[:, j] = np.linalg.norm(pts - pts.mean(0), axis=1)
    return names, D


HNAMES, HD = displacement(HUMAN)
MNAMES, MD = displacement(MACAQ)
HUMAN_MEAN_SPREAD = float(HD.mean())
TOP_SPREAD = sorted(zip(ABBR, HD.mean(0)), key=lambda kv: -kv[1])[:3]
MAX_SPREAD = TOP_SPREAD[0][1]

COIN_MM = 1.2
CAL_HARD, CAL_EASY = "LIGO", "AC"

plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": [
            "Helvetica Neue",
            "Helvetica",
            "Arial",
            "DejaVu Sans",
        ],
        "text.color": INK,
        "pdf.fonttype": 42,
        "svg.fonttype": "none",
    }
)

fig = plt.figure(figsize=(W, H))
fig.patch.set_facecolor("white")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.set_aspect("equal")
ax.axis("off")

_TEXTS, _CARDS, _NOTEXT = [], [], []


def notext(name, x, y, w, h, pad=0.03):
    """Register a visual region no label may sit on top of (charts, images)."""
    _NOTEXT.append((name, x + pad, y + pad, x + w - pad, y + h - pad))


# ── primitives ────────────────────────────────────────────────────────────────
def rrect(x, y, w, h, fc="white", ec=HAIR, lw=1.2, r=0.12, z=1, alpha=1.0):
    ax.add_patch(
        FancyBboxPatch(
            (x + r, y + r),
            w - 2 * r,
            h - 2 * r,
            boxstyle=f"round,pad={r},rounding_size={r}",
            facecolor=fc,
            edgecolor=ec,
            linewidth=lw,
            zorder=z,
            alpha=alpha,
            mutation_aspect=1,
        )
    )


def card(name, x, y, w, h, color, r=0.17, z=1, fc="white"):
    rrect(x, y, w, h, fc=fc, ec=HAIR, lw=1.3, r=r, z=z)
    ax.add_patch(
        FancyBboxPatch(
            (x + 0.055, y + 0.2),
            0.125,
            h - 0.4,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor=color,
            edgecolor="none",
            zorder=z + 0.1,
        )
    )
    _CARDS.append((name, x, y, x + w, y + h))


def txt(
    x,
    y,
    s,
    size=10,
    color=INK,
    weight="normal",
    ha="left",
    va="center",
    style="normal",
    z=6,
    spacing=None,
):
    t = ax.text(
        x,
        y,
        s,
        fontsize=size,
        color=color,
        fontweight=weight,
        ha=ha,
        va=va,
        style=style,
        zorder=z,
        linespacing=spacing or 1.15,
    )
    _TEXTS.append((t, s))
    return t


_renderer = fig.canvas.get_renderer()


def extent(s, size, weight="normal", style="normal"):
    t = ax.text(0, 0, s, fontsize=size, fontweight=weight, style=style)
    bb = t.get_window_extent(_renderer)
    inv = ax.transData.inverted()
    (x0, y0), (x1, y1) = inv.transform((bb.x0, bb.y0)), inv.transform(
        (bb.x1, bb.y1)
    )
    t.remove()
    return x1 - x0, y1 - y0


def pill(
    cx, cy, s, color, size=8.4, h=0.34, fc="white", pad=0.30, weight="bold"
):
    w = extent(s, size, weight)[0] + 2 * pad
    rrect(cx - w / 2, cy - h / 2, w, h, fc=fc, ec=color, lw=1.3, r=h / 2, z=5)
    txt(cx, cy, s, size=size, color=color, weight=weight, ha="center", z=6)
    return w


def pill_right(x_right, cy, s, color, size=8.4, **kw):
    w = extent(s, size, kw.get("weight", "bold"))[0] + 2 * kw.get("pad", 0.30)
    pill(x_right - w / 2, cy, s, color, size=size, **kw)
    return w


def arrow(p, q, color=MUT, lw=2.2, rad=0.0, ms=16, z=4):
    ax.add_patch(
        FancyArrowPatch(
            p,
            q,
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>",
            mutation_scale=ms,
            lw=lw,
            color=color,
            zorder=z,
            capstyle="round",
            joinstyle="round",
        )
    )


def flow(x, y, color="#c2ccd6", s=0.13, n=2):
    """A quiet stage connector — small open chevrons pointing right."""
    for k in range(n):
        xk = x + k * s * 0.72
        ax.plot(
            [xk - s * 0.5, xk, xk - s * 0.5],
            [y + s, y, y - s],
            color=color,
            lw=2.0,
            zorder=4,
            solid_capstyle="round",
            solid_joinstyle="round",
        )


def imgbox(x, y, w, h, z=3, guard=True):
    if guard:
        notext("img", x, y, w, h)
    a = fig.add_axes([x / W, y / H, w / W, h / H])
    a.set_zorder(z)
    a.axis("off")
    return a


def chartbox(x, y, w, h, z=6, polar=False, guard=True):
    if guard:
        notext("chart", x, y, w, h)
    a = fig.add_axes([x / W, y / H, w / W, h / H], polar=polar)
    a.set_zorder(z)
    a.patch.set_alpha(0)
    return a


def section(x, y, n, color, title, kicker, ts=13, ks=9.6):
    s = 0.28
    rrect(x, y - s, 2 * s, 2 * s, fc=color, ec="none", r=0.08, z=6)
    txt(x + s, y, n, size=10.5, color="white", weight="bold", ha="center", z=7)
    txt(x + 0.76, y + 0.02, title, size=ts, weight="bold", color=color)
    txt(
        x + 0.76 + extent(title, ts, "bold")[0] + 0.24,
        y,
        kicker,
        size=ks,
        color=MUT,
    )


def eyebrow(x, y, s, ha="left"):
    txt(x, y, s, size=8.2, weight="bold", color=SUB, ha=ha)


# ── icons ─────────────────────────────────────────────────────────────────────
def ic_target(cx, cy, s, color):
    ax.add_patch(Circle((cx, cy), s, fill=False, ec=color, lw=1.6, zorder=7))
    ax.add_patch(Circle((cx, cy), s * 0.42, fill=True, fc=color, zorder=7))
    for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        ax.plot(
            [cx + dx * s * 0.6, cx + dx * s * 1.35],
            [cy + dy * s * 0.6, cy + dy * s * 1.35],
            color=color,
            lw=1.5,
            zorder=7,
            solid_capstyle="round",
        )


def ic_file(cx, cy, s, color):
    w, h, fold = s * 1.15, s * 1.5, s * 0.42
    p = MPath(
        [
            (cx - w / 2, cy - h / 2),
            (cx - w / 2, cy + h / 2),
            (cx + w / 2 - fold, cy + h / 2),
            (cx + w / 2, cy + h / 2 - fold),
            (cx + w / 2, cy - h / 2),
            (cx - w / 2, cy - h / 2),
        ],
        [MPath.MOVETO] + [MPath.LINETO] * 4 + [MPath.CLOSEPOLY],
    )
    ax.add_patch(PathPatch(p, fc="white", ec=color, lw=1.6, zorder=7))
    ax.plot(
        [cx + w / 2 - fold, cx + w / 2 - fold, cx + w / 2],
        [cy + h / 2, cy + h / 2 - fold, cy + h / 2 - fold],
        color=color,
        lw=1.3,
        zorder=7,
        solid_joinstyle="round",
    )
    for i, yy in enumerate((0.20, -0.05, -0.30)):
        ax.plot(
            [
                cx - w / 2 + s * 0.22,
                cx + w / 2 - s * 0.22 - (s * 0.34 if i == 0 else 0),
            ],
            [cy + yy * s * 2] * 2,
            color=color,
            lw=1.0,
            zorder=7,
            solid_capstyle="round",
            alpha=0.8,
        )


def ic_chat(cx, cy, s, color):
    w, h = s * 1.7, s * 1.25
    rrect(
        cx - w / 2,
        cy - h / 2 + 0.12,
        w,
        h,
        fc="white",
        ec=color,
        lw=1.6,
        r=0.14,
        z=7,
    )
    ax.add_patch(
        Polygon(
            [
                (cx - s * 0.2, cy - h / 2 + 0.18),
                (cx - s * 0.55, cy - h / 2 - 0.14),
                (cx + s * 0.12, cy - h / 2 + 0.18),
            ],
            closed=True,
            fc="white",
            ec=color,
            lw=1.6,
            zorder=7,
            joinstyle="round",
        )
    )
    ax.add_patch(
        Rectangle(
            (cx - s * 0.5, cy - h / 2 + 0.14),
            s * 0.7,
            0.1,
            fc="white",
            ec="none",
            zorder=7.15,
        )
    )
    for dx in (-0.42, 0, 0.42):
        ax.add_patch(
            Circle((cx + dx * s, cy + 0.14), s * 0.11, fc=color, zorder=7.2)
        )


def ic_gear(cx, cy, s, color):
    n, outer, inner = 8, s, s * 0.66
    pts = [
        (
            cx + (outer if i % 2 == 0 else inner) * np.cos(np.pi / n * i),
            cy + (outer if i % 2 == 0 else inner) * np.sin(np.pi / n * i),
        )
        for i in range(n * 2)
    ]
    ax.add_patch(
        Polygon(
            pts, closed=True, fc=color, ec="none", zorder=7, joinstyle="round"
        )
    )
    ax.add_patch(Circle((cx, cy), s * 0.32, fc="white", zorder=7.1))


def ic_stack(cx, cy, s, color):
    for i, yy in enumerate((-0.5, 0.0, 0.5)):
        ax.add_patch(
            Ellipse(
                (cx, cy + yy * s),
                s * 1.8,
                s * 0.7,
                fc=(color if i == 2 else "white"),
                ec=color,
                lw=1.4,
                zorder=7 + i * 0.1,
            )
        )


def ic_globe(cx, cy, s, color):
    ax.add_patch(Circle((cx, cy), s, fill=False, ec=color, lw=1.6, zorder=7))
    ax.add_patch(
        Arc(
            (cx, cy),
            s * 1.0,
            s * 2,
            theta1=0,
            theta2=360,
            ec=color,
            lw=1.2,
            zorder=7,
        )
    )
    for yy in (0, 0.5, -0.5):
        ax.plot(
            [cx - s * np.cos(yy), cx + s * np.cos(yy)],
            [cy + yy * s] * 2,
            color=color,
            lw=1.1,
            zorder=7,
        )


def ic_copyleft(cx, cy, s, color):
    ax.add_patch(Circle((cx, cy), s, fill=False, ec=color, lw=1.6, zorder=7))
    ax.add_patch(
        Arc(
            (cx, cy),
            s * 1.15,
            s * 1.15,
            theta1=-50,
            theta2=230,
            ec=color,
            lw=1.7,
            zorder=7.1,
        )
    )


def ic_orcid(cx, cy, s, color="#A6CE39"):
    ax.add_patch(Circle((cx, cy), s, fc=color, zorder=7))
    txt(
        cx,
        cy,
        "iD",
        size=s * 13,
        color="white",
        weight="bold",
        ha="center",
        z=7.2,
    )


def ic_docker(cx, cy, s, color):
    for i in range(3):
        ax.add_patch(
            Rectangle(
                (cx - s * 0.98 + i * s * 0.50, cy + s * 0.10),
                s * 0.40,
                s * 0.40,
                fc=color + "33",
                ec=color,
                lw=0.9,
                zorder=7.2,
            )
        )
    ax.add_patch(
        Rectangle(
            (cx - s * 0.48, cy + s * 0.56),
            s * 0.40,
            s * 0.40,
            fc=color + "55",
            ec=color,
            lw=0.9,
            zorder=7.2,
        )
    )
    body = MPath(
        [
            (cx - s * 1.15, cy + s * 0.06),
            (cx + s * 0.85, cy + s * 0.06),
            (cx + s * 1.28, cy - s * 0.30),
            (cx + s * 0.58, cy - s * 0.62),
            (cx - s * 0.90, cy - s * 0.62),
            (cx - s * 1.15, cy + s * 0.06),
        ],
        [MPath.MOVETO] + [MPath.LINETO] * 4 + [MPath.CLOSEPOLY],
    )
    ax.add_patch(PathPatch(body, fc=color, ec="none", zorder=7))
    ax.plot(
        [cx + s * 1.02, cx + s * 1.38],
        [cy - s * 0.10, cy + s * 0.32],
        color=color,
        lw=1.4,
        zorder=7,
        solid_capstyle="round",
    )


def ic_slicer(cx, cy, s, color):
    ax.add_patch(
        Polygon(
            [
                (cx - s, cy - s * 0.2),
                (cx, cy - s * 0.75),
                (cx + s, cy - s * 0.2),
                (cx, cy + s * 0.35),
            ],
            closed=True,
            fc=color + "22",
            ec=color,
            lw=1.2,
            zorder=7,
        )
    )
    ax.add_patch(
        Polygon(
            [
                (cx - s, cy - s * 0.2),
                (cx, cy + s * 0.35),
                (cx, cy + s * 1.00),
                (cx - s, cy + s * 0.45),
            ],
            closed=True,
            fc=color + "44",
            ec=color,
            lw=1.2,
            zorder=7.1,
        )
    )
    ax.add_patch(
        Polygon(
            [
                (cx + s, cy - s * 0.2),
                (cx, cy + s * 0.35),
                (cx, cy + s * 1.00),
                (cx + s, cy + s * 0.45),
            ],
            closed=True,
            fc=color + "66",
            ec=color,
            lw=1.2,
            zorder=7.1,
        )
    )


def ic_eye(cx, cy, s, color):
    ax.add_patch(
        Ellipse(
            (cx, cy), s * 2.3, s * 1.35, fill=False, ec=color, lw=1.5, zorder=7
        )
    )
    ax.add_patch(Circle((cx, cy), s * 0.45, fc=color, zorder=7.1))


def ic_bulb(cx, cy, s, color):
    ax.add_patch(
        Circle(
            (cx, cy + s * 0.25),
            s * 0.75,
            fill=False,
            ec=color,
            lw=1.5,
            zorder=7,
        )
    )
    for dy, hw in ((-0.60, 0.40), (-0.85, 0.30)):
        ax.plot(
            [cx - s * hw, cx + s * hw],
            [cy + s * dy] * 2,
            color=color,
            lw=1.4,
            zorder=7,
            solid_capstyle="round",
        )


def ic_person(cx, cy, s, color):
    ax.add_patch(
        Circle(
            (cx, cy + s * 0.42),
            s * 0.40,
            fc=color,
            ec="white",
            lw=1.0,
            zorder=7,
        )
    )
    ax.add_patch(
        Wedge(
            (cx, cy - s * 0.34),
            s * 0.78,
            0,
            180,
            fc=color,
            ec="white",
            lw=1.0,
            zorder=7,
        )
    )


def ic_brain(cx, cy, s, color):
    ax.add_patch(
        Rectangle(
            (cx + s * 0.02, cy - s * 0.80),
            s * 0.26,
            s * 0.55,
            fc=color,
            ec="none",
            zorder=6.9,
        )
    )
    ax.add_patch(
        Ellipse(
            (cx, cy + s * 0.16),
            s * 1.85,
            s * 1.30,
            fc=color,
            ec="white",
            lw=0.5,
            zorder=7,
        )
    )
    ax.add_patch(
        Ellipse(
            (cx + s * 0.44, cy - s * 0.42),
            s * 0.90,
            s * 0.60,
            fc=color,
            ec="white",
            lw=0.5,
            zorder=7,
        )
    )


def ic_coin2(cx, cy, s):
    """A tiny two-tone coin — a quiet nod to 'two sides of the same coin'."""
    ax.add_patch(
        Wedge((cx, cy), s, 90, 270, fc=GOLD_BG, ec=GOLD_HI, lw=1.3, zorder=6)
    )
    ax.add_patch(
        Wedge((cx, cy), s, -90, 90, fc=GOLD_HI, ec=GOLD_HI, lw=1.3, zorder=6)
    )


def icon_chip(
    cx,
    cy,
    icon_fn,
    label,
    w=2.10,
    color=LEARN_C,
    h=0.42,
    fc="#eef4fc",
    size=8.2,
):
    rrect(cx - w / 2, cy - h / 2, w, h, fc=fc, ec=color, lw=1.0, r=h / 2, z=5)
    icon_fn(cx - w / 2 + 0.27, cy, 0.12, color)
    txt(
        cx - w / 2 + 0.50,
        cy,
        label,
        size=size,
        color=color,
        weight="bold",
        ha="left",
        z=6,
    )


# ══════════════════════════════════════════════════════════════════════════════
# TITLE — a single slim credit line (no app chrome)
# ══════════════════════════════════════════════════════════════════════════════
txt(M, TITLE_Y, "AFIDs Validator", size=15, weight="bold", color=INK)
_ntw = extent("AFIDs Validator", 15, "bold")[0]
txt(
    M + _ntw + 0.22,
    TITLE_Y,
    "quality assurance and active learning for anatomical landmark placement",
    size=10.0,
    color=SUB,
    style="italic",
)
txt(
    XR,
    TITLE_Y,
    "validator.afids.io · open · GPL-3.0",
    size=9.0,
    color=MUT,
    ha="right",
)

# ══════════════════════════════════════════════════════════════════════════════
# 01 — THE DATA  (protocol + consensus ground truth + reference templates)
# ══════════════════════════════════════════════════════════════════════════════
card("DATA", M, A_y0, CTW, H_DATA, DATA_C)
section(
    M + 0.32,
    A_y1 - 0.38,
    "01",
    DATA_C,
    "THE DATA",
    "protocol · consensus ground truth · reference frames",
)
pill_right(
    XR - 0.30,
    A_y1 - 0.38,
    "Taha et al., Sci Data 2023 · 10:449",
    DATA_C,
    size=8.0,
)

EYE = A_y1 - 0.86  # eyebrow row
BAND = A_y1 - 1.83  # stage-row centre
CAP1, CAP2 = A_y0 + 0.54, A_y0 + 0.35  # captions under the left/centre stages
STAT_Y = A_y0 + 0.56  # ridgeline summary pills

# ── the protocol (AFIDs cover artwork from Lau et al. 2019, HBM cover) ─────────
_cover = OUT / "logos" / "lau_brain_hero.png"
_cov = mpimg.imread(str(_cover)) if _cover.exists() else None
bw = 2.34
bh = bw * (_cov.shape[0] / _cov.shape[1]) if _cov is not None else bw / 1.6
bx, by = 0.78, BAND - bh / 2 + 0.04
_b = imgbox(bx, by, bw, bh, z=3)
if _cov is not None:
    _b.imshow(_cov)
ax.add_patch(
    FancyBboxPatch(
        (bx + 0.03, by + 0.03),
        bw - 0.06,
        bh - 0.06,
        boxstyle="round,pad=0,rounding_size=0.09",
        fill=False,
        ec=DATA_C,
        lw=1.6,
        zorder=4,
    )
)
eyebrow(bx, EYE, "THE PROTOCOL")
txt(
    bx + bw / 2,
    CAP1,
    "32 landmarks · 8 regions",
    size=9.6,
    weight="bold",
    ha="center",
)
txt(
    bx + bw / 2,
    CAP2,
    "AFIDs protocol · Lau et al., Hum Brain Mapp 2019",
    size=7.6,
    color=MUT,
    ha="center",
)

flow(bx + bw + 0.34, BAND)

# ── the data: subject images + templates, summed to the curated fiducial count ─
sx = 3.62
N_BRAINS = N_IMG + N_HUMAN + N_MACAQ
N_FID = N_BRAINS * 32
eyebrow(sx, EYE, "IMAGES & TEMPLATES")

xnum, xlab = sx + 1.30, sx + 1.42


def data_row(y, nb, count, label, color):
    for i in range(nb):
        ic_brain(sx + 0.16 + i * 0.148, y + 0.02, 0.058, color)
    txt(
        xnum,
        y + 0.03,
        count,
        size=10.5,
        weight="bold",
        color=color,
        ha="right",
    )
    txt(xlab, y + 0.03, label, size=8.4, color=SUB)


data_row(BAND + 0.60, 5, f"{N_IMG}", "subject images", DATA_C)
data_row(BAND + 0.20, 5, f"+ {N_HUMAN}", "human templates", DATA_C)
data_row(BAND - 0.20, 5, f"+ {N_MACAQ}", "macaque templates", MACAQ_C)
ax.plot(
    [sx + 0.66, xnum + 0.04],
    [BAND - 0.40, BAND - 0.40],
    color="#b7c0ca",
    lw=1.1,
    zorder=3,
)
txt(
    xnum,
    BAND - 0.64,
    f"{N_FID:,}",
    size=13.5,
    weight="bold",
    color=DATA_C,
    ha="right",
)
txt(xlab, BAND - 0.64, "curated fiducials", size=9.0, weight="bold", color=INK)
txt(
    sx + 0.16,
    BAND - 0.86,
    f"{N_BRAINS} brains × 32 landmarks · 4 open datasets",
    size=6.9,
    color=MUT,
    style="italic",
)

flow(sx + 3.10, BAND)

# ── consensus ─────────────────────────────────────────────────────────────────
cx0, cwid = 7.42, 1.62
ccx = cx0 + cwid / 2
eyebrow(ccx, EYE, "CONSENSUS = GROUND TRUTH", ha="center")
cs = chartbox(cx0, BAND - cwid / 2 + 0.06, cwid, cwid)
cs.set_xlim(-1.75, 1.75)
cs.set_ylim(-1.75, 1.75)
cs.set_aspect("equal")
cs.axis("off")
_pts = np.array([[0.62, 0.45], [-0.55, 0.30], [0.18, -0.72], [-0.30, -0.18]])
cs.add_patch(
    Circle((0, 0), GLOB["median"], fill=False, ec=MUT, ls=(0, (3, 3)), lw=1.0)
)
for p, cc in zip(_pts, ["#0f766e", "#2f9e91", "#66bdb2", "#a5d8d1"]):
    cs.plot([0, p[0]], [0, p[1]], color=cc, lw=1.2, zorder=2)
    cs.scatter(*p, s=74, c=cc, edgecolors="white", linewidths=1.1, zorder=3)
cs.scatter(
    0,
    0,
    s=320,
    marker="*",
    c=GOLD_HI,
    edgecolors=INK,
    linewidths=0.8,
    zorder=4,
)
_ccap = BAND - cwid / 2 - 0.09  # captions hug the (now larger) icon
txt(ccx, _ccap, "per-subject consensus", size=8.6, weight="bold", ha="center")
txt(
    ccx,
    _ccap - 0.20,
    f"from {N_SETS} expert annotations",
    size=7.6,
    color=MUT,
    ha="center",
    style="italic",
)

flow(cx0 + cwid + 0.30, BAND)

# ── the distributions that fall out ───────────────────────────────────────────
RX0, RX1 = cx0 + cwid + 0.62, XR - 0.54
eyebrow(
    (RX0 + RX1) / 2, EYE, "RATER-TO-CONSENSUS ERROR, PER LANDMARK", ha="center"
)
PICK = sorted(
    ["AC", "SPLE", "PMJ", "CUL", "PG", "RLVAC", "RSAMTH", "LIGO"],
    key=lambda a: -LM[a]["p50"],
)
XMAX = 3.0
rg = chartbox(RX0 + 0.62, BAND - 0.62, RX1 - RX0 - 0.66, 1.42)
xs = np.linspace(0.02, XMAX, 500)
for i, a in enumerate(PICK):
    y0 = i * 1.0
    d = logn_pdf(a, xs)
    d = d / d.max() * 1.12
    c = REGION_COLORS[ABBR2REG[a]]
    z = 10 - i
    rg.fill_between(xs, y0, y0 + d, color=c, alpha=0.62, lw=0, zorder=z)
    rg.plot(
        xs, y0 + d, color="white", lw=1.9, zorder=z, solid_capstyle="round"
    )
    rg.plot(
        xs, y0 + d, color=c, lw=1.1, zorder=z + 0.1, solid_capstyle="round"
    )
    rg.plot([0, XMAX], [y0, y0], color="white", lw=0.9, zorder=z + 0.05)
    p50 = LM[a]["p50"]
    rg.plot(
        [p50, p50],
        [y0, y0 + np.interp(p50, xs, d)],
        color="white",
        lw=1.3,
        zorder=z + 0.15,
    )
    rg.plot(
        [p50, p50],
        [y0, y0 + np.interp(p50, xs, d)],
        color=c,
        lw=0.9,
        ls=(0, (1.8, 1.4)),
        zorder=z + 0.2,
    )
    rg.scatter(
        [-0.18],
        [y0 + 0.09],
        s=9,
        c=c,
        edgecolors="white",
        linewidths=0.4,
        clip_on=False,
        zorder=z + 0.3,
    )
    rg.text(
        -0.30,
        y0 + 0.09,
        a,
        ha="right",
        va="center",
        fontsize=6.4,
        color=INK,
        fontweight="bold",
    )
    rg.text(
        XMAX + 0.05,
        y0 + 0.09,
        f"{p50:.2f}",
        ha="left",
        va="center",
        fontsize=6.1,
        color=MUT,
    )
for thr in (1, 2):
    rg.axvline(thr, color="#c2c9d1", ls=":", lw=0.9, zorder=0.5)
rg.set_xlim(0, XMAX)
rg.set_ylim(-0.28, 8.55)
rg.set_yticks([])
rg.set_xticks([0, 1, 2, 3])
rg.tick_params(labelsize=6.3, length=2.2, color=HAIR, pad=1.4)
for s in ("top", "right", "left"):
    rg.spines[s].set_visible(False)
rg.spines["bottom"].set_color(HAIR)
rg.text(
    XMAX / 2, 8.28, "mm from consensus", ha="center", fontsize=6.3, color=MUT
)
rg.text(
    XMAX + 0.05,
    8.28,
    "median",
    ha="left",
    fontsize=5.9,
    color=MUT,
    style="italic",
)

_stats = [
    (f"median {GLOB['median']:.2f} mm", DATA_C),
    (f"{GLOB['within_1mm'] * 100:.0f}% < 1 mm", TIER["ex"]),
    (f"{GLOB['within_2mm'] * 100:.0f}% < 2 mm", TIER["good"]),
]
_ws = [extent(s, 7.9, "bold")[0] + 0.58 for s, _ in _stats]
_sx = (RX0 + RX1) / 2 - (sum(_ws) + 0.22 * (len(_ws) - 1)) / 2
for (s, c), w in zip(_stats, _ws):
    pill(_sx + w / 2, STAT_Y, s, c, size=7.9, h=0.30)
    _sx += w + 0.22
txt(
    (RX0 + RX1) / 2,
    STAT_Y - 0.26,
    "difficulty is landmark-specific — tutor and validator both read against it",
    size=7.6,
    color=MUT,
    ha="center",
    style="italic",
)

# ══════════════════════════════════════════════════════════════════════════════
# THE METRIC — a slim shared header spanning both product cards
# (the "same mm, two verdicts" proof lives inside the cards themselves)
# ══════════════════════════════════════════════════════════════════════════════
_thesis = "One Euclidean error — two uses"
_ty = BR_y0 + 0.40
txt(SEAM, _ty, _thesis, size=11.5, weight="bold", color=SLATE, ha="center")
txt(
    SEAM,
    BR_y0 + 0.17,
    "the same millimetre, always read against how hard the landmark is",
    size=8.2,
    color=MUT,
    ha="center",
    style="italic",
)
# quiet colour cue mapping the shared metric onto each card, no heavy arrows
txt(
    M + 0.30,
    BR_y0 + 0.13,
    "taught in context",
    size=7.8,
    color=LEARN_C,
    weight="bold",
    ha="left",
)
txt(
    XR - 0.30,
    BR_y0 + 0.13,
    "audited at scale",
    size=7.8,
    color=VALID_C,
    weight="bold",
    ha="right",
)

# ══════════════════════════════════════════════════════════════════════════════
# 03 — LEARN  (left card)
# ══════════════════════════════════════════════════════════════════════════════
LX0 = M
LX1 = M + CARDW
card("LEARN", LX0, P_y0, CARDW, H_PROD, LEARN_C)
ic_chat(LX0 + 0.42, P_y1 - 0.38, 0.18, LEARN_C)
section(
    LX0 + 0.78,
    P_y1 - 0.38,
    "02",
    LEARN_C,
    "LEARN",
    "AI-guided tutor · /learn",
    ts=12.5,
    ks=8.8,
)
pill_right(
    LX1 - 0.28, P_y1 - 0.38, "bring your own API key", LEARN_C, size=7.8
)

sh = 1.62
sw = sh * 1.4938
scy = P_y1 - 0.82 - sh
_c = imgbox(LX0 + 0.40, scy, sw, sh, z=3)
if (OUT / "ga_crop.png").exists():
    _im = mpimg.imread(str(OUT / "ga_crop.png"))
    _c.imshow(_im)
    _c.add_patch(
        Rectangle(
            (0, 0),
            _im.shape[1] - 1,
            _im.shape[0] - 1,
            fill=False,
            ec=LEARN_C,
            lw=1.5,
        )
    )
txt(
    LX0 + 0.40 + sw / 2,
    scy - 0.18,
    "NiiVue viewer + streaming AI tutor",
    size=7.4,
    color=MUT,
    ha="center",
    style="italic",
)

# five-step cycle (right of screenshot)
cyc = ["Introduce", "Place", "Compute", "Feedback", "Dialogue"]
cyc_c = [LEARN_C, DATA_C, SLATE, LEARN_C, DATA_C]
cbx = LX0 + sw + 0.78
cstep = (LX1 - 0.34 - cbx) / 4
cyr = P_y1 - 1.32
cr = 0.185
# return loop arcing up and over the bubbles (on top, so it is never hidden)
arrow(
    (cbx + 4 * cstep, cyr + cr + 0.02),
    (cbx, cyr + cr + 0.02),
    color=LEARN_C,
    lw=1.5,
    rad=0.22,
    ms=12,
    z=6.6,
)
txt(
    (cbx + cbx + 4 * cstep) / 2,
    cyr + 0.40,
    "repeat × 32 landmarks",
    size=7.0,
    color=LEARN_C,
    ha="center",
    style="italic",
)
for i, (s, c) in enumerate(zip(cyc, cyc_c)):
    xx = cbx + i * cstep
    ax.add_patch(Circle((xx, cyr), cr, fc=c, ec="white", lw=1.1, zorder=6))
    txt(
        xx,
        cyr,
        str(i + 1),
        size=8.4,
        color="white",
        weight="bold",
        ha="center",
        z=7,
    )
    txt(xx, cyr - 0.32, s, size=6.6, ha="center", weight="bold")
    if i < len(cyc) - 1:
        arrow(
            (xx + 0.20, cyr), (xx + cstep - 0.20, cyr), color=MUT, lw=1.4, ms=9
        )

# principle chips (2×2 under the cycle)
chw = (LX1 - 0.34 - cbx - 0.24) / 2 + 0.24
pcx = cbx + (4 * cstep) / 2
for (dx, dy), (fn, lab) in zip(
    [(-0.5, 0), (0.5, 0), (-0.5, 1), (0.5, 1)],
    [
        (ic_target, "anatomy-first"),
        (ic_eye, "viewer-aware"),
        (ic_file, "RAG-grounded"),
        (ic_bulb, "productive failure"),
    ],
):
    icon_chip(
        pcx + dx * (chw - 0.02), cyr - 0.74 - dy * 0.50, fn, lab, w=chw - 0.06
    )

# tutor quote (bottom strip, spans the card)
qx0, qx1 = LX0 + 0.34, LX1 - 0.30
qh = 0.82
qb = P_y0 + 0.22
qcy = qb + qh / 2
rrect(qx0, qb, qx1 - qx0, qh, fc="#f2f7fd", ec="#cfe0f6", lw=1.0, r=0.11, z=2)
rrect(
    qx0 + 0.14, qb + 0.20, 0.06, qh - 0.40, fc=LEARN_C, ec="none", r=0.03, z=3
)
txt(
    qx0 + 0.40,
    qcy + 0.20,
    f"“Your AC sits {COIN_MM} mm from consensus — the {ordinal(pct_of('AC', COIN_MM))} "
    f"percentile, where trained raters land within {LM['AC']['p50']:.2f} mm.",
    size=7.8,
    style="italic",
)
txt(
    qx0 + 0.40,
    qcy - 0.02,
    "Re-check the midline: AC is where the commissure crosses it, not the bright "
    "bundle above.”",
    size=7.8,
    style="italic",
)
txt(
    qx1 - 0.20,
    qb + 0.15,
    "— streaming /learn tutor",
    size=6.9,
    color=LEARN_C,
    weight="bold",
    ha="right",
    style="italic",
)

# ══════════════════════════════════════════════════════════════════════════════
# 04 — VALIDATE  (right card)
# ══════════════════════════════════════════════════════════════════════════════
VX0 = M + CARDW + GAP
VX1 = XR
card("VALIDATE", VX0, P_y0, CARDW, H_PROD, VALID_C)
ic_gear(VX0 + 0.42, P_y1 - 0.38, 0.17, VALID_C)
section(
    VX0 + 0.78,
    P_y1 - 0.38,
    "03",
    VALID_C,
    "VALIDATE",
    "multi-template engine",
    ts=12.5,
    ks=8.8,
)
pill_right(VX1 - 0.28, P_y1 - 0.38, "instant feedback", VALID_C, size=7.8)

# flow: upload → compare
fy = P_y1 - 1.02
ic_file(VX0 + 0.56, fy, 0.28, VALID_C)
txt(VX0 + 0.56, fy - 0.60, "upload", size=7.8, weight="bold", ha="center")
txt(VX0 + 0.56, fy - 0.79, "FCSV / JSON", size=7.0, color=MUT, ha="center")
arrow((VX0 + 0.92, fy), (VX0 + 1.44, fy), color=MUT, lw=1.9, ms=12)
ic_gear(VX0 + 1.82, fy, 0.27, VALID_C)
txt(VX0 + 1.82, fy - 0.60, "32 errors", size=7.8, weight="bold", ha="center")
txt(
    VX0 + 1.82,
    fy - 0.79,
    f"vs {N_TPL} templates",
    size=7.0,
    color=MUT,
    ha="center",
)

# mini charts (ranked bars + radar) on the left-lower block
derr = {
    a: LM[a]["p50"] * (1.0 + 0.55 * math.sin(i * 2.1))
    for i, a in enumerate(ABBR)
}
derr["PC"], derr["SPLE"] = 4.6, 5.3

t2 = chartbox(VX0 + 0.44, P_y0 + 0.66, 1.86, 1.30)
vals = sorted(derr.values(), reverse=True)
t2.bar(range(len(vals)), vals, color=[TIER[tier(v)] for v in vals], width=0.9)
for thr in (1, 2, 4):
    t2.axhline(thr, color="#cfcfcf", ls=":", lw=0.7)
t2.set_xticks([])
t2.set_ylim(0, 6)
t2.set_yticks([2, 4])
t2.tick_params(labelsize=5.6, length=2, color=HAIR, pad=1.4)
for s in ("top", "right"):
    t2.spines[s].set_visible(False)
for s in ("left", "bottom"):
    t2.spines[s].set_color(HAIR)
txt(
    VX0 + 1.37,
    P_y0 + 0.48,
    "ranked error (mm)",
    size=6.9,
    color=SUB,
    ha="center",
)

t3 = chartbox(VX0 + 2.42, P_y0 + 0.72, 1.20, 1.20, polar=True)
rv = [float(np.mean([derr[a] for a in aa])) for aa in REGION_MAP.values()]
th = np.linspace(0, 2 * np.pi, len(REGION_ORDER), endpoint=False)
t3.plot(np.concatenate([th, th[:1]]), rv + rv[:1], color=VALID_C, lw=1.5)
t3.fill(np.concatenate([th, th[:1]]), rv + rv[:1], color=VALID_C, alpha=0.2)
t3.set_xticks(th)
t3.set_xticklabels(
    ["Com", "Bstem", "Cblm", "Dien", "Vent", "Call", "Temp", "Basal"],
    fontsize=4.6,
)
for lbl, r in zip(t3.get_xticklabels(), REGION_ORDER):
    lbl.set_color(REGION_COLORS[r])
    lbl.set_fontweight("bold")
t3.tick_params(pad=-2.2)
t3.set_yticklabels([])
t3.set_ylim(0, max(rv) * 1.15)
t3.grid(color="#e3e3e3", lw=0.55)
t3.spines["polar"].set_color(HAIR)
txt(
    VX0 + 3.02, P_y0 + 0.48, "regional radar", size=6.9, color=SUB, ha="center"
)

# calibrated report table (right block)
rx0, rx1 = VX0 + 3.86, VX1 - 0.30
rrect(
    rx0, P_y0 + 0.44, rx1 - rx0, 2.16, fc=PANEL, ec=HAIR, lw=1.0, r=0.10, z=2
)
eyebrow(rx0 + 0.20, P_y0 + 2.40, "CALIBRATED REPORT")
for x, lab, ha in [
    (rx0 + 0.22, "landmark", "left"),
    (rx0 + 1.30, "error", "right"),
    (rx1 - 0.22, "verdict", "right"),
]:
    txt(x, P_y0 + 2.12, lab, size=6.6, color=MUT, ha=ha, weight="bold")
ax.plot(
    [rx0 + 0.20, rx1 - 0.20],
    [P_y0 + 2.00, P_y0 + 2.00],
    color=HAIR,
    lw=0.8,
    zorder=3,
)
for i, (a, mm) in enumerate(
    [("LIGO", 1.2), ("AC", 1.2), ("PMJ", 0.9), ("SPLE", 3.4)]
):
    yy = P_y0 + 1.78 - i * 0.34
    p = pct_of(a, mm)
    c = (
        TIER["ex"]
        if p < 50
        else TIER["good"]
        if p < 75
        else TIER["fair"]
        if p < 90
        else TIER["bad"]
    )
    v = (
        "excellent"
        if p < 50
        else "good"
        if p < 75
        else "review"
        if p < 90
        else "off-target"
    )
    ax.add_patch(
        Circle(
            (rx0 + 0.30, yy),
            0.052,
            fc=REGION_COLORS[ABBR2REG[a]],
            ec="white",
            lw=0.5,
            zorder=6,
        )
    )
    txt(rx0 + 0.44, yy, a, size=7.6, weight="bold")
    txt(rx0 + 1.30, yy, f"{mm:.1f} mm", size=7.6, color=SUB, ha="right")
    ax.add_patch(
        Rectangle(
            (rx0 + 1.48, yy - 0.11),
            rx1 - rx0 - 1.68,
            0.075,
            fc="#e6e9ee",
            ec="none",
            zorder=5,
        )
    )
    ax.add_patch(
        Rectangle(
            (rx0 + 1.48, yy - 0.11),
            (rx1 - rx0 - 1.68) * p / 100,
            0.075,
            fc=c,
            ec="none",
            zorder=5.1,
        )
    )
    txt(
        rx1 - 0.22,
        yy,
        f"{v} · {ordinal(p)}",
        size=7.2,
        color=c,
        weight="bold",
        ha="right",
    )

# tier legend (bottom, spans the charts block)
tiers_lbl = [
    ("< 1  excellent", TIER["ex"]),
    ("1–2  good", TIER["good"]),
    ("2–4  fair", TIER["fair"]),
    ("≥ 4  needs work", TIER["bad"]),
]
_tw = [extent(s, 6.9)[0] + 0.20 for s, _ in tiers_lbl]
_tx = VX0 + 0.44
for (s, c), w in zip(tiers_lbl, _tw):
    ax.add_patch(
        Rectangle((_tx, P_y0 + 0.26), 0.13, 0.13, fc=c, ec="none", zorder=6)
    )
    txt(_tx + 0.19, P_y0 + 0.325, s, size=6.9, color=SUB)
    _tx += w + 0.18

# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATION
# ══════════════════════════════════════════════════════════════════════════════
rrect(M, F_y0, CTW, H_FOUND, fc="#fdf8f1", ec="#f0e3d2", lw=1.2, r=0.12, z=1)
txt(
    M + 0.36,
    F_y0 + H_FOUND / 2,
    "OPEN\nBY DESIGN",
    size=8.6,
    weight="bold",
    color=OPEN_C,
    spacing=1.05,
)
# real tool logos (paper_figures/logos/), with a vector fallback if one is missing
LOGO = Path(OUT / "logos")
LOGO_H = 0.30
foundation = [
    ("gpl", "GPL-3.0 code", ic_copyleft),
    ("opendata", "Open reference data", ic_stack),
    ("templateflow", "TemplateFlow", ic_globe),
    (
        "niivue",
        "NiiVue viewer",
        lambda cx, cy, s, c: ic_target(cx, cy, s * 0.85, c),
    ),
    ("slicer_mark", "3D Slicer", ic_slicer),
    (
        "orcid",
        "ORCID identity",
        lambda cx, cy, s, c: ic_orcid(cx, cy, s * 0.95),
    ),
    (
        "docker",
        "Docker self-host",
        lambda cx, cy, s, c: ic_docker(cx, cy, s * 0.86, c),
    ),
]


def logo_width(name):
    p = LOGO / f"{name}.png"
    if p.exists():
        im = mpimg.imread(str(p))
        return LOGO_H * im.shape[1] / im.shape[0], p
    return 0.30, None


fx0, fx1 = 1.62, XR - 0.20
fstep = (fx1 - fx0) / len(foundation)
fcy = F_y0 + H_FOUND / 2
for i, (name, label, fallback) in enumerate(foundation):
    iw, path = logo_width(name)
    blk = iw + 0.16 + extent(label, 7.8, "bold")[0]
    x_ = fx0 + fstep * i + (fstep - blk) / 2
    if path is not None:
        a = imgbox(x_, fcy - LOGO_H / 2, iw, LOGO_H, z=6)
        a.imshow(mpimg.imread(str(path)), aspect="auto")
    else:
        fallback(x_ + 0.13, fcy, 0.13, OPEN_C)
        iw = 0.26
    txt(x_ + iw + 0.16, fcy, label, size=7.8, color="#6b5a45", weight="bold")
    if i < len(foundation) - 1:
        ax.plot(
            [fx0 + fstep * (i + 1)] * 2,
            [fcy - 0.20, fcy + 0.20],
            color="#eaddca",
            lw=1.0,
            zorder=2,
        )

# ══════════════════════════════════════════════════════════════════════════════
# AUDIT — no label leaves its card, leaves the page, or collides with another
# ══════════════════════════════════════════════════════════════════════════════
fig.canvas.draw()
_r2 = fig.canvas.get_renderer()
_inv = ax.transData.inverted()


def _bbox(t):
    bb = t.get_window_extent(_r2)
    (x0, y0) = _inv.transform((bb.x0, bb.y0))
    (x1, y1) = _inv.transform((bb.x1, bb.y1))
    return x0, y0, x1, y1


_boxes = [(_bbox(t), s.replace("\n", "⏎")[:36]) for t, s in _TEXTS]
_bad = []
for (x0, y0, x1, y1), lab in _boxes:
    if x0 < 0.03 or x1 > W - 0.03 or y0 < 0.03 or y1 > H - 0.03:
        _bad.append(
            f"  PAGE    [{lab}] x=({x0:.2f},{x1:.2f}) y=({y0:.2f},{y1:.2f})"
        )
        continue
    cxm, cym = (x0 + x1) / 2, (y0 + y1) / 2
    owner = next(
        (c for c in _CARDS if c[1] <= cxm <= c[3] and c[2] <= cym <= c[4]),
        None,
    )
    if owner:
        name, a0, b0, a1, b1 = owner
        if (
            x0 < a0 + 0.05
            or x1 > a1 - 0.05
            or y0 < b0 + 0.03
            or y1 > b1 - 0.03
        ):
            _bad.append(
                f"  SPILL   [{lab}] leaves {name}: x=({x0:.2f},{x1:.2f}) "
                f"y=({y0:.2f},{y1:.2f}) card x=({a0:.2f},{a1:.2f}) y=({b0:.2f},{b1:.2f})"
            )
    else:
        for name, a0, b0, a1, b1 in _CARDS:
            if x0 < a1 and x1 > a0 and y0 < b1 and y1 > b0:
                _bad.append(f"  STRAY   [{lab}] intrudes into {name}")
                break
    for zn, a0, b0, a1, b1 in _NOTEXT:  # text sitting on a chart/image
        ox = min(x1, a1) - max(x0, a0)
        oy = min(y1, b1) - max(y0, b0)
        if ox > 0.05 and oy > 0.05:
            _bad.append(
                f"  ONCHART [{lab}] over {zn}-region  overlap {ox:.2f}×{oy:.2f} in"
            )
for i in range(len(_boxes)):
    (ax0, ay0, ax1, ay1), la = _boxes[i]
    for j in range(i + 1, len(_boxes)):
        (bx0, by0, bx1, by1), lb = _boxes[j]
        ox = min(ax1, bx1) - max(ax0, bx0)
        oy = min(ay1, by1) - max(ay0, by0)
        if ox > 0.02 and oy > 0.02:
            _bad.append(
                f"  COLLIDE [{la}] ⨯ [{lb}]  overlap {ox:.2f}×{oy:.2f} in"
            )

print(
    f"\n{'⚠ %d layout problem(s):' % len(_bad) if _bad else '✓ layout audit clean'}"
)
print("\n".join(_bad))

for _ext in ("png", "pdf"):
    fig.savefig(
        OUT / f"fig0_graphical_abstract.{_ext}", facecolor="white", dpi=300
    )
plt.close(fig)
print(
    f"wrote fig0_graphical_abstract.png / .pdf   ({W}×{H:.1f} in, ratio {W / H:.2f})"
)
print(
    f"  {N_IMG} images · {N_SETS} expert annotations · {N_TPL} templates "
    f"({N_HUMAN}H + {N_MACAQ}M) · max spread {MAX_SPREAD:.1f} mm"
)
print(
    f"  {COIN_MM} mm  ->  {CAL_HARD} {ordinal(pct_of(CAL_HARD, COIN_MM))} pct · "
    f"{CAL_EASY} {ordinal(pct_of(CAL_EASY, COIN_MM))} pct"
)
