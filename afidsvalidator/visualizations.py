"""Utilities for generating AFIDs-related graphics"""

import plotly.graph_objects as go

from afidsvalidator.model import EXPECTED_DESCS

# Landmark abbreviations grouped by neuroanatomical region.
# Each abbreviation matches the attribute name on the Afids object (desc[-1]).
LANDMARK_REGIONS = {
    "Commissural": ["AC", "PC"],
    "Brainstem": ["ICS", "PMJ", "SIPF", "RSLMS", "LSLMS", "RILMS", "LILMS"],
    "Cerebellar": ["CUL"],
    "Diencephalic": ["PG", "IMS", "RMB", "LMB"],
    "Ventricular": ["RLVAC", "LLVAC", "RLVPC", "LLVPC"],
    "Callosal": ["GENU", "SPLE"],
    "Temporal": ["RALTH", "LALTH", "RSAMTH", "LSAMTH", "RIAMTH", "LIAMTH"],
    "Basal/Frontal": ["RIGO", "LIGO", "RVOH", "LVOH", "ROSF", "LOSF"],
}


def gen_connecting_lines(ref_afids, user_afids):
    """Assemble points from each fcsv into pairs.

    Parameters
    ----------
    ref_afids : Afids
        Reference AFiDs object.
    user_afids : Afids
        User-provided AFIDs object.

    Returns
    -------
    list of list of dict
        A list, where each element is a pair of x,y,z dicts to respective
        AFIDs coordinates.
    """
    connecting_lines = []
    for ref_entry, user_entry in [
        (
            getattr(ref_afids, desc[-1]),
            getattr(user_afids, desc[-1]),
        )
        for desc in EXPECTED_DESCS
    ]:
        connecting_lines.append(
            [
                {
                    "x": ref_entry.x,
                    "y": ref_entry.y,
                    "z": ref_entry.z,
                },
                {
                    "x": user_entry.x,
                    "y": user_entry.y,
                    "z": user_entry.z,
                },
            ]
        )
    return connecting_lines


def calculate_magnitudes(connecting_lines):
    """Calculate the segment points and magnitude of each line.

    Parameters
    ----------
    connecting_lines : list of list of dict
        A list, where each element is a pair of x,y,z dicts to respective
        AFIDs coordinates.

    Returns
    -------
    lines_x, lines_y, lines_z : list of float or none
        A list where every four elements contains the three points describing
        the position of a line segment along one axis, then None.
    lines_magnitudes : list of float
        A list where every four elements contains the Euclidean distance of
        the line three times, then 0.
    """
    lines_x = []
    lines_y = []
    lines_z = []
    lines_magnitudes = []
    for line in connecting_lines:
        lines_x += [
            line[0]["x"],
            (line[0]["x"] + line[1]["x"]) / 2,
            line[1]["x"],
            None,
        ]

        lines_y += [
            line[0]["y"],
            (line[0]["y"] + line[1]["y"]) / 2,
            line[1]["y"],
            None,
        ]

        lines_z += [
            line[0]["z"],
            (line[0]["z"] + line[1]["z"]) / 2,
            line[1]["z"],
            None,
        ]

        distance = (
            (line[0]["x"] - line[1]["x"]) ** 2
            + (line[0]["y"] - line[1]["y"]) ** 2
            + (line[0]["z"] - line[1]["z"]) ** 2
        ) ** 0.5
        lines_magnitudes += [distance, distance, distance, 0]

    return (lines_x, lines_y, lines_z, lines_magnitudes)


def generate_3d_scatter(ref_afids, user_afids):
    """Generate an HTML snippet containing a 3D scatter plot.

    Parameters
    ----------
    ref_afids : Afids
        Reference AFIDS object.
    user_afids : Afids
        User-provided AFIDs object.

    Returns
    -------
    str
        HTML snippet containing a 3D scatter plot illustrating the distance
        between pairs of provided AFIDs.
    """

    connecting_lines = gen_connecting_lines(ref_afids, user_afids)

    lines_x, lines_y, lines_z, lines_magnitudes = calculate_magnitudes(
        connecting_lines
    )

    ids = [desc[-1] for desc in EXPECTED_DESCS]

    dset1 = [
        go.Scatter3d(
            x=[getattr(ref_afids, desc[-1]).x for desc in EXPECTED_DESCS],
            y=[getattr(ref_afids, desc[-1]).y for desc in EXPECTED_DESCS],
            z=[getattr(ref_afids, desc[-1]).z for desc in EXPECTED_DESCS],
            showlegend=True,
            mode="markers",
            marker={
                "size": 4,
                "color": "rgba(255,191,31,0.9)",
                "line": {"width": 1.5, "color": "rgba(50,50,50,1.0)"},
            },
            hovertemplate=(
                "%{text}<br>x: %{x:.4f}<br>y: %{y:.4f}<br>" + "z: %{z:.4f}"
            ),
            text=[f"<b>{ids[int(i)]}</b>" for i in range(len(ids))],
            name="Template AFIDs",
        ),
        go.Scatter3d(
            x=[getattr(user_afids, desc[-1]).x for desc in EXPECTED_DESCS],
            y=[getattr(user_afids, desc[-1]).y for desc in EXPECTED_DESCS],
            z=[getattr(user_afids, desc[-1]).z for desc in EXPECTED_DESCS],
            showlegend=True,
            mode="markers",
            marker={
                "size": 4,
                "color": "rgba(0,0,0,0.9)",
                "line": {"width": 1.5, "color": "rgba(50,50,50,1.0)"},
            },
            hovertemplate=(
                "%{text}<br>x: %{x:.4f}<br>y: %{y:.4f}<br>" + "z: %{z:.4f}"
            ),
            text=[f"<b>{ids[int(i)]}</b>" for i in range(len(ids))],
            name="Uploaded AFIDs",
        ),
        go.Scatter3d(
            x=lines_x,
            y=lines_y,
            z=lines_z,
            showlegend=False,
            mode="lines",
            hovertemplate="%{text}",
            text=[
                (
                    f"<b>{ids[int(i / 4)]}</b><br>Euclidean Distance: "
                    f"{lines_magnitudes[i]:.3f} mm"
                )
                for i in range(len(lines_x))
            ],
            line={
                "color": lines_magnitudes,
                "colorscale": "Bluered",
                "width": 8,
                "showscale": True,
                "colorbar": {"title": {"text": "Euclidean distance"}},
            },
            name="Euclidean Distance",
        ),
    ]

    bigfig = go.Figure()
    bigfig.add_trace(dset1[0])
    bigfig.add_trace(dset1[1])
    bigfig.add_trace(dset1[2])

    bigfig.update_layout(
        title_text="Euclidean distances from template",
        autosize=True,
        barmode="stack",
        coloraxis={"colorscale": "Bluered"},
        legend_orientation="h",
    )

    return bigfig.to_html(include_plotlyjs="cdn", full_html=False)


def generate_histogram(ref_afids, user_afids):
    """Generate an HTML snippet containing a histogram of distances.

    Parameters
    ----------
    ref_afids : Afids
        Reference AFIDs object.
    user_afids : Afids
        User-provided AFIDs object.

    Returns
    -------
    str
        HTML snippet containing a histogram of the Euclidean distance
        between pairs of provided AFIDs.
    """
    connecting_lines = gen_connecting_lines(ref_afids, user_afids)
    _, _, _, lines_magnitudes = calculate_magnitudes(connecting_lines)

    ids = [desc[-1] for desc in EXPECTED_DESCS]

    # next figure: histogram of distances
    lines_magnitudes_unique = [
        i for ix, i in enumerate(lines_magnitudes) if not ix % 4
    ]

    howtosort = sorted(
        range(len(lines_magnitudes_unique)),
        key=lambda k: lines_magnitudes_unique[k],
    )
    dists_sorted = [lines_magnitudes_unique[i] for i in howtosort]
    ids_sorted = [ids[i] for i in howtosort]

    fig4 = go.Figure(
        data=go.Bar(
            x=do_binning(dists_sorted),
            y=[1 for i in ids],
            text=[
                str(i) + "<br>" + str(round(dists_sorted[ix], 3)) + " mm"
                for ix, i in enumerate(ids_sorted)
            ],
            marker_color=dists_sorted,
            marker_colorscale="Bluered",
            showlegend=False,
        )
    )

    fig4.update_layout(
        title_text="Template vs. provided AFIDs",
        autosize=True,
        coloraxis={"colorscale": "Bluered"},
    )

    return fig4.to_html(include_plotlyjs="cdn", full_html=False)


def generate_radar_chart(ref_afids, user_afids):
    """Generate an HTML snippet containing a radar chart of regional errors.

    Parameters
    ----------
    ref_afids : Afids
        Reference AFIDs object.
    user_afids : Afids
        User-provided AFIDs object.

    Returns
    -------
    str
        HTML snippet containing a radar chart of mean Euclidean error
        per neuroanatomical region.
    """
    region_names = list(LANDMARK_REGIONS.keys())
    region_means = []

    for landmarks in LANDMARK_REGIONS.values():
        distances = []
        for lm in landmarks:
            ref_pos = getattr(ref_afids, lm)
            user_pos = getattr(user_afids, lm)
            dist = (
                (ref_pos.x - user_pos.x) ** 2
                + (ref_pos.y - user_pos.y) ** 2
                + (ref_pos.z - user_pos.z) ** 2
            ) ** 0.5
            distances.append(dist)
        region_means.append(sum(distances) / len(distances))

    # Close the polygon loop
    theta = region_names + [region_names[0]]
    r = region_means + [region_means[0]]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=r,
            theta=theta,
            fill="toself",
            fillcolor="rgba(0, 255, 1, 0.15)",
            line={"color": "rgba(0, 255, 1, 0.9)", "width": 2},
            hovertemplate=(
                "<b>%{theta}</b><br>Mean error: %{r:.2f} mm<extra></extra>"
            ),
            name="Mean error (mm)",
        )
    )

    fig.update_layout(
        title={
            "text": "Error Profile by Neuroanatomical Region",
            "font": {"color": "white", "size": 16},
        },
        polar={
            "bgcolor": "rgba(0,0,0,0)",
            "radialaxis": {
                "visible": True,
                "tickfont": {"color": "white", "size": 10},
                "ticksuffix": " mm",
                "gridcolor": "rgba(255,255,255,0.2)",
                "linecolor": "rgba(255,255,255,0.2)",
            },
            "angularaxis": {
                "tickfont": {"color": "white", "size": 12},
                "gridcolor": "rgba(255,255,255,0.15)",
                "linecolor": "rgba(255,255,255,0.2)",
            },
        },
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin={"t": 60, "b": 40, "l": 60, "r": 60},
    )

    return fig.to_html(include_plotlyjs="cdn", full_html=False)


def do_binning(in_data, nbins=6):
    """Manually bin a list of numbers.

    Parameters
    ----------
    in_data : list of float
        The values to bin.
    nbins : int, optional
        The number of bins to use.

    Returns
    -------
    list of string
        A list of strings describing each bin's limits, to two decimal places.
    """
    # min is always 0
    output = []

    fullrange = int(max(in_data)) + 1
    interval = fullrange / nbins
    for i in in_data:
        cpy = i
        for j in range(nbins):
            cpy -= interval
            if cpy < 0:
                out = interval * j
                break

        outformatted = str(round(out, 2)) + "-" + str(round(out + interval, 2))
        output.append(outformatted)
    return output
