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
4  A worked validation report (illustrative session)
5  Why the reference standard is principled (inter-MNI-template variability)
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
        "font.sans-serif": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
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
    ax.text(-0.02, 1.06, letter, transform=ax.transAxes, fontsize=13,
            fontweight="bold", va="bottom", ha="right", color=INK)


def despine(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


# ── Landmark metadata ─────────────────────────────────────────────────────────
ABBR = [
    "AC", "PC", "ICS", "PMJ", "SIPF", "RSLMS", "LSLMS", "RILMS", "LILMS",
    "CUL", "IMS", "RMB", "LMB", "PG", "RLVAC", "LLVAC", "RLVPC", "LLVPC",
    "GENU", "SPLE", "RALTH", "LALTH", "RSAMTH", "LSAMTH", "RIAMTH", "LIAMTH",
    "RIGO", "LIGO", "RVOH", "LVOH", "ROSF", "LOSF",
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
    "excellent": "#0ca30c", "good": "#7ab648",
    "fair": "#ec835a", "needs_work": "#d03b3b",
}


def tier(d):
    return ("excellent" if d < 1 else "good" if d < 2 else "fair" if d < 4
            else "needs_work")


# ── Data ──────────────────────────────────────────────────────────────────────
HUMAN_DIR = Path("afidsvalidator/afids-templates/human")
BRAIN = Path("instance/brain_cache/tpl-MNI152NLin2009cAsym_res-01_T1w.nii.gz")
MNI_KEY = "tpl-MNI152NLin2009cAsym"
# Eight canonical MNI templates for the variability analysis (alias excluded)
MNI_SET = [
    "tpl-MNI152Lin", "tpl-MNI152NLin2009bAsym", "tpl-MNI152NLin2009bSym",
    "tpl-MNI152NLin2009cAsym", "tpl-MNI152NLin2009cSym",
    "tpl-MNI152NLin6Asym", "tpl-MNI152NLin6Sym", "tpl-MNI305",
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
                [float(p[1]), float(p[2]), float(p[3])])
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
    import warnings

    from nilearn import plotting

    mni = parse_fcsv(HUMAN_DIR / f"{MNI_KEY}_afids.fcsv")
    fig = plt.figure(figsize=(13, 4.7))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        disp = plotting.plot_glass_brain(
            None, display_mode="lyrz", figure=fig, alpha=0.28, black_bg=False)
        for region, abbrevs in REGION_MAP.items():
            coords = np.array([mni[a] for a in abbrevs if a in mni])
            disp.add_markers(
                coords, marker_color=REGION_COLORS[region], marker_size=32,
                marker=".", alpha=0.95)

    handles = [
        plt.Line2D([0], [0], marker="o", linestyle="", markersize=8,
                   markerfacecolor=REGION_COLORS[r], markeredgecolor="white",
                   markeredgewidth=0.7, label=r)
        for r in REGION_ORDER
    ]
    fig.legend(handles=handles, loc="lower center", ncol=8, fontsize=8.5,
               frameon=False, bbox_to_anchor=(0.5, -0.02), columnspacing=1.4,
               handletextpad=0.3)
    fig.suptitle("The 32 AFIDs landmarks on the MNI152NLin2009cAsym template",
                 fontsize=12.5, fontweight="bold", y=1.0)
    _save(fig, "fig3_landmarks")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 — inter-MNI-template variability
# ══════════════════════════════════════════════════════════════════════════════
def fig5_variability():
    fig = plt.figure(figsize=(13.6, 5.2))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.0, 1.55, 1.0], wspace=0.5)

    # Panel A — AC–PC distance, outliers highlighted
    axA = fig.add_subplot(gs[0, 0])
    despine(axA)
    acpc = {t: float(np.linalg.norm(ACN[t]["PC"])) for t in MNI_SET}
    items = sorted(acpc.items(), key=lambda kv: kv[1])
    names = [t.replace("tpl-", "") for t, _ in items]
    vals = [v for _, v in items]
    outlier = {"MNI305", "MNI152Lin"}
    colors = ["#d03b3b" if n in outlier else "#5b7a9d" for n in names]
    y = np.arange(len(vals))
    axA.barh(y, vals, color=colors, height=0.72)
    axA.axvline(float(np.mean(vals)), color="#333333", ls="--", lw=1.1,
                label=f"mean {np.mean(vals):.1f} mm")
    axA.set_yticks(y)
    axA.set_yticklabels(names, fontsize=6.6)
    axA.set_xlim(27, 31.5)
    axA.set_xlabel("AC–PC distance (mm)", fontsize=8.5)
    axA.legend(fontsize=7, loc="lower right", frameon=False)
    axA.annotate("linear / original\nvariants diverge",
                 xy=(31.0, len(vals) - 1), xytext=(28.7, len(vals) - 2.2),
                 fontsize=6.8, color="#d03b3b",
                 arrowprops=dict(arrowstyle="-", color="#d03b3b", lw=0.7))
    panel_letter(axA, "A", "Template mismatch cost")

    # Panel B — per-landmark variability, ranked; SD as light upper cap
    axB = fig.add_subplot(gs[0, 1])
    despine(axB)
    stats = sorted(((a, *variability(a)) for a in ABBR if a != "AC"),
                   key=lambda s: s[1], reverse=True)
    labels = [s[0] for s in stats]
    means = np.array([s[1] for s in stats])
    sds = np.array([s[2] for s in stats])
    x = np.arange(len(labels))
    colors = [REGION_COLORS[ABBR2REG[a]] for a in labels]
    axB.bar(x, means, color=colors, width=0.82, zorder=3)
    for thr in (1, 2):
        axB.axhline(thr, color="#c8c8c8", ls=":", lw=0.9, zorder=0)
        axB.annotate(f"{thr} mm", (len(labels) - 0.4, thr), fontsize=6.5,
                     color="#999999", va="bottom", ha="right")
    axB.set_xticks(x)
    axB.set_xticklabels(labels, rotation=90, fontsize=6)
    axB.set_ylabel("Inter-template variability (mm)", fontsize=8.5)
    axB.set_ylim(0, float(max(means)) * 1.15)
    axB.set_xlim(-0.7, len(labels) - 0.3)
    panel_letter(axB, "B", "Per-landmark variability (8 MNI templates)")

    # Panel C — regional radar
    axC = fig.add_subplot(gs[0, 2], projection="polar")
    reg_means = {r: np.mean([variability(a)[0] for a in aa if a != "AC"])
                 for r, aa in REGION_MAP.items()}
    regs = REGION_ORDER
    theta = np.linspace(0, 2 * np.pi, len(regs), endpoint=False)
    rvals = [reg_means[r] for r in regs]
    tc = np.concatenate([theta, theta[:1]])
    rc = rvals + rvals[:1]
    axC.plot(tc, rc, color="#2a78d6", lw=1.8)
    axC.fill(tc, rc, color="#2a78d6", alpha=0.20)
    axC.set_xticks(theta)
    axC.set_xticklabels([r.replace("/", "/\n") for r in regs], fontsize=6.6)
    for lbl in axC.get_xticklabels():
        lbl.set_clip_on(False)
    axC.set_ylim(0, max(rvals) * 1.18)
    axC.set_yticks([0.5, 1.0, 1.5])
    axC.set_rlabel_position(96)
    axC.tick_params(axis="y", labelsize=5.8, colors="#999999")
    axC.tick_params(axis="x", pad=1)
    axC.set_title("C   Regional mean", loc="left", pad=20, fontsize=10.5)
    axC.grid(color="#dddddd")

    fig.suptitle("Even within the MNI family, references differ enough to matter",
                 fontsize=12.5, fontweight="bold", y=1.02)
    _save(fig, "fig5_variability")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — worked validation report (illustrative session)
# ══════════════════════════════════════════════════════════════════════════════
def fig4_validation():
    mni = parse_fcsv(HUMAN_DIR / f"{MNI_KEY}_afids.fcsv")
    rng = np.random.default_rng(7)
    user = {}
    for a in ABBR:
        base, _ = variability(a)
        sigma = 0.5 + 0.9 * base
        user[a] = mni[a] + rng.normal(0, sigma, 3)
    user["PC"] = mni["PC"] + np.array([0.2, 3.6, 2.4])       # habenular confusion
    user["SPLE"] = mni["SPLE"] + np.array([-0.5, 5.1, 1.2])  # callosal body
    dists = {a: float(np.linalg.norm(user[a] - mni[a])) for a in ABBR}

    fig = plt.figure(figsize=(13.6, 5.0))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.05, 1.55, 1.0], wspace=0.48)

    # Panel A — clean 3D scatter
    axA = fig.add_subplot(gs[0, 0], projection="3d")
    axA.set_box_aspect((1, 1, 1))
    for pane in (axA.xaxis, axA.yaxis, axA.zaxis):
        pane.pane.set_facecolor("white")
        pane.pane.set_edgecolor("#e8e8e8")
        pane._axinfo["grid"].update(color="#eeeeee", linewidth=0.5)
    for a in ABBR:
        r, u = mni[a], user[a]
        axA.plot([r[0], u[0]], [r[1], u[1]], [r[2], u[2]],
                 color=TIER_COLORS[tier(dists[a])], lw=0.9, alpha=0.8, zorder=1)
    R = np.array([mni[a] for a in ABBR])
    U = np.array([user[a] for a in ABBR])
    axA.scatter(*R.T, s=22, c="#DDAA33", edgecolors="k", linewidths=0.3,
                label="Reference", depthshade=False)
    axA.scatter(*U.T, s=20, c="#333333", label="Placement", depthshade=False)
    axA.legend(fontsize=7, loc="upper left", framealpha=0.9)
    axA.set_xlabel("x", fontsize=7, labelpad=-4)
    axA.set_ylabel("y", fontsize=7, labelpad=-4)
    axA.set_zlabel("z", fontsize=7, labelpad=-4)
    axA.tick_params(labelsize=5.5, pad=-1)
    axA.view_init(elev=16, azim=-72)
    axA.set_title("A   Placement vs reference", loc="left", fontsize=10.5, y=0.98)

    # Panel B — ranked error
    axB = fig.add_subplot(gs[0, 1])
    despine(axB)
    order = sorted(ABBR, key=lambda a: dists[a], reverse=True)
    vals = [dists[a] for a in order]
    colors = [TIER_COLORS[tier(dists[a])] for a in order]
    x = np.arange(len(order))
    axB.bar(x, vals, color=colors, width=0.82, zorder=3)
    for thr in (1, 2, 4):
        axB.axhline(thr, color="#c8c8c8", ls=":", lw=0.9, zorder=0)
    axB.set_xticks(x)
    axB.set_xticklabels(order, rotation=90, fontsize=6)
    axB.set_ylabel("Euclidean error (mm)", fontsize=8.5)
    axB.set_xlim(-0.7, len(order) - 0.3)
    mean_err = float(np.mean(list(dists.values())))
    axB.annotate(f"mean {mean_err:.1f} mm", (0.97, 0.92), xycoords="axes fraction",
                 ha="right", fontsize=8.5, color="#555555")
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in TIER_COLORS.values()]
    axB.legend(handles, ["<1 excellent", "1–2 good", "2–4 fair", "≥4 needs work"],
               fontsize=6.6, ncol=2, loc="upper right", frameon=False,
               bbox_to_anchor=(0.995, 0.86))
    panel_letter(axB, "B", "Per-landmark error (ranked)")

    # Panel C — regional radar
    axC = fig.add_subplot(gs[0, 2], projection="polar")
    reg_err = {r: np.mean([dists[a] for a in aa]) for r, aa in REGION_MAP.items()}
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
    axC.set_yticks([t for t in (1, 2, 3, 4) if t < rmax])
    axC.set_rlabel_position(96)
    axC.tick_params(axis="y", labelsize=5.8, colors="#999999")
    axC.tick_params(axis="x", pad=1)
    axC.set_title("C   Mean error by region", loc="left", pad=20, fontsize=10.5)
    axC.grid(color="#dddddd")

    fig.suptitle("A worked validation report (illustrative session)",
                 fontsize=12.5, fontweight="bold", y=1.06)
    _save(fig, "fig4_validation")


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
        ("Introduce", "AI tutor: anatomy,\nMRI appearance,\nwhere to look", LLM_C, "LLM"),
        ("Place", "Learner clicks a\nfiducial in the\nNiiVue viewer", USER_C, "user"),
        ("Compute", "Server: Euclidean\nerror + direction\n(< 50 ms)", SRV_C, "server"),
        ("Feedback", "AI tutor: verdict,\nanatomical reasoning,\nviewer tips", LLM_C, "LLM"),
        ("Dialogue", "Free-form Q&A,\nthen advance to\nthe next landmark", USER_C, "user"),
    ]
    cx = [1.55, 4.0, 6.45, 8.9, 5.2]
    cy = [4.35, 4.35, 4.35, 4.35, 1.95]
    for i, ((title, body, color, actor), x, y) in enumerate(zip(steps, cx, cy), 1):
        ax.add_patch(FancyBboxPatch((x - 1.02, y - 0.78), 2.04, 1.56,
                     boxstyle="round,pad=0.03,rounding_size=0.14",
                     linewidth=1.5, edgecolor=color, facecolor=color + "12", zorder=2))
        # number badge
        ax.add_patch(Circle((x - 0.78, y + 0.56), 0.17, color=color, zorder=4))
        ax.text(x - 0.78, y + 0.56, str(i), ha="center", va="center",
                fontsize=8, color="white", fontweight="bold", zorder=5)
        ax.text(x + 0.05, y + 0.5, title, ha="center", va="center", fontsize=10,
                fontweight="bold", color=color)
        ax.text(x, y - 0.14, body, ha="center", va="center", fontsize=7.3,
                color="#333333")
        ax.text(x, y - 0.62, actor, ha="center", va="center", fontsize=6,
                style="italic", color="#999999")

    def arrow(p, q, rad=0.0):
        ax.add_patch(FancyArrowPatch(p, q, connectionstyle=f"arc3,rad={rad}",
                     arrowstyle="-|>", mutation_scale=15, lw=1.5,
                     color="#888888", zorder=1))

    arrow((2.62, 4.35), (2.94, 4.35))
    arrow((5.07, 4.35), (5.39, 4.35))
    arrow((7.52, 4.35), (7.84, 4.35))
    arrow((8.9, 3.52), (6.15, 2.35), rad=-0.18)
    arrow((4.25, 2.35), (1.55, 3.52), rad=-0.18)
    ax.text(2.55, 2.78, "repeat ×32", fontsize=7.3, style="italic",
            color="#999999", rotation=36)

    principles = [
        ("Productive failure", "attempt before full instruction"),
        ("Anatomy-first", "never give raw coordinates"),
        ("Viewer-context aware", "feedback adapts to zoom / resolution"),
        ("RAG-grounded", "answers anchored to the AFIDs protocol"),
    ]
    ax.add_patch(FancyBboxPatch((0.4, 0.12), 10.2, 0.98,
                 boxstyle="round,pad=0.02,rounding_size=0.06",
                 linewidth=0, facecolor="#f4f4f6", zorder=0))
    ax.text(0.68, 0.61, "Design\nprinciples", fontsize=8.2, fontweight="bold",
            color="#333333", va="center", linespacing=1.1)
    for i, (name, desc) in enumerate(principles):
        xx = 2.55 + i * 2.05
        ax.add_patch(Circle((xx - 0.16, 0.61), 0.05, color="#2a78d6"))
        ax.text(xx, 0.75, name, fontsize=7.7, fontweight="bold",
                color="#2a78d6", va="center")
        ax.text(xx, 0.44, desc, fontsize=6.4, color="#555555", va="center")

    ax.text(5.5, 5.55, "The guided-learning cycle", ha="center", fontsize=13,
            fontweight="bold", color=INK)
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
    crop = im[rows.min():rows.max(), cols.min():cols.max()]
    H, W = crop.shape[:2]
    green = "#00ff01"
    fig = plt.figure(figsize=(12, 12 * H / W + 1.1))
    ax = fig.add_axes([0, 0.11, 1, 0.89])
    ax.imshow(crop)
    ax.axis("off")
    for fx, fy, n in [(0.33, 0.40, "1"), (0.725, 0.115, "2"), (0.80, 0.46, "3"),
                      (0.945, 0.05, "4"), (0.30, 0.945, "5")]:
        ax.add_patch(Circle((fx * W, fy * H), 34, facecolor=green,
                            edgecolor="black", lw=2, zorder=5))
        ax.text(fx * W, fy * H, n, ha="center", va="center", fontsize=15,
                fontweight="bold", color="black", zorder=6)
    legend = ("\u2460  Multiplanar MRI viewer (NiiVue)      "
              "\u2461  Rater-calibrated result: error + percentile vs raters\n"
              "\u2462  Difficulty-aware, anatomy-first AI tutor      "
              "\u2463  Bring-your-own-key + active model      "
              "\u2464  32-landmark progress + export")
    fig.text(0.5, 0.05, legend, ha="center", va="center", fontsize=10.5,
             color="#222222", linespacing=1.9)
    fig.text(0.5, 0.005, "The AFIDs Validator guided-learning interface "
             "(live session)", ha="center", fontsize=13, fontweight="bold",
             color="#111111")
    _save(fig, "fig1_interface")


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 6 — trained-rater reliability, and how it differs from template variability
# ══════════════════════════════════════════════════════════════════════════════
def fig6_reliability():
    import json

    rel = json.loads(
        (Path("afidsvalidator") / "rater_reliability.json").read_text()
    )["landmarks"]

    fig = plt.figure(figsize=(13.4, 5.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.35, 1.0], wspace=0.28)

    # Panel A — per-landmark trained-rater AFLE spectrum (median + IQR)
    axA = fig.add_subplot(gs[0, 0])
    despine(axA)
    items = sorted(((a, rel[a]) for a in ABBR if a in rel),
                   key=lambda kv: kv[1]["p50"])
    y = np.arange(len(items))
    for i, (a, s) in enumerate(items):
        c = REGION_COLORS[ABBR2REG[a]]
        axA.plot([s["p25"], s["p75"]], [i, i], color=c, lw=2.4,
                 solid_capstyle="round", alpha=0.55, zorder=2)
        axA.plot(s["p50"], i, "o", color=c, ms=6, zorder=3)
    for thr in (0.5, 1.0):
        axA.axvline(thr, color="#c8c8c8", ls=":", lw=0.9, zorder=0)
    axA.set_yticks(y)
    axA.set_yticklabels([a for a, _ in items], fontsize=5.6)
    axA.set_ylim(-0.7, len(items) - 0.3)
    axA.set_xlabel("Trained-rater localization error (mm)  ·  median + IQR",
                   fontsize=8.5)
    axA.set_xlim(0, None)
    panel_letter(axA, "A", "How hard each landmark is for humans")

    # Panel B — rater difficulty vs template variability (distinct axes)
    axB = fig.add_subplot(gs[0, 1])
    despine(axB)
    common = [a for a in ABBR if a in rel and a != "AC"]
    xv = np.array([variability(a)[0] for a in common])
    yv = np.array([rel[a]["p50"] for a in common])
    cols = [REGION_COLORS[ABBR2REG[a]] for a in common]
    axB.scatter(xv, yv, c=cols, s=34, edgecolors="white", linewidths=0.5, zorder=3)
    m, b = np.polyfit(xv, yv, 1)
    xs = np.array([xv.min(), xv.max()])
    axB.plot(xs, m * xs + b, color="#898781", lw=1.2, ls="--", zorder=1)
    r = float(np.corrcoef(xv, yv)[0, 1])
    axB.annotate(f"r = {r:.2f}", (0.05, 0.92), xycoords="axes fraction",
                 fontsize=9, color="#52514e", fontweight="bold")
    for a in ("LIGO", "RVOH", "PC", "RLVPC"):
        if a in common:
            axB.annotate(a, (variability(a)[0], rel[a]["p50"]),
                         textcoords="offset points", xytext=(4, 3),
                         fontsize=6.5, color="#52514e")
    axB.set_xlabel("Inter-template variability (mm)", fontsize=8.5)
    axB.set_ylabel("Trained-rater median error (mm)", fontsize=8.5)
    panel_letter(axB, "B", "Two distinct kinds of difficulty")

    handles = [
        plt.Line2D([0], [0], marker="o", linestyle="", markersize=7,
                   markerfacecolor=REGION_COLORS[r_], markeredgecolor="white",
                   markeredgewidth=0.6, label=r_)
        for r_ in REGION_ORDER
    ]
    fig.legend(handles=handles, loc="lower center", ncol=8, fontsize=8,
               frameon=False, bbox_to_anchor=(0.5, -0.04), columnspacing=1.3,
               handletextpad=0.3)
    fig.suptitle("Trained-rater reliability grounds the tutor's feedback",
                 fontsize=12.5, fontweight="bold", y=1.02)
    _save(fig, "fig6_reliability")


# ── Save helper ───────────────────────────────────────────────────────────────
def _save(fig, name):
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"{name}.{ext}", facecolor="white")
    plt.close(fig)
    print(f"  wrote {name}.png / .pdf")


def fig0_graphical_abstract():
    """Graphical abstract: the tool, the rater data, and the calibration idea."""
    import json
    import matplotlib.image as mpimg

    ink = "#141414"
    rel = json.loads(
        (Path("afidsvalidator") / "rater_reliability.json").read_text()
    )["landmarks"]
    fig = plt.figure(figsize=(13.5, 6.6))
    fig.patch.set_facecolor("white")
    fig.text(0.5, 0.95, "Teaching brains to see brains", ha="center",
             fontsize=20, fontweight="bold", color=ink)
    fig.text(0.5, 0.905, "An open, AI-guided platform for learning anatomical "
             "landmark placement, calibrated to a decade of expert rater data",
             ha="center", fontsize=10.5, color="#555")

    src = OUT / "ss_learn_hero.png"
    if src.exists():
        im = mpimg.imread(str(src))
        g = im[..., :3].mean(-1)
        rows = np.where(g.max(1) > 0.08)[0]
        cols = np.where(g.max(0) > 0.08)[0]
        y0 = rows.min()
        crop = im[y0:y0 + int(0.60 * (rows.max() - y0)), cols.min():cols.max()]
        axL = fig.add_axes([0.035, 0.10, 0.46, 0.74])
        axL.imshow(crop)
        axL.axis("off")
        axL.add_patch(plt.Rectangle((0, 0), crop.shape[1] - 1,
                      crop.shape[0] - 1, fill=False, ec="#00ff01", lw=2.5))
    fig.text(0.265, 0.055, "Browser MRI viewer + streaming AI tutor  \u00b7  no "
             "install  \u00b7  bring-your-own-key", ha="center", fontsize=9,
             color="#555", style="italic")

    def card(x, y, w, h):
        fig.patches.append(FancyBboxPatch((x, y), w, h,
            boxstyle="round,pad=0.006,rounding_size=0.012",
            transform=fig.transFigure, facecolor="#f5f6f8",
            edgecolor="#e2e2e6", lw=1, zorder=0))

    card(0.53, 0.60, 0.44, 0.235)
    fig.text(0.55, 0.795, "ANATOMY-FIRST TUTORING", fontsize=10.5,
             fontweight="bold", color="#2a78d6")
    for i, t in enumerate(["Teaches recognition, never coordinate lookup",
                           "Plain-language glosses for every anatomical term",
                           "Feedback adapts to the viewer (zoom / resolution)"]):
        fig.text(0.556, 0.745 - i * 0.043, "\u2022  " + t, fontsize=9.3,
                 color="#333")

    card(0.53, 0.335, 0.44, 0.235)
    fig.text(0.55, 0.53, "GROUNDED IN 492 EXPERT PLACEMENTS  \u00b7  132 SUBJECTS",
             fontsize=10, fontweight="bold", color="#882255")
    ax2 = fig.add_axes([0.556, 0.355, 0.40, 0.135])
    ax2.set_zorder(5)
    ax2.patch.set_alpha(0)
    rows2 = sorted([a for a in ABBR if a in rel], key=lambda a: rel[a]["p50"])
    ax2.bar(np.arange(len(rows2)), [rel[a]["p50"] for a in rows2],
            color=[REGION_COLORS[ABBR2REG[a]] for a in rows2], width=0.82)
    ax2.set_ylim(0, 1.6)
    ax2.set_xticks([0, len(rows2) - 1])
    ax2.set_xticklabels([rows2[0], rows2[-1]], fontsize=8)
    ax2.set_yticks([0.5, 1.0, 1.5])
    ax2.tick_params(labelsize=7)
    ax2.set_ylabel("median AFLE (mm)", fontsize=8)
    for s in ("top", "right"):
        ax2.spines[s].set_visible(False)

    card(0.53, 0.07, 0.44, 0.235)
    fig.text(0.55, 0.265,
             '"YOU vs. THE EXPERTS"  \u2014  THE SAME ERROR, JUDGED IN CONTEXT',
             fontsize=9.6, fontweight="bold", color=ink)
    ax3 = fig.add_axes([0.60, 0.095, 0.33, 0.135])
    ax3.set_zorder(5)
    ax3.patch.set_alpha(0)
    ax3.set_xlim(0, 3.2)
    ax3.set_ylim(-0.6, 1.6)
    for i, a in enumerate(("LIGO", "AC")):
        s = rel[a]
        y = 1 if i == 0 else 0
        ax3.plot([s["p10"], s["p90"]], [y, y], color="#bbb", lw=6,
                 solid_capstyle="round", alpha=0.6)
        ax3.plot(s["p50"], y, "o", color="#666", ms=6)
        ax3.text(-0.05, y, a, ha="right", va="center", fontsize=8.5,
                 fontweight="bold")
    ax3.axvline(1.2, color="#111", ls="--", lw=1)
    ax3.plot(1.2, 1, "o", color="#0ca30c", ms=11, mec="white")
    ax3.plot(1.2, 0, "o", color="#d03b3b", ms=11, mec="white")
    ax3.text(1.6, 1, "expert (42nd pct)", fontsize=8, color="#0ca30c",
             va="center", fontweight="bold")
    ax3.text(1.6, 0, "off-target (92nd pct)", fontsize=8, color="#d03b3b",
             va="center", fontweight="bold")
    ax3.text(1.2, 1.5, "a 1.2 mm placement", ha="center", fontsize=7.8,
             color="#333")
    ax3.axis("off")

    fig.text(0.5, 0.02, "Quality assurance and active learning as two sides "
             "of the same coin.", ha="center", fontsize=11, fontweight="bold",
             color=ink, style="italic")
    for ext in ("png", "pdf"):
        fig.savefig(OUT / f"fig0_graphical_abstract.{ext}",
                    facecolor="white", bbox_inches=None)
    plt.close(fig)
    print("  wrote fig0_graphical_abstract.png / .pdf")


if __name__ == "__main__":
    print("Generating figures →", OUT.resolve())
    fig0_graphical_abstract()
    fig1_interface()
    fig2_cycle()
    fig3_landmarks()
    fig4_validation()
    fig5_variability()
    fig6_reliability()
    print("Done.")
