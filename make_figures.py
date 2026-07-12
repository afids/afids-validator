"""Publication figures for the AFIDs Validator education paper.

Regenerates all five manuscript figures from source (the MNI human FCSV
templates and the cached MNI152NLin2009cAsym T1w volume). Outputs 300-dpi PNG
and vector PDF to paper_figures/.

    python make_figures.py

The inter-template variability analysis (Figure 5) is restricted to the eight
canonical MNI152/MNI305 templates — a directly comparable family — excluding
the near-duplicate MNI2009cAsym alias.

Figures
-------
1  Guided-learning interface (annotated mockup over a real MNI slice)
2  The learning cycle and pedagogical principles (schematic)
3  The 32 AFIDs landmarks on MNI152NLin2009cAsym (glass-brain projections)
4  A worked quality-control catch on real data (template-space mismatch)
5  A difficulty benchmark for landmark placement (492 trained raters)
6  Two distinct kinds of difficulty (rater localization vs template variability)
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch

# ── Output & style ────────────────────────────────────────────────────────────
OUT = Path("paper_figures")
OUT.mkdir(exist_ok=True)

INK = "#1a1a1a"
GRID = "#e6e6e6"
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": [
            "Helvetica Neue",
            "Helvetica",
            "Arial",
            "DejaVu Sans",
        ],
        "font.size": 9,
        "text.color": INK,
        "axes.edgecolor": "#b8b8b8",
        "axes.labelcolor": INK,
        "axes.linewidth": 0.8,
        "axes.titlesize": 11,
        "axes.titleweight": "bold",
        "axes.titlecolor": INK,
        "xtick.color": "#555555",
        "ytick.color": "#555555",
        "figure.dpi": 120,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,
    }
)


def panel_letter(ax, letter, title):
    ax.set_title(f"{title}", loc="left", pad=8, fontsize=10.5)
    ax.text(
        -0.02,
        1.06,
        letter,
        transform=ax.transAxes,
        fontsize=13,
        fontweight="bold",
        va="bottom",
        ha="right",
        color=INK,
    )


def despine(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# ── Landmark metadata ─────────────────────────────────────────────────────────
ABBR = [
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
ABBR2REG = {a: r for r, aa in REGION_MAP.items() for a in aa}
REGION_ORDER = list(REGION_MAP.keys())
REGION_COLORS = {  # validated categorical palette (worst adjacent CVD ΔE 24.2)
    "Commissural": "#2a78d6",
    "Brainstem": "#1baf7a",
    "Cerebellar": "#eda100",
    "Diencephalic": "#008300",
    "Ventricular": "#4a3aa7",
    "Callosal": "#e34948",
    "Temporal": "#e87ba4",
    "Basal/Frontal": "#eb6834",
}
TIER_COLORS = {  # ordinal good→bad, aligned to the validated status palette
    "excellent": "#0ca30c",
    "good": "#7ab648",
    "fair": "#ec835a",
    "needs_work": "#d03b3b",
}


def tier(d):
    return (
        "excellent"
        if d < 1
        else "good"
        if d < 2
        else "fair"
        if d < 4
        else "needs_work"
    )


# ── Data ──────────────────────────────────────────────────────────────────────
HUMAN_DIR = Path("afidsvalidator/afids-templates/human")
BRAIN = Path("instance/brain_cache/tpl-MNI152NLin2009cAsym_res-01_T1w.nii.gz")
MNI_KEY = "tpl-MNI152NLin2009cAsym"
# Eight canonical MNI templates for the variability analysis (alias excluded)
MNI_SET = [
    "tpl-MNI152Lin",
    "tpl-MNI152NLin2009bAsym",
    "tpl-MNI152NLin2009bSym",
    "tpl-MNI152NLin2009cAsym",
    "tpl-MNI152NLin2009cSym",
    "tpl-MNI152NLin6Asym",
    "tpl-MNI152NLin6Sym",
    "tpl-MNI305",
]


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
            out[ABBR[int(p[11]) - 1]] = np.array(
                [float(p[1]), float(p[2]), float(p[3])]
            )
        except (ValueError, IndexError):
            continue
    return out


TPLS = {t: parse_fcsv(HUMAN_DIR / f"{t}_afids.fcsv") for t in MNI_SET}
ACN = {t: {a: c - v["AC"] for a, c in v.items()} for t, v in TPLS.items()}


def variability(a):
    pts = np.array([ACN[t][a] for t in MNI_SET])
    cen = pts.mean(0)
    d = np.linalg.norm(pts - cen, axis=1)
    return float(d.mean()), float(d.std())


# ── Brain volume (canonical RAS) ──────────────────────────────────────────────
def load_brain():
    import nibabel as nib

    img = nib.as_closest_canonical(nib.load(str(BRAIN)))
    data = np.asarray(img.get_fdata(), dtype=np.float32)
    data /= np.percentile(data, 99.5)
    data = np.clip(data, 0, 1) ** 0.8  # mild gamma for tissue contrast
    aff = img.affine
    nx, ny, nz = data.shape
    ext = dict(
        x=(aff[0, 3], aff[0, 3] + aff[0, 0] * nx),
        y=(aff[1, 3], aff[1, 3] + aff[1, 1] * ny),
        z=(aff[2, 3], aff[2, 3] + aff[2, 2] * nz),
    )
    return data, aff, ext


def world_to_vox(aff, xyz):
    return (np.linalg.inv(aff) @ np.array([*xyz, 1.0]))[:3]


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — the 32 landmarks on real MNI anatomy
# ══════════════════════════════════════════════════════════════════════════════
def fig3_landmarks():
    """A visual field guide: one real MNI152 T1w patch per AFIDs landmark.

    Each panel is a patch of the template centred on a landmark (crosshair on
    the exact point), grouped and coloured by region, tagged with the median
    trained-rater error and the viewing plane.
    """
    import json

    import nibabel as nib

    mni = parse_fcsv(HUMAN_DIR / f"{MNI_KEY}_afids.fcsv")
    rel = json.loads(
        (Path("afidsvalidator") / "rater_reliability.json").read_text()
    )["landmarks"]

    img = nib.as_closest_canonical(nib.load(str(BRAIN)))
    data = np.asarray(img.get_fdata(), dtype=np.float32)
    data /= np.percentile(data, 99.5)
    data = np.clip(data, 0, 1) ** 0.85
    inv = np.linalg.inv(img.affine)
    res = abs(img.affine[0, 0])
    half = 20.0
    n = int(round(half / res))

    def patch(a):
        v = np.rint(inv @ np.array([*mni[a], 1.0]))[:3].astype(int)
        if abs(mni[a][0]) < 6:  # midline → sagittal
            im = np.rot90(
                data[v[0], max(0, v[1] - n):v[1] + n, max(0, v[2] - n):v[2] + n]
            )
            plane = "sag"
        else:  # bilateral → axial
            im = np.rot90(
                data[max(0, v[0] - n):v[0] + n, max(0, v[1] - n):v[1] + n, v[2]]
            )
            plane = "ax"
        lo, hi = np.percentile(im, [2, 98])  # per-tile local contrast
        return np.clip((im - lo) / (hi - lo + 1e-6), 0, 1), plane

    order = [a for r in REGION_ORDER for a in REGION_MAP[r]]
    fig = plt.figure(figsize=(13.5, 8.0))
    gs = fig.add_gridspec(
        4, 8, hspace=0.42, wspace=0.12, left=0.02, right=0.98, top=0.96,
        bottom=0.08
    )
    for k, a in enumerate(order):
        ax = fig.add_subplot(gs[divmod(k, 8)])
        im, plane = patch(a)
        ax.imshow(im, cmap="gray", origin="upper", aspect="equal",
                  extent=(-half, half, -half, half))
        c = REGION_COLORS[ABBR2REG[a]]
        for s in (1, -1):  # gapped crosshair keeps the exact point visible
            ax.plot([s * 3.2, s * 8], [0, 0], color=c, lw=1.1, alpha=0.95,
                    solid_capstyle="round")
            ax.plot([0, 0], [s * 3.2, s * 8], color=c, lw=1.1, alpha=0.95,
                    solid_capstyle="round")
        ax.plot(0, 0, "o", ms=4.5, mfc="none", mec=c, mew=1.5)
        ax.set_xlim(-half, half)
        ax.set_ylim(-half, half)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor(c)
            sp.set_linewidth(2.4)
        ax.set_title(a, color=c, fontsize=8.5, fontweight="bold", pad=2)
        ax.text(0.05, 0.05, f"{rel[a]['p50']:.2f} mm", transform=ax.transAxes,
                fontsize=5.6, color="white", ha="left", va="bottom",
                bbox=dict(boxstyle="round,pad=0.12", fc=c, ec="none",
                          alpha=0.85))
        ax.text(0.95, 0.05, plane, transform=ax.transAxes, fontsize=5.2,
                color="#e8e8e8", ha="right", va="bottom")

    handles = [
        plt.Line2D([0], [0], marker="s", linestyle="", markersize=8,
                   markerfacecolor=REGION_COLORS[r], markeredgecolor="none",
                   label=r)
        for r in REGION_ORDER
    ]
    fig.legend(handles=handles, loc="lower center", ncol=8, fontsize=8.5,
               frameon=False, bbox_to_anchor=(0.5, 0.015), columnspacing=1.3,
               handletextpad=0.3)
    _save(fig, "fig3_landmarks")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 — a difficulty benchmark for landmark placement (from 492 raters)
# ══════════════════════════════════════════════════════════════════════════════
def _pctile_curve(s):
    """Monotone mm→percentile mapping from a landmark's reliability summary."""
    xs = [0.0, s["p10"], s["p25"], s["p50"], s["p75"], s["p90"]]
    ys = [0.0, 10.0, 25.0, 50.0, 75.0, 90.0]
    # extend past p90 with the p75→p90 slope, saturating at 99th percentile
    slope = 10.0 / max(1e-6, s["p90"] - s["p75"])
    xs.append(s["p90"] + (99.0 - 90.0) / slope)
    ys.append(99.0)
    return np.array(xs), np.array(ys)


def fig5_difficulty():
    """The trained-rater difficulty benchmark that grounds the tutor."""
    import json

    rel = json.loads(
        (Path("afidsvalidator") / "rater_reliability.json").read_text()
    )["landmarks"]

    fig = plt.figure(figsize=(13.8, 5.8))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.0, 1.05], wspace=0.34)

    # Panel A — difficulty atlas: median + IQR + mean (heavy tail), ranked
    axA = fig.add_subplot(gs[0, 0])
    despine(axA)
    items = sorted(
        ((a, rel[a]) for a in ABBR if a in rel), key=lambda kv: kv[1]["p50"]
    )
    y = np.arange(len(items))
    for i, (a, s) in enumerate(items):
        c = REGION_COLORS[ABBR2REG[a]]
        axA.plot(
            [s["p25"], s["p75"]],
            [i, i],
            color=c,
            lw=2.6,
            solid_capstyle="round",
            alpha=0.55,
            zorder=2,
        )
        axA.plot(s["p50"], i, "o", color=c, ms=5.5, zorder=4)
        axA.plot(s["mean"], i, "x", color=c, ms=4.5, mew=1.1, zorder=3)
    for thr, lab in ((0.5, ""), (1.0, ""), (2.0, "")):
        axA.axvline(thr, color="#c8c8c8", ls=":", lw=0.9, zorder=0)
    axA.set_yticks(y)
    axA.set_yticklabels([a for a, _ in items], fontsize=5.6)
    axA.set_ylim(-0.7, len(items) - 0.3)
    axA.set_xlim(0, 2.6)
    axA.set_xlabel("Trained-rater localization error, AFLE (mm)", fontsize=8.5)
    axA.plot([], [], "o", color="#555", ms=5.5, label="median")
    axA.plot(
        [], [], "x", color="#555", ms=4.5, mew=1.1, label="mean (heavy tail)"
    )
    axA.plot(
        [], [], "-", color="#999", lw=2.6, alpha=0.6, label="IQR (p25–p75)"
    )
    axA.legend(
        fontsize=6.3, loc="lower right", frameon=False, handletextpad=0.4
    )
    panel_letter(axA, "A", "A 3.9× difficulty spectrum across 32 landmarks")

    # Panel B — the same 1.2 mm placement, two verdicts
    axB = fig.add_subplot(gs[0, 1])
    despine(axB)
    demo = [("LIGO", 0), ("AC", 1)]  # hard on bottom row, easy on top row
    probe = 1.2
    for i, (a, yi) in enumerate(demo):
        s = rel[a]
        c = REGION_COLORS[ABBR2REG[a]]
        axB.plot(
            [s["p10"], s["p90"]],
            [yi, yi],
            color=c,
            lw=2.2,
            alpha=0.45,
            solid_capstyle="round",
            zorder=2,
        )
        axB.plot(
            [s["p25"], s["p75"]],
            [yi, yi],
            color=c,
            lw=8,
            alpha=0.5,
            solid_capstyle="round",
            zorder=2,
        )
        axB.plot(
            s["p50"],
            yi,
            "o",
            color=c,
            ms=8,
            zorder=4,
            markeredgecolor="white",
            markeredgewidth=0.8,
        )
        xs, ys = _pctile_curve(s)
        pct = float(np.interp(probe, xs, ys))
        p = round(pct)
        suf = ("th" if 11 <= p % 100 <= 13
               else {1: "st", 2: "nd", 3: "rd"}.get(p % 10, "th"))
        verdict = (
            f"within range\n(≈{p}{suf} pct, near median)"
            if pct < 75
            else f"outside expert range\n(≈{p}{suf} pct)"
        )
        axB.annotate(
            f"{a}: {verdict}",
            (probe, yi + 0.22),
            fontsize=7.2,
            ha="center",
            va="bottom",
            color=c,
            fontweight="bold",
        )
    axB.axvline(probe, color="#111111", ls="--", lw=1.3, zorder=5)
    axB.annotate(
        "one placement:\n1.2 mm from target",
        (probe, -0.62),
        fontsize=7.4,
        ha="center",
        va="top",
        color="#111111",
    )
    axB.set_yticks([0, 1])
    axB.set_yticklabels(["LIGO\n(hard)", "AC\n(easy)"], fontsize=7.5)
    axB.set_ylim(-1.05, 1.7)
    axB.set_xlim(0, 4.0)
    axB.set_xlabel("Trained-rater AFLE distribution (mm)", fontsize=8.5)
    panel_letter(axB, "B", "The same 1.2 mm — two verdicts")

    # Panel C — the mm→percentile calibration the platform applies
    axC = fig.add_subplot(gs[0, 2])
    despine(axC)
    curves = [("AC", "easiest"), ("IMS", "typical"), ("LIGO", "hardest")]
    xx = np.linspace(0, 4, 200)
    for a, _ in curves:
        s = rel[a]
        xs, ys = _pctile_curve(s)
        yy = np.interp(xx, xs, ys)
        axC.plot(
            xx, yy, color=REGION_COLORS[ABBR2REG[a]], lw=2.0, label=a, zorder=3
        )
    axC.axvline(1.2, color="#111111", ls="--", lw=1.0, zorder=1)
    for a, _ in curves:
        xs, ys = _pctile_curve(rel[a])
        axC.plot(
            1.2,
            float(np.interp(1.2, xs, ys)),
            "o",
            color=REGION_COLORS[ABBR2REG[a]],
            ms=5,
            zorder=4,
            markeredgecolor="white",
            markeredgewidth=0.7,
        )
    axC.axhline(50, color="#dddddd", lw=0.8, zorder=0)
    axC.set_xlim(0, 4)
    axC.set_ylim(0, 100)
    axC.set_xlabel("Placement error (mm)", fontsize=8.5)
    axC.set_ylabel("Percentile within trained raters", fontsize=8.5)
    axC.legend(
        fontsize=7,
        loc="lower right",
        frameon=False,
        title="landmark",
        title_fontsize=7,
    )
    axC.annotate("1.2 mm", (1.2, 4), fontsize=6.6, color="#111111", ha="left")
    panel_letter(axC, "C", "One error, calibrated per landmark")

    _save(fig, "fig5_difficulty")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — a worked QC catch on real data (template-space mismatch)
# ══════════════════════════════════════════════════════════════════════════════
def fig4_qc_catch():
    """A worked quality-control catch on REAL reference data.

    A common, silent error: landmarks defined in one MNI space are checked
    against a reference in another. We reproduce it exactly — MNI305-space
    landmarks validated against the platform default (MNI152NLin2009cAsym),
    aligned only at the anterior commissure (a one-point registration). The
    residual is the geometry a proper registration would still have to recover;
    the engine flags it as a region-localized signature, not a global blur.
    """
    import json

    rel = json.loads(
        (Path("afidsvalidator") / "rater_reliability.json").read_text()
    )["landmarks"]
    ref = ACN["tpl-MNI152NLin2009cAsym"]
    user = ACN["tpl-MNI305"]
    dists = {a: float(np.linalg.norm(user[a] - ref[a])) for a in ABBR}

    fig = plt.figure(figsize=(13.6, 5.0))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.55, 1.0], wspace=0.48)

    # Panel A — clean 3D scatter (AC-aligned coordinates)
    axA = fig.add_subplot(gs[0, 0], projection="3d")
    axA.set_box_aspect((1, 1, 1))
    for pane in (axA.xaxis, axA.yaxis, axA.zaxis):
        pane.pane.set_facecolor("white")
        pane.pane.set_edgecolor("#e8e8e8")
        pane._axinfo["grid"].update(color="#eeeeee", linewidth=0.5)
    for a in ABBR:
        r, u = ref[a], user[a]
        axA.plot(
            [r[0], u[0]],
            [r[1], u[1]],
            [r[2], u[2]],
            color=TIER_COLORS[tier(dists[a])],
            lw=0.9,
            alpha=0.8,
            zorder=1,
        )
    R = np.array([ref[a] for a in ABBR])
    U = np.array([user[a] for a in ABBR])
    axA.scatter(
        *R.T,
        s=22,
        c="#DDAA33",
        edgecolors="k",
        linewidths=0.3,
        label="Reference (default)",
        depthshade=False,
    )
    axA.scatter(
        *U.T, s=20, c="#333333", label="Uploaded (MNI305)", depthshade=False
    )
    axA.legend(fontsize=6.6, loc="upper left", framealpha=0.9)
    axA.set_xlabel("x", fontsize=7, labelpad=-4)
    axA.set_ylabel("y", fontsize=7, labelpad=-4)
    axA.set_zlabel("z", fontsize=7, labelpad=-4)
    axA.tick_params(labelsize=5.5, pad=-1)
    axA.view_init(elev=16, azim=-72)
    axA.set_title(
        "A   Uploaded vs reference", loc="left", fontsize=10.5, y=0.98
    )

    # Panel B — ranked error, with each landmark's trained-rater p90 as a marker
    axB = fig.add_subplot(gs[0, 1])
    despine(axB)
    order = sorted(ABBR, key=lambda a: dists[a], reverse=True)
    vals = [dists[a] for a in order]
    colors = [TIER_COLORS[tier(dists[a])] for a in order]
    x = np.arange(len(order))
    axB.bar(x, vals, color=colors, width=0.82, zorder=3)
    p90 = [rel[a]["p90"] for a in order]
    axB.plot(
        x,
        p90,
        "_",
        color="#111111",
        ms=7,
        mew=1.3,
        zorder=4,
        label="trained-rater p90",
    )
    for thr in (1, 2, 4):
        axB.axhline(thr, color="#c8c8c8", ls=":", lw=0.9, zorder=0)
    axB.set_xticks(x)
    axB.set_xticklabels(order, rotation=90, fontsize=6)
    axB.set_ylabel("Euclidean error (mm)", fontsize=8.5)
    axB.set_xlim(-0.7, len(order) - 0.3)
    mean_err = float(np.mean(list(dists.values())))
    n_over = sum(1 for a in ABBR if dists[a] > rel[a]["p90"])
    axB.annotate(
        f"mean {mean_err:.1f} mm  ·  {n_over}/32 beyond trained-rater p90",
        (0.97, 0.93),
        xycoords="axes fraction",
        ha="right",
        fontsize=8,
        color="#555555",
    )
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=c) for c in TIER_COLORS.values()
    ]
    axB.legend(
        handles,
        ["<1 excellent", "1–2 good", "2–4 fair", "≥4 needs work"],
        fontsize=6.6,
        ncol=2,
        loc="upper right",
        frameon=False,
        bbox_to_anchor=(0.995, 0.84),
    )
    panel_letter(axB, "B", "Per-landmark error vs the trained-rater ceiling")

    # Panel C — regional radar (the localized signature)
    axC = fig.add_subplot(gs[0, 2], projection="polar")
    reg_err = {
        r: np.mean([dists[a] for a in aa]) for r, aa in REGION_MAP.items()
    }
    regs = REGION_ORDER
    theta = np.linspace(0, 2 * np.pi, len(regs), endpoint=False)
    rv = [reg_err[r] for r in regs]
    tc = np.concatenate([theta, theta[:1]])
    rc = rv + rv[:1]
    axC.plot(tc, rc, color="#d03b3b", lw=1.8)
    axC.fill(tc, rc, color="#d03b3b", alpha=0.20)
    axC.set_xticks(theta)
    axC.set_xticklabels([r.replace("/", "/\n") for r in regs], fontsize=6.6)
    for lbl in axC.get_xticklabels():
        lbl.set_clip_on(False)
    rmax = max(rc)
    axC.set_ylim(0, rmax * 1.12)
    axC.set_yticks([t for t in (1, 2, 3, 4, 5) if t < rmax])
    axC.set_rlabel_position(96)
    axC.tick_params(axis="y", labelsize=5.8, colors="#999999")
    axC.tick_params(axis="x", pad=1)
    axC.set_title(
        "C   Mean error by region", loc="left", pad=20, fontsize=10.5
    )
    axC.grid(color="#dddddd")

    _save(fig, "fig4_qc_catch")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — the learning cycle and pedagogical principles
# ══════════════════════════════════════════════════════════════════════════════
def fig2_cycle():
    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.8)
    ax.axis("off")

    # coloured by actor: AI tutor (blue), learner (green), server (grey)
    LLM_C, USER_C, SRV_C = "#2a78d6", "#008300", "#898781"
    steps = [
        (
            "Introduce",
            "AI tutor: anatomy,\nMRI appearance,\nwhere to look",
            LLM_C,
            "LLM",
        ),
        (
            "Place",
            "Learner clicks a\nfiducial in the\nNiiVue viewer",
            USER_C,
            "user",
        ),
        (
            "Compute",
            "Server: Euclidean\nerror + direction\n(< 50 ms)",
            SRV_C,
            "server",
        ),
        (
            "Feedback",
            "AI tutor: verdict,\nanatomical reasoning,\nviewer tips",
            LLM_C,
            "LLM",
        ),
        (
            "Dialogue",
            "Free-form Q&A,\nthen advance to\nthe next landmark",
            USER_C,
            "user",
        ),
    ]
    cx = [1.55, 4.0, 6.45, 8.9, 5.2]
    cy = [4.35, 4.35, 4.35, 4.35, 1.95]
    for i, ((title, body, color, actor), x, y) in enumerate(
        zip(steps, cx, cy), 1
    ):
        ax.add_patch(
            FancyBboxPatch(
                (x - 1.02, y - 0.78),
                2.04,
                1.56,
                boxstyle="round,pad=0.03,rounding_size=0.14",
                linewidth=1.5,
                edgecolor=color,
                facecolor=color + "12",
                zorder=2,
            )
        )
        # number badge
        ax.add_patch(Circle((x - 0.78, y + 0.56), 0.17, color=color, zorder=4))
        ax.text(
            x - 0.78,
            y + 0.56,
            str(i),
            ha="center",
            va="center",
            fontsize=8,
            color="white",
            fontweight="bold",
            zorder=5,
        )
        ax.text(
            x + 0.05,
            y + 0.5,
            title,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color=color,
        )
        ax.text(
            x,
            y - 0.14,
            body,
            ha="center",
            va="center",
            fontsize=7.3,
            color="#333333",
        )
        ax.text(
            x,
            y - 0.62,
            actor,
            ha="center",
            va="center",
            fontsize=6,
            style="italic",
            color="#999999",
        )

    def arrow(p, q, rad=0.0):
        ax.add_patch(
            FancyArrowPatch(
                p,
                q,
                connectionstyle=f"arc3,rad={rad}",
                arrowstyle="-|>",
                mutation_scale=15,
                lw=1.5,
                color="#888888",
                zorder=1,
            )
        )

    arrow((2.62, 4.35), (2.94, 4.35))
    arrow((5.07, 4.35), (5.39, 4.35))
    arrow((7.52, 4.35), (7.84, 4.35))
    arrow((8.9, 3.52), (6.15, 2.35), rad=-0.18)
    arrow((4.25, 2.35), (1.55, 3.52), rad=-0.18)
    ax.text(
        2.55,
        2.78,
        "repeat ×32",
        fontsize=7.3,
        style="italic",
        color="#999999",
        rotation=36,
    )

    principles = [
        ("Productive failure", "attempt before full instruction"),
        ("Anatomy-first", "never give raw coordinates"),
        ("Viewer-context aware", "feedback adapts to zoom / resolution"),
        ("RAG-grounded", "anchored to the AFIDs protocol"),
    ]
    ax.add_patch(
        FancyBboxPatch(
            (0.4, 0.12),
            10.2,
            0.98,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            linewidth=0,
            facecolor="#f4f4f6",
            zorder=0,
        )
    )
    ax.text(
        0.68,
        0.61,
        "Design\nprinciples",
        fontsize=8.2,
        fontweight="bold",
        color="#333333",
        va="center",
        linespacing=1.1,
    )
    for i, (name, desc) in enumerate(principles):
        xx = 2.5 + i * 2.0
        ax.add_patch(Circle((xx - 0.16, 0.61), 0.05, color="#2a78d6"))
        ax.text(
            xx,
            0.75,
            name,
            fontsize=7.7,
            fontweight="bold",
            color="#2a78d6",
            va="center",
        )
        ax.text(xx, 0.44, desc, fontsize=6.4, color="#555555", va="center")

    _save(fig, "fig2_learning_cycle")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — annotated interface mockup over a real MNI slice
# ══════════════════════════════════════════════════════════════════════════════
def fig1_interface():
    """Annotated hero built from a live-app screenshot.

    ``paper_figures/ss_learn_hero.png`` is captured by capture_screenshots.sh
    against a running instance; this only composites callouts onto it, so it is
    skipped when the asset is absent.
    """
    import matplotlib.image as mpimg

    src = OUT / "ss_learn_hero.png"
    if not src.exists():
        print("  (skip fig1 \u2014 run capture_screenshots.sh first)")
        return
    im = mpimg.imread(str(src))
    g = im[..., :3].mean(-1) if im.ndim == 3 else im
    rows = np.where(g.max(1) > 0.08)[0]
    cols = np.where(g.max(0) > 0.08)[0]
    crop = im[rows.min() : rows.max(), cols.min() : cols.max()]
    H, W = crop.shape[:2]
    green = "#00ff01"
    fig = plt.figure(figsize=(12, 12 * H / W + 1.1))
    ax = fig.add_axes([0, 0.11, 1, 0.89])
    ax.imshow(crop)
    ax.axis("off")
    for fx, fy, n in [
        (0.33, 0.40, "1"),
        (0.725, 0.115, "2"),
        (0.80, 0.46, "3"),
        (0.945, 0.05, "4"),
        (0.30, 0.945, "5"),
    ]:
        ax.add_patch(
            Circle(
                (fx * W, fy * H),
                34,
                facecolor=green,
                edgecolor="black",
                lw=2,
                zorder=5,
            )
        )
        ax.text(
            fx * W,
            fy * H,
            n,
            ha="center",
            va="center",
            fontsize=15,
            fontweight="bold",
            color="black",
            zorder=6,
        )
    legend = (
        "\u2460  Multiplanar MRI viewer (NiiVue)      "
        "\u2461  Rater-calibrated result: error + percentile vs raters\n"
        "\u2462  Difficulty-aware, anatomy-first AI tutor      "
        "\u2463  Bring-your-own-key + active model      "
        "\u2464  32-landmark progress + export"
    )
    fig.text(
        0.5,
        0.05,
        legend,
        ha="center",
        va="center",
        fontsize=10.5,
        color="#222222",
        linespacing=1.9,
    )
    _save(fig, "fig1_interface")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 6 — two distinct kinds of difficulty (localize vs reproduce)
# ══════════════════════════════════════════════════════════════════════════════
def fig6_two_difficulties():
    import json

    rel = json.loads(
        (Path("afidsvalidator") / "rater_reliability.json").read_text()
    )["landmarks"]

    fig = plt.figure(figsize=(12.6, 5.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.15], wspace=0.28)

    # Panel A — rater difficulty vs template variability (distinct axes)
    axA = fig.add_subplot(gs[0, 0])
    despine(axA)
    common = [a for a in ABBR if a in rel and a != "AC"]
    xv = np.array([variability(a)[0] for a in common])
    yv = np.array([rel[a]["p50"] for a in common])
    cols = [REGION_COLORS[ABBR2REG[a]] for a in common]
    axA.scatter(
        xv, yv, c=cols, s=38, edgecolors="white", linewidths=0.5, zorder=3
    )
    m, b = np.polyfit(xv, yv, 1)
    xs = np.array([xv.min(), xv.max()])
    axA.plot(xs, m * xs + b, color="#898781", lw=1.2, ls="--", zorder=1)
    r = float(np.corrcoef(xv, yv)[0, 1])
    axA.annotate(
        f"r = {r:.2f}",
        (0.05, 0.92),
        xycoords="axes fraction",
        fontsize=9,
        color="#52514e",
        fontweight="bold",
    )
    for a in ("LIGO", "RVOH", "PC", "RLVPC"):
        if a in common:
            axA.annotate(
                a,
                (variability(a)[0], rel[a]["p50"]),
                textcoords="offset points",
                xytext=(4, 3),
                fontsize=6.5,
                color="#52514e",
            )
    axA.set_xlabel(
        "Inter-template variability, 'reproduce' (mm)", fontsize=8.5
    )
    axA.set_ylabel("Trained-rater median error, 'localize' (mm)", fontsize=8.5)
    panel_letter(axA, "A", "Hard to localize ≠ hard to reproduce")

    # Panel B — per-landmark template variability, ranked (demoted correctness)
    axB = fig.add_subplot(gs[0, 1])
    despine(axB)
    stats = sorted(
        ((a, *variability(a)) for a in ABBR if a != "AC"),
        key=lambda s: s[1],
        reverse=True,
    )
    labels = [s[0] for s in stats]
    means = np.array([s[1] for s in stats])
    x = np.arange(len(labels))
    colors = [REGION_COLORS[ABBR2REG[a]] for a in labels]
    axB.bar(x, means, color=colors, width=0.82, zorder=3)
    for thr in (1, 2):
        axB.axhline(thr, color="#c8c8c8", ls=":", lw=0.9, zorder=0)
        axB.annotate(
            f"{thr} mm",
            (len(labels) - 0.4, thr),
            fontsize=6.5,
            color="#999999",
            va="bottom",
            ha="right",
        )
    axB.set_xticks(x)
    axB.set_xticklabels(labels, rotation=90, fontsize=6)
    axB.set_ylabel("Inter-template variability (mm)", fontsize=8.5)
    axB.set_ylim(0, float(max(means)) * 1.15)
    axB.set_xlim(-0.7, len(labels) - 0.3)
    panel_letter(axB, "B", "How much references disagree (8 MNI templates)")

    handles = [
        plt.Line2D(
            [0],
            [0],
            marker="o",
            linestyle="",
            markersize=7,
            markerfacecolor=REGION_COLORS[r_],
            markeredgecolor="white",
            markeredgewidth=0.6,
            label=r_,
        )
        for r_ in REGION_ORDER
    ]
    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=8,
        fontsize=8,
        frameon=False,
        bbox_to_anchor=(0.5, -0.04),
        columnspacing=1.3,
        handletextpad=0.3,
    )
    _save(fig, "fig6_two_difficulties")


# ── Save helper ───────────────────────────────────────────────────────────────
def _save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", facecolor="white")
    plt.close(fig)
    print(f"  wrote {name}.png / .pdf")


def fig0_graphical_abstract():
    """Graphical abstract — the whole platform in one frame.

    Composed by the dedicated ``make_graphical_abstract.py`` (layout) on top of
    two embedded rasters built by ``make_ga_assets.py`` (the region-coloured
    glass brain and a crop of the live /learn interface). Kept here so the full
    figure set still regenerates from ``python make_figures.py``.
    """
    import runpy

    runpy.run_path("make_ga_assets.py", run_name="__main__")
    runpy.run_path("make_graphical_abstract.py", run_name="__main__")


if __name__ == "__main__":
    print("Generating figures →", OUT.resolve())
    fig0_graphical_abstract()
    fig1_interface()
    fig2_cycle()
    fig3_landmarks()
    fig4_qc_catch()
    fig5_difficulty()
    fig6_two_difficulties()
    print("Done.")
