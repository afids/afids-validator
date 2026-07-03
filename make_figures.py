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
    data, aff, ext = load_brain()
    mni = parse_fcsv(HUMAN_DIR / f"{MNI_KEY}_afids.fcsv")

    def mip(axis):
        m = data.max(axis=axis)
        return (m / m.max()) ** 0.7  # brighten silhouette

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.8))
    fig.subplots_adjust(wspace=0.16)
    panels = [
        ("Sagittal", mip(0), "y", "z", ("Posterior — Anterior", "Inferior — Superior"),
         lambda c: (c[1], c[2])),
        ("Coronal", mip(1), "x", "z", ("Left — Right", "Inferior — Superior"),
         lambda c: (c[0], c[2])),
        ("Axial", mip(2), "x", "y", ("Left — Right", "Posterior — Anterior"),
         lambda c: (c[0], c[1])),
    ]
    for ax, (title, m, ha, va, (xl, yl), proj) in zip(axes, panels):
        ax.imshow(m.T, extent=[*ext[ha], *ext[va]], origin="lower", cmap="gray",
                  aspect="equal", vmin=0, vmax=1)
        for a, c in mni.items():
            px, py = proj(c)
            ax.scatter(px, py, s=46, c=REGION_COLORS[ABBR2REG[a]],
                       edgecolors="white", linewidths=0.8, zorder=3)
        for a in ("AC", "PC"):
            px, py = proj(mni[a])
            ax.annotate(a, (px, py), textcoords="offset points", xytext=(6, 5),
                        color="white", fontsize=7.5, fontweight="bold", zorder=4)
        ax.set_title(title, fontsize=11, color=INK)
        ax.set_xlabel(xl, fontsize=7.5, color="#666666")
        ax.set_ylabel(yl, fontsize=7.5, color="#666666")
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color("#dddddd")

    handles = [
        plt.Line2D([0], [0], marker="o", linestyle="", markersize=8,
                   markerfacecolor=REGION_COLORS[r], markeredgecolor="white",
                   markeredgewidth=0.8, label=r)
        for r in REGION_ORDER
    ]
    fig.legend(handles=handles, loc="lower center", ncol=8, fontsize=8.5,
               frameon=False, bbox_to_anchor=(0.5, -0.04), columnspacing=1.4,
               handletextpad=0.3)
    fig.suptitle("The 32 AFIDs landmarks on the MNI152NLin2009cAsym T1w template",
                 fontsize=12.5, fontweight="bold", y=1.03)
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
    data, aff, ext = load_brain()
    mni = parse_fcsv(HUMAN_DIR / f"{MNI_KEY}_afids.fcsv")
    GREEN, BG, CARD = "#00ff01", "#0b0b0b", "#0f0f0f"

    fig = plt.figure(figsize=(12.5, 6.8))
    fig.patch.set_facecolor("white")

    # header band
    fig.text(0.065, 0.955, "Guided Learning Mode", fontsize=14, fontweight="bold",
             color=INK)
    fig.text(0.065, 0.922,
             "Anatomy-first AI tutoring inside a browser MRI viewer — no install, "
             "bring-your-own-key, works on any device.",
             fontsize=8.8, color="#666666")

    # ── viewer panel ──────────────────────────────────────────────────────────
    axv = fig.add_axes([0.065, 0.115, 0.53, 0.75])
    axv.set_facecolor(BG)
    ac = mni["AC"]
    k = int(round(world_to_vox(aff, ac)[2]))
    sl = (data[:, :, k] ** 0.85)
    axv.imshow(sl.T, extent=[*ext["x"], *ext["y"]], origin="lower",
               cmap="gray", aspect="equal", vmin=0, vmax=1)
    ref = (ac[0], ac[1])
    placed = (ac[0] + 2.2, ac[1] - 1.4)
    axv.axhline(placed[1], color=GREEN, lw=0.7, alpha=0.65)
    axv.axvline(placed[0], color=GREEN, lw=0.7, alpha=0.65)
    axv.scatter(*ref, s=150, marker="D", facecolors="none", edgecolors="#ffcc00",
                linewidths=1.8, zorder=5)
    axv.scatter(*placed, s=110, marker="o", facecolors="none", edgecolors="#ff4040",
                linewidths=2.0, zorder=5)
    axv.annotate("expert reference", ref, textcoords="offset points", xytext=(9, 9),
                 color="#ffcc00", fontsize=8, fontweight="bold")
    axv.annotate("your placement", placed, textcoords="offset points", xytext=(7, -15),
                 color="#ff6060", fontsize=8, fontweight="bold")
    axv.set_xlim(-70, 70)
    axv.set_ylim(-104, 74)
    axv.set_xticks([]); axv.set_yticks([])
    for s in axv.spines.values():
        s.set_color("#2a3a2a"); s.set_linewidth(1.5)
    axv.set_title("MRI VIEWER   ·   Landmark 1 / 32", color=GREEN, fontsize=9.5,
                  fontweight="bold", loc="left", fontfamily="monospace", pad=6)

    # action buttons + toolbar
    axtb = fig.add_axes([0.065, 0.03, 0.53, 0.075])
    axtb.axis("off"); axtb.set_xlim(0, 10); axtb.set_ylim(0, 2)
    actions = [("● Place fiducial", GREEN, "#00ff01"),
               ("◆ Show reference", "#ffaa00", "#332600"),
               ("Next →", GREEN, "#0a200a")]
    ax_x = 0
    for lab, fg, _ in actions:
        w = 2.35 if "Place" in lab else 2.35 if "reference" in lab else 1.6
        axtb.add_patch(FancyBboxPatch((ax_x, 1.05), w, 0.8,
                       boxstyle="round,pad=0.02,rounding_size=0.12",
                       linewidth=1.2, edgecolor=fg, facecolor="#111111"))
        axtb.text(ax_x + w / 2, 1.45, lab, ha="center", va="center", fontsize=7,
                  color=fg, fontfamily="monospace", fontweight="bold")
        ax_x += w + 0.25
    tools = ["RAS −1.2·3.4·0.8", "ZOOM 2.4×", "RES 1mm", "RAD", "◉ Go to landmark"]
    tx = [0, 2.55, 3.75, 4.8, 5.65]
    tw = [2.4, 1.1, 0.95, 0.85, 2.0]
    for lab, x, w in zip(tools, tx, tw):
        axtb.add_patch(FancyBboxPatch((x, 0.05), w, 0.72,
                       boxstyle="round,pad=0.02,rounding_size=0.1",
                       linewidth=1, edgecolor="#2a2a2a", facecolor="#141414"))
        axtb.text(x + w / 2, 0.41, lab, ha="center", va="center", fontsize=6.2,
                  color=GREEN if "Go to" in lab else "#a8a8a8", fontfamily="monospace")

    # ── chat panel ────────────────────────────────────────────────────────────
    axc = fig.add_axes([0.63, 0.03, 0.325, 0.845])
    axc.set_facecolor(CARD)
    axc.set_xlim(0, 10); axc.set_ylim(0, 10)
    axc.set_xticks([]); axc.set_yticks([])
    for s in axc.spines.values():
        s.set_color("#1e1e1e")
    axc.text(0.3, 9.78, "AI TUTOR", color="#8a8a8a", fontsize=9.5, fontweight="bold",
             fontfamily="monospace", va="top")
    axc.text(9.7, 9.8, "gpt-4o  ⚙", color="#9a9a9a", fontsize=7.2,
             fontfamily="monospace", va="top", ha="right")
    # landmark header card
    axc.add_patch(FancyBboxPatch((0.3, 8.75), 9.4, 0.7,
                  boxstyle="round,pad=0.03", linewidth=0, facecolor="#151515"))
    axc.add_patch(plt.Rectangle((0.3, 8.75), 0.07, 0.7, color=GREEN))
    axc.text(0.62, 9.1, "01  AC", color=GREEN, fontsize=9, fontweight="bold",
             va="center", fontfamily="monospace")
    axc.text(2.35, 9.1, "Anterior Commissure", color="#bbbbbb", fontsize=7.8,
             va="center")

    def bubble(role, ytop, h, text):
        face = "#141414" if role == "assistant" else "#171717"
        edge = GREEN if role == "assistant" else "#4a4a4a"
        tag = "AI tutor" if role == "assistant" else "You"
        axc.text(0.32, ytop + 0.16, tag, color=edge if role == "assistant" else "#777777",
                 fontsize=5.8, fontfamily="monospace", va="bottom")
        axc.add_patch(FancyBboxPatch((0.3, ytop - h), 9.4, h,
                      boxstyle="round,pad=0.03", linewidth=0, facecolor=face))
        axc.add_patch(plt.Rectangle((0.3, ytop - h), 0.07, h, color=edge))
        axc.text(0.6, ytop - 0.12, text,
                 color="#d3d3d3" if role == "assistant" else "#9a9a9a",
                 fontsize=6.7, va="top", linespacing=1.34,
                 style="italic" if role == "user" else "normal")

    bubble("assistant", 8.35, 1.5,
           "The anterior commissure is a compact white-matter bundle\n"
           "crossing the midline at the base of the septum pellucidum.\n"
           "On this axial slice, find the small bright band just anterior\n"
           "to the columns of the fornix.")
    # quality badge
    axc.add_patch(FancyBboxPatch((0.3, 5.95), 4.7, 0.55, boxstyle="round,pad=0.02",
                  linewidth=1.2, edgecolor="#ffaa00", facecolor="#1a1000"))
    axc.text(0.55, 6.22, "△  Fair  —  2.6 mm", color="#ffaa00", fontsize=7.6,
             va="center", fontfamily="monospace", fontweight="bold")
    bubble("assistant", 5.65, 1.72,
           "Not quite — 2.6 mm off. Your placement sits on the fornix\n"
           "columns, just posterior to the AC. The AC is the brighter\n"
           "bundle immediately anterior. You're at 2 mm resolution —\n"
           "switch to 1 mm (RES) and zoom in to resolve the border.")
    bubble("user", 3.5, 0.62, "why is it hard to see on T1?")
    bubble("assistant", 2.65, 1.35,
           "On T1 the AC has similar intensity to surrounding white\n"
           "matter. Use the coronal plane at the midline, where it\n"
           "appears as a distinct oval crossing between the hemispheres.")

    # input row
    axc.add_patch(FancyBboxPatch((0.3, 0.2), 8.2, 0.56, boxstyle="round,pad=0.02",
                  linewidth=1, edgecolor="#242424", facecolor="#151515"))
    axc.text(0.55, 0.48, "Ask a question about this landmark…", color="#6a6a6a",
             fontsize=6.7, va="center")
    axc.add_patch(FancyBboxPatch((8.7, 0.2), 1.0, 0.56, boxstyle="round,pad=0.02",
                  linewidth=0, facecolor=GREEN))
    axc.plot(9.2, 0.48, marker=">", markersize=9, color="#000000")

    # progress tracker (above the chat card, no overlap)
    axp = fig.add_axes([0.63, 0.915, 0.325, 0.03])
    axp.axis("off"); axp.set_xlim(0, 32); axp.set_ylim(0, 1)
    for i in range(32):
        axp.add_patch(plt.Rectangle((i + 0.12, 0.0), 0.76, 1.0,
                      color=GREEN if i == 0 else "#2b2b2b"))
    axp.text(0, 1.5, "SESSION PROGRESS   1 / 32", color="#8a8a8a", fontsize=7,
             fontfamily="monospace", va="bottom")

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


if __name__ == "__main__":
    print("Generating figures →", OUT.resolve())
    fig1_interface()
    fig2_cycle()
    fig3_landmarks()
    fig4_validation()
    fig5_variability()
    fig6_reliability()
    print("Done.")
