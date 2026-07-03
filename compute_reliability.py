"""Compute a per-landmark rater-reliability prior from the afids-data release.

The AFIDs multi-rater data release (Taha et al., 2023, Sci Data 10:449) ships,
for each subject, the placements of several trained raters plus a consensus
"groundtruth". This script computes, for each of the 32 AFIDs, the distribution
of anatomical fiducial localization error (AFLE) — the Euclidean distance from a
rater's placement to the consensus — and writes it to
``afidsvalidator/rater_reliability.json``. That prior lets the guided-learning
tutor calibrate its feedback to how hard each landmark actually is for humans
(e.g. 1 mm on the anterior commissure is poor, but 1 mm on the indusium griseum
origin is expert-level).

Because AFLE is a distance between two placements of the *same* image, it is
invariant to the FCSV coordinate convention (LPS vs RAS), so no conversion is
needed.

Usage
-----
Fetch the annotation FCSVs (the landmark annotations are CC-BY; only the imaging
is DUA-gated), then point this script at the directory that contains the dataset
folders::

    datalad install -r https://github.com/afids/afids-data.git
    # or clone the per-dataset annotation repos directly, e.g.
    #   git clone https://github.com/afids/AFIDs-HCP.git
    #   git clone https://github.com/afids/AFIDs-OASIS.git

    python compute_reliability.py --data-dir /path/to/afids-datasets

The script scans recursively for the release's derivative layout
``derivatives/afids_rater/**/*desc-rater*_afids.fcsv`` (per-rater placements) and
``derivatives/afids_groundtruth/**/*_afids.fcsv`` (consensus), so it works
against the super-dataset or against individually cloned dataset repos.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
from collections import defaultdict

import numpy as np

# AFIDs 1-based protocol order → abbreviation
ABBR = [
    "AC", "PC", "ICS", "PMJ", "SIPF", "RSLMS", "LSLMS", "RILMS", "LILMS",
    "CUL", "IMS", "RMB", "LMB", "PG", "RLVAC", "LLVAC", "RLVPC", "LLVPC",
    "GENU", "SPLE", "RALTH", "LALTH", "RSAMTH", "LSAMTH", "RIAMTH", "LIAMTH",
    "RIGO", "LIGO", "RVOH", "LVOH", "ROSF", "LOSF",
]


def parse_fcsv(path: str) -> dict[int, np.ndarray]:
    """Return {landmark_number: [x, y, z]} from a Slicer FCSV file.

    Returns an empty dict for files that cannot be read (e.g. unfetched
    git-annex pointers), so a partial dataset never aborts the run.
    """
    out: dict[int, np.ndarray] = {}
    try:
        fh = open(path, encoding="utf-8", errors="ignore")
    except OSError:
        return out
    with fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            p = line.split(",")
            if len(p) < 13:
                continue
            try:
                num = int(p[11])
                if 1 <= num <= 32:
                    out[num] = np.array(
                        [float(p[1]), float(p[2]), float(p[3])])
            except (ValueError, IndexError):
                continue
    return out


def _image_key(basename: str, rater_token: str) -> str:
    return basename.replace(f"_desc-{rater_token}", "").replace(
        "_afids.fcsv", "")


def collect_errors(data_dir: str):
    """Return {landmark_number: [afle, …]} across all subjects/datasets."""
    gt: dict[str, dict[int, np.ndarray]] = {}
    for f in glob.glob(
        os.path.join(data_dir, "**", "afids_groundtruth", "**", "*_afids.fcsv"),
        recursive=True,
    ):
        key = _image_key(os.path.basename(f), "groundtruth")
        gt[key] = parse_fcsv(f)

    errors: dict[int, list[float]] = defaultdict(list)
    n_images: set[str] = set()
    rater_files = glob.glob(
        os.path.join(data_dir, "**", "afids_rater", "**", "*desc-rater*_afids.fcsv"),
        recursive=True,
    )
    for f in rater_files:
        base = os.path.basename(f)
        m = re.search(r"desc-(rater[^_]+)", base)
        if not m:
            continue
        key = _image_key(base, m.group(1))
        if key not in gt:
            continue
        n_images.add(key)
        placed = parse_fcsv(f)
        for num in range(1, 33):
            if num in placed and num in gt[key]:
                errors[num].append(
                    float(np.linalg.norm(placed[num] - gt[key][num])))
    return errors, len(rater_files), len(n_images)


def summarize(errors, n_files, n_images) -> dict:
    landmarks = {}
    for num in range(1, 33):
        v = np.array(errors.get(num, []))
        if v.size == 0:
            continue
        landmarks[ABBR[num - 1]] = {
            "n": int(v.size),
            "mean": round(float(v.mean()), 3),
            "sd": round(float(v.std()), 3),
            "p10": round(float(np.percentile(v, 10)), 3),
            "p25": round(float(np.percentile(v, 25)), 3),
            "p50": round(float(np.median(v)), 3),
            "p75": round(float(np.percentile(v, 75)), 3),
            "p90": round(float(np.percentile(v, 90)), 3),
        }
    allv = np.concatenate([np.array(errors[n]) for n in errors]) if errors \
        else np.array([])
    glob_stats = {
        "median": round(float(np.median(allv)), 3),
        "mean": round(float(allv.mean()), 3),
        "sd": round(float(allv.std()), 3),
        "within_1mm": round(float(np.mean(allv < 1)), 3),
        "within_2mm": round(float(np.mean(allv < 2)), 3),
    }
    return {
        "meta": {
            "source": "afids-data release (Taha et al., 2023, Sci Data 10:449)",
            "reference": "per-subject consensus groundtruth",
            "metric": "Euclidean distance rater -> groundtruth (mm), "
                      "convention-invariant",
            "n_rater_files": n_files,
            "n_images": n_images,
        },
        "global": glob_stats,
        "landmarks": landmarks,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--data-dir", required=True,
        help="Directory containing afids-data dataset folders "
             "(each with derivatives/afids_rater and afids_groundtruth).")
    ap.add_argument(
        "--out",
        default=os.path.join(
            os.path.dirname(__file__), "afidsvalidator", "rater_reliability.json"),
        help="Output JSON path.")
    args = ap.parse_args()

    errors, n_files, n_images = collect_errors(args.data_dir)
    if not errors:
        raise SystemExit(
            f"No rater placements found under {args.data_dir!r}. Expected the "
            "afids-data derivative layout (derivatives/afids_rater/…).")
    report = summarize(errors, n_files, n_images)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    g = report["global"]
    print(f"Images: {n_images} | rater files: {n_files}")
    print(f"Global AFLE: median {g['median']} mm, mean {g['mean']} mm; "
          f"{g['within_1mm']*100:.0f}% within 1 mm")
    print(f"Wrote {args.out} ({len(report['landmarks'])} landmarks)")


if __name__ == "__main__":
    main()
