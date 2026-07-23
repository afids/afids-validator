"""Render the two embedded raster assets for the graphical abstract.

    paper_figures/ga_brain.png   — glass-brain (lateral) with 32 region-coloured AFIDs, transparent
    paper_figures/ga_crop.png    — tight crop of the /learn interface (viewer + tutor)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path("paper_figures")
OUT.mkdir(exist_ok=True)

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
HUMAN_DIR = Path("afidsvalidator/afids-templates/human")
MNI_KEY = "tpl-MNI152NLin2009cAsym"


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


BRAIN = Path("instance/brain_cache/tpl-MNI152NLin2009cAsym_res-01_T1w.nii.gz")


def brain_asset():
    """A real mid-sagittal T1 slice with the 32 fiducials as bold markers."""
    import nibabel as nib

    mni = parse_fcsv(HUMAN_DIR / f"{MNI_KEY}_afids.fcsv")
    img = nib.as_closest_canonical(nib.load(str(BRAIN)))
    data = np.asarray(img.get_fdata(), dtype=np.float32)
    data /= np.percentile(data, 99.6)
    data = np.clip(data, 0, 1) ** 0.85
    aff = img.affine
    nx, ny, nz = data.shape
    y0, z0 = aff[1, 3], aff[2, 3]
    y1, z1 = y0 + aff[1, 1] * ny, z0 + aff[2, 2] * nz

    xi = int(round((0.0 - aff[0, 3]) / aff[0, 0]))  # mid-sagittal (x = 0)
    sl = data[xi, :, :].T  # -> (z, y)

    fig = plt.figure(figsize=(6, 5.2))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(
        sl,
        cmap="gray",
        origin="lower",
        extent=[y0, y1, z0, z1],
        aspect="equal",
        vmin=0,
        vmax=1,
        interpolation="bilinear",
    )
    # crop tight to the brain profile
    ys = [mni[a][1] for a in mni]
    zs = [mni[a][2] for a in mni]
    ax.set_xlim(y0 + 6, y1 - 6)
    ax.set_ylim(z0 + 20, z1 - 6)
    for region, abbrevs in REGION_MAP.items():
        pts = np.array([mni[a] for a in abbrevs if a in mni])
        ax.scatter(
            pts[:, 1],
            pts[:, 2],
            s=150,
            c=REGION_COLORS[region],
            edgecolors="white",
            linewidths=1.3,
            alpha=0.98,
            zorder=5,
        )
    ax.axis("off")
    fig.savefig(
        OUT / "ga_brain.png",
        transparent=True,
        dpi=400,
        bbox_inches="tight",
        pad_inches=0,
    )
    plt.close(fig)
    print("  wrote ga_brain.png")


def crop_asset():
    import matplotlib.image as mpimg

    src = OUT / "ss_learn_hero.png"
    if not src.exists():
        print("  (skip crop — no ss_learn_hero.png)")
        return
    im = mpimg.imread(str(src))
    g = im[..., :3].mean(-1) if im.ndim == 3 else im
    rows = np.where(g.max(1) > 0.08)[0]
    cols = np.where(g.max(0) > 0.08)[0]
    r0, r1 = rows.min(), rows.max()
    c0, c1 = cols.min(), cols.max()
    # keep the upper ~62% (viewer panels + tutor header/feedback), full width
    r1 = r0 + int(0.62 * (r1 - r0))
    crop = im[r0:r1, c0:c1]
    # convert to uint8 RGB and save
    arr = (np.clip(crop[..., :3], 0, 1) * 255).astype(np.uint8)
    from PIL import Image

    Image.fromarray(arr).save(OUT / "ga_crop.png")
    print(f"  wrote ga_crop.png  ({arr.shape[1]}x{arr.shape[0]})")


if __name__ == "__main__":
    brain_asset()
    crop_asset()
    print("Done.")
