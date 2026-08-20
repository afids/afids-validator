"""
AFIDS Template Analysis Script
Analyzes all human and macaca FCSV template files to compute inter-template variability.
"""

import os
import json
import csv
import math
from pathlib import Path
from collections import defaultdict

# ─── LANDMARK METADATA ────────────────────────────────────────────────────────

# Map from full description (as in desc column) to abbreviation
# Order matches fiducial index 1-32
LANDMARK_ABBREVS = [
    "AC",       # 1
    "PC",       # 2
    "ICS",      # 3 - infracollicular sulcus
    "PMJ",      # 4
    "SIPF",     # 5 - superior interpeduncular fossa
    "RSLMS",    # 6 - R superior LMS
    "LSLMS",    # 7 - L superior LMS
    "RILMS",    # 8 - R inferior LMS
    "LILMS",    # 9 - L inferior LMS
    "CUL",      # 10 - culmen
    "IMS",      # 11 - intermammillary sulcus
    "RMB",      # 12 - R MB
    "LMB",      # 13 - L MB
    "PG",       # 14 - pineal gland
    "RLVAC",    # 15 - R LV at AC
    "LLVAC",    # 16 - L LV at AC
    "RLVPC",    # 17 - R LV at PC
    "LLVPC",    # 18 - L LV at PC
    "GENU",     # 19 - genu of CC
    "SPLE",     # 20 - splenium of CC
    "RALTH",    # 21 - R AL temporal horn
    "LALTH",    # 22 - L AL temporal horn
    "RSAMTH",   # 23 - R superior AM temporal horn
    "LSAMTH",   # 24 - L superior AM temporal horn
    "RIAMTH",   # 25 - R inferior AM temporal horn
    "LIAMTH",   # 26 - L inferior AM temporal horn
    "RIGO",     # 27 - R indusium griseum origin
    "LIGO",     # 28 - L indusium griseum origin
    "RVOH",     # 29 - R ventral occipital horn
    "LVOH",     # 30 - L ventral occipital horn
    "ROSF",     # 31 - R olfactory sulcal fundus
    "LOSF",     # 32 - L olfactory sulcal fundus
]

REGION_MAP = {
    "Commissural":  ["AC", "PC"],
    "Brainstem":    ["ICS", "PMJ", "SIPF", "RSLMS", "LSLMS", "RILMS", "LILMS"],
    "Cerebellar":   ["CUL"],
    "Diencephalic": ["PG", "IMS", "RMB", "LMB"],
    "Ventricular":  ["RLVAC", "LLVAC", "RLVPC", "LLVPC"],
    "Callosal":     ["GENU", "SPLE"],
    "Temporal":     ["RALTH", "LALTH", "RSAMTH", "LSAMTH", "RIAMTH", "LIAMTH"],
    "Basal/Frontal":["RIGO", "LIGO", "RVOH", "LVOH", "ROSF", "LOSF"],
}

# Build reverse map: abbrev -> region
ABBREV_TO_REGION = {}
for region, abbrevs in REGION_MAP.items():
    for a in abbrevs:
        ABBREV_TO_REGION[a] = region


# ─── PARSING ──────────────────────────────────────────────────────────────────

def parse_fcsv(filepath):
    """
    Returns a list of 32 dicts: {abbrev, x, y, z, index}
    Indexed by fiducial order (1-based label column).
    """
    landmarks = []
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(",")
            if len(parts) < 13:
                continue
            try:
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                label_idx = int(parts[11]) - 1  # 0-based
                abbrev = LANDMARK_ABBREVS[label_idx]
                landmarks.append({
                    "abbrev": abbrev,
                    "index": label_idx + 1,
                    "x": x, "y": y, "z": z
                })
            except (ValueError, IndexError):
                continue
    return landmarks


def load_all_templates(directory):
    """
    Returns dict: {template_name: {abbrev: [x, y, z]}}
    """
    data = {}
    dirpath = Path(directory)
    for fcsv_file in sorted(dirpath.glob("*.fcsv")):
        template_name = fcsv_file.stem.replace("_afids", "")
        landmarks = parse_fcsv(fcsv_file)
        data[template_name] = {lm["abbrev"]: [lm["x"], lm["y"], lm["z"]] for lm in landmarks}
    return data


# ─── STATISTICS ───────────────────────────────────────────────────────────────

def mean(vals):
    return sum(vals) / len(vals)

def std(vals):
    m = mean(vals)
    variance = sum((v - m) ** 2 for v in vals) / len(vals)
    return math.sqrt(variance)

def euclidean(a, b):
    return math.sqrt(sum((ai - bi) ** 2 for ai, bi in zip(a, b)))

def compute_variability(template_data):
    """
    For each landmark, compute across templates:
    - mean_x, mean_y, mean_z
    - std_x, std_y, std_z
    - mean Euclidean distance from each template to centroid
    - max pairwise Euclidean distance
    - std of Euclidean distances (used for ranking)
    """
    templates = list(template_data.keys())
    results = {}

    for abbrev in LANDMARK_ABBREVS:
        coords = []
        for tpl in templates:
            if abbrev in template_data[tpl]:
                coords.append((tpl, template_data[tpl][abbrev]))

        if not coords:
            continue

        xs = [c[1][0] for c in coords]
        ys = [c[1][1] for c in coords]
        zs = [c[1][2] for c in coords]

        cx = mean(xs)
        cy = mean(ys)
        cz = mean(zs)

        dists_to_centroid = [euclidean(c[1], [cx, cy, cz]) for c in coords]

        # Max pairwise distance
        max_pair_dist = 0.0
        max_pair = ("", "")
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                d = euclidean(coords[i][1], coords[j][1])
                if d > max_pair_dist:
                    max_pair_dist = d
                    max_pair = (coords[i][0], coords[j][0])

        results[abbrev] = {
            "abbrev": abbrev,
            "region": ABBREV_TO_REGION.get(abbrev, "Unknown"),
            "n_templates": len(coords),
            "centroid_x": round(cx, 4),
            "centroid_y": round(cy, 4),
            "centroid_z": round(cz, 4),
            "std_x": round(std(xs), 4),
            "std_y": round(std(ys), 4),
            "std_z": round(std(zs), 4),
            "mean_dist_to_centroid": round(mean(dists_to_centroid), 4),
            "std_dist_to_centroid": round(std(dists_to_centroid), 4),
            "max_pairwise_dist": round(max_pair_dist, 4),
            "max_pair_templates": f"{max_pair[0]} vs {max_pair[1]}",
            "per_template_dist": {tpl: round(d, 4) for (tpl, _), d in zip(coords, dists_to_centroid)},
        }

    return results


# ─── MAIN ─────────────────────────────────────────────────────────────────────

HUMAN_DIR  = "/Users/alaataha/projects_claude/afids-validator/afidsvalidator/afids-templates/human"
MACACA_DIR = "/Users/alaataha/projects_claude/afids-validator/afidsvalidator/afids-templates/macaca"

print("=" * 80)
print("AFIDS TEMPLATE ANALYSIS")
print("=" * 80)

# ── HUMAN TEMPLATES ───────────────────────────────────────────────────────────
print("\n\nLOADING HUMAN TEMPLATES...")
human_data = load_all_templates(HUMAN_DIR)
print(f"  Templates found: {len(human_data)}")
for t in sorted(human_data.keys()):
    n = len(human_data[t])
    print(f"    {t}: {n} landmarks")

human_var = compute_variability(human_data)

# ── TABLE 1: MNI152NLin2009cAsym coordinates ──────────────────────────────────
mni_key = "tpl-MNI152NLin2009cAsym"
print("\n\n" + "=" * 80)
print("TABLE 1: MNI152NLin2009cAsym COORDINATES FOR ALL 32 LANDMARKS")
print("=" * 80)
print(f"{'#':<4} {'Abbrev':<10} {'Region':<15} {'X':>10} {'Y':>10} {'Z':>10}")
print("-" * 65)
for i, abbrev in enumerate(LANDMARK_ABBREVS, 1):
    if mni_key in human_data and abbrev in human_data[mni_key]:
        c = human_data[mni_key][abbrev]
        region = ABBREV_TO_REGION.get(abbrev, "Unknown")
        print(f"{i:<4} {abbrev:<10} {region:<15} {c[0]:>10.4f} {c[1]:>10.4f} {c[2]:>10.4f}")

# ── TABLE 2: Inter-template variability for human templates ───────────────────
print("\n\n" + "=" * 80)
print("TABLE 2: INTER-TEMPLATE VARIABILITY (15 HUMAN TEMPLATES)")
print("=" * 80)
print(f"{'#':<4} {'Abbrev':<10} {'Region':<15} {'Cx':>8} {'Cy':>8} {'Cz':>8} "
      f"{'SDx':>7} {'SDy':>7} {'SDz':>7} {'MnDist':>8} {'StdDist':>9} {'MaxPair':>9}")
print("-" * 110)

for i, abbrev in enumerate(LANDMARK_ABBREVS, 1):
    if abbrev not in human_var:
        continue
    v = human_var[abbrev]
    print(f"{i:<4} {abbrev:<10} {v['region']:<15} "
          f"{v['centroid_x']:>8.2f} {v['centroid_y']:>8.2f} {v['centroid_z']:>8.2f} "
          f"{v['std_x']:>7.3f} {v['std_y']:>7.3f} {v['std_z']:>7.3f} "
          f"{v['mean_dist_to_centroid']:>8.3f} {v['std_dist_to_centroid']:>9.3f} "
          f"{v['max_pairwise_dist']:>9.3f}")

# ── TABLE 3: Ranking by inter-template variability ────────────────────────────
print("\n\n" + "=" * 80)
print("TABLE 3: LANDMARKS RANKED BY INTER-TEMPLATE VARIABILITY")
print("  (metric: mean Euclidean distance to centroid across templates)")
print("=" * 80)

ranked = sorted(human_var.values(), key=lambda v: v["mean_dist_to_centroid"], reverse=True)

print(f"{'Rank':<6} {'Abbrev':<10} {'Region':<15} {'MnDist(mm)':>12} {'MaxPair(mm)':>13} {'Most Variable Pair'}")
print("-" * 90)
for rank, v in enumerate(ranked, 1):
    print(f"{rank:<6} {v['abbrev']:<10} {v['region']:<15} "
          f"{v['mean_dist_to_centroid']:>12.3f} {v['max_pairwise_dist']:>13.3f}  "
          f"{v['max_pair_templates']}")

# ── TABLE 4: Per-template distance to centroid for each landmark ──────────────
print("\n\n" + "=" * 80)
print("TABLE 4: DISTANCE TO CENTROID (mm) — EACH TEMPLATE × EACH LANDMARK")
print("=" * 80)

templates_sorted = sorted(human_data.keys())
header = f"{'Abbrev':<10}" + "".join(f"{t.replace('tpl-',''):<22}" for t in templates_sorted)
print(header)
print("-" * (10 + 22 * len(templates_sorted)))

for abbrev in LANDMARK_ABBREVS:
    if abbrev not in human_var:
        continue
    row = f"{abbrev:<10}"
    for tpl in templates_sorted:
        d = human_var[abbrev]["per_template_dist"].get(tpl, float("nan"))
        row += f"{d:<22.3f}"
    print(row)

# ── MACACA ANALYSIS ───────────────────────────────────────────────────────────
print("\n\n" + "=" * 80)
print("MACACA TEMPLATE ANALYSIS (6 TEMPLATES)")
print("=" * 80)
mac_data = load_all_templates(MACACA_DIR)
print(f"  Templates found: {len(mac_data)}")
for t in sorted(mac_data.keys()):
    print(f"    {t}: {len(mac_data[t])} landmarks")

mac_var = compute_variability(mac_data)

print("\n\nMACACQ INTER-TEMPLATE VARIABILITY:")
print(f"{'#':<4} {'Abbrev':<10} {'Region':<15} {'Cx':>8} {'Cy':>8} {'Cz':>8} "
      f"{'SDx':>7} {'SDy':>7} {'SDz':>7} {'MnDist':>8} {'MaxPair':>9}")
print("-" * 100)
for i, abbrev in enumerate(LANDMARK_ABBREVS, 1):
    if abbrev not in mac_var:
        continue
    v = mac_var[abbrev]
    print(f"{i:<4} {abbrev:<10} {v['region']:<15} "
          f"{v['centroid_x']:>8.2f} {v['centroid_y']:>8.2f} {v['centroid_z']:>8.2f} "
          f"{v['std_x']:>7.3f} {v['std_y']:>7.3f} {v['std_z']:>7.3f} "
          f"{v['mean_dist_to_centroid']:>8.3f} "
          f"{v['max_pairwise_dist']:>9.3f}")

print("\n\nMACACQ LANDMARKS RANKED BY VARIABILITY:")
ranked_mac = sorted(mac_var.values(), key=lambda v: v["mean_dist_to_centroid"], reverse=True)
print(f"{'Rank':<6} {'Abbrev':<10} {'Region':<15} {'MnDist(mm)':>12} {'MaxPair(mm)':>13}")
print("-" * 60)
for rank, v in enumerate(ranked_mac, 1):
    print(f"{rank:<6} {v['abbrev']:<10} {v['region']:<15} "
          f"{v['mean_dist_to_centroid']:>12.3f} {v['max_pairwise_dist']:>13.3f}")

# ── TABLE 5: Region-level summary (human) ─────────────────────────────────────
print("\n\n" + "=" * 80)
print("TABLE 5: REGION-LEVEL VARIABILITY SUMMARY (HUMAN)")
print("=" * 80)

region_stats = defaultdict(list)
for abbrev, v in human_var.items():
    region_stats[v["region"]].append(v["mean_dist_to_centroid"])

print(f"{'Region':<18} {'N LMs':>6} {'Mean MnDist':>12} {'Max MnDist':>12} {'Min MnDist':>12}")
print("-" * 65)
region_rows = []
for region, dists in region_stats.items():
    region_rows.append((region, len(dists), mean(dists), max(dists), min(dists)))
region_rows.sort(key=lambda r: r[2], reverse=True)
for region, n, mn, mx, mi in region_rows:
    print(f"{region:<18} {n:>6} {mn:>12.3f} {mx:>12.3f} {mi:>12.3f}")

# ── INTERESTING PATTERNS ──────────────────────────────────────────────────────
print("\n\n" + "=" * 80)
print("INTERESTING PATTERNS & OBSERVATIONS")
print("=" * 80)

# Top 5 most variable
top5 = ranked[:5]
bottom5 = ranked[-5:]
print(f"\nTop 5 MOST variable human landmarks (mean dist to centroid):")
for v in top5:
    print(f"  {v['abbrev']:<10} {v['region']:<15}  {v['mean_dist_to_centroid']:.3f} mm  "
          f"(max pairwise: {v['max_pairwise_dist']:.3f} mm)")

print(f"\nTop 5 LEAST variable human landmarks:")
for v in bottom5:
    print(f"  {v['abbrev']:<10} {v['region']:<15}  {v['mean_dist_to_centroid']:.3f} mm  "
          f"(max pairwise: {v['max_pairwise_dist']:.3f} mm)")

# Compare human vs macaca overall
human_overall = mean([v["mean_dist_to_centroid"] for v in human_var.values()])
mac_overall   = mean([v["mean_dist_to_centroid"] for v in mac_var.values()])
print(f"\nOverall mean inter-template variability:")
print(f"  Human  ({len(human_data)} templates): {human_overall:.3f} mm")
print(f"  Macaca  ({len(mac_data)} templates): {mac_overall:.3f} mm")

# Bilateral symmetry check (human, MNI2009cAsym)
print(f"\nBilateral asymmetry check in MNI152NLin2009cAsym:")
bilateral_pairs = [
    ("RSLMS", "LSLMS"), ("RILMS", "LILMS"),
    ("RMB", "LMB"), ("RLVAC", "LLVAC"), ("RLVPC", "LLVPC"),
    ("RALTH", "LALTH"), ("RSAMTH", "LSAMTH"), ("RIAMTH", "LIAMTH"),
    ("RIGO", "LIGO"), ("RVOH", "LVOH"), ("ROSF", "LOSF"),
]
if mni_key in human_data:
    mni = human_data[mni_key]
    print(f"  {'Pair':<22} {'|x_R|':>8} {'|x_L|':>8} {'Asym(mm)':>10}")
    print(f"  {'-'*55}")
    for ra, la in bilateral_pairs:
        if ra in mni and la in mni:
            cr = mni[ra]; cl = mni[la]
            asym = euclidean(cr, [- cl[0], cl[1], cl[2]])  # mirror L across midline
            print(f"  {ra+'/'+la:<22} {abs(cr[0]):>8.2f} {abs(cl[0]):>8.2f} {asym:>10.3f}")

print("\n\nDone.")
