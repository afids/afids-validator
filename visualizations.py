"""Utilities for generating AFIDs-related graphics"""

import plotly.graph_objects as go


def gen_connecting_lines(ref_json, user_json):
    """Assemble points from each fcsv into pairs.

    Parameters
    ----------
    ref_json : dict
        Dictionary of reference AFIDs
    user_json : dict
        Dictionary of user-provided AFIDs

    Returns
    -------
    list of list of dict
        A list, where each element is a pair of x,y,z dicts to respective
        AFIDs coordinates.
    """
    connecting_lines = []
    for ref_entry, user_entry in zip(ref_json.values(), user_json.values()):
        connecting_lines.append(
            [
                {
                    "x": float(ref_entry["x"]),
                    "y": float(ref_entry["y"]),
                    "z": float(ref_entry["z"]),
                },
                {
                    "x": float(user_entry["x"]),
                    "y": float(user_entry["y"]),
                    "z": float(user_entry["z"]),
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


def generate_3d_scatter(ref_json, user_json):
    """Generate an HTML snippet containing a 3D scatter plot.

    Parameters
    ----------
    ref_json : dict
        Dictionary of reference AFIDs.
    user_json : dict
        Dictionary of user-provided AFIDs.

    Returns
    -------
    str
        HTML snippet containing a 3D scatter plot illustrating the distance
        between pairs of provided AFIDs.
    """

    connecting_lines = gen_connecting_lines(ref_json, user_json)

    lines_x, lines_y, lines_z, lines_magnitudes = calculate_magnitudes(
        connecting_lines
    )

    ids = [entry["desc"] for entry in ref_json.values()]

    dset1 = [
        go.Scatter3d(
            x=[float(i["x"]) for i in ref_json.values()],
            y=[float(i["y"]) for i in ref_json.values()],
            z=[float(i["z"]) for i in ref_json.values()],
            showlegend=True,
            mode="markers",
            marker=dict(
                size=4,
                color="rgba(255,191,31,0.9)",
                line=dict(width=1.5, color="rgba(50,50,50,1.0)"),
            ),
            hovertemplate=(
                "%{text}<br>x: %{x:.4f}<br>y: %{y:.4f}<br>" + "z: %{z:.4f}"
            ),
            text=["<b>{0}</b>".format(ids[int(i)]) for i in range(len(ids))],
            name="Template AFIDs",
        ),
        go.Scatter3d(
            x=[float(i["x"]) for i in user_json.values()],
            y=[float(i["y"]) for i in user_json.values()],
            z=[float(i["z"]) for i in user_json.values()],
            showlegend=True,
            mode="markers",
            marker=dict(
                size=4,
                color="rgba(0,0,0,0.9)",
                line=dict(width=1.5, color="rgba(50,50,50,1.0)"),
            ),
            hovertemplate=(
                "%{text}<br>x: %{x:.4f}<br>y: %{y:.4f}<br>" + "z: %{z:.4f}"
            ),
            text=["<b>{0}</b>".format(ids[int(i)]) for i in range(len(ids))],
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
                "<b>{0}</b><br>Euclidean Distance: {1:.3f} mm".format(
                    ids[int(i / 4)], lines_magnitudes[i]
                )
                for i in range(len(lines_x))
            ],
            line=dict(
                color=lines_magnitudes,
                colorscale="Bluered",
                width=8,
                showscale=True,
                colorbar=dict(title=dict(text="Euclidean distance")),
            ),
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
        coloraxis=dict(colorscale="Bluered"),
        legend_orientation="h",
    )

    return bigfig.to_html(include_plotlyjs="cdn", full_html=False)


def generate_histogram(ref_json, user_json):
    """Generate an HTML snippet containing a histogram of distances.

    Parameters
    ----------
    ref_json : dict
        Dictionary of reference AFIDs.
    user_json : dict
        Dictionary of user-provided AFIDs.

    Returns
    -------
    str
        HTML snippet containing a histogram of the Euclidean distance
        between pairs of provided AFIDs.
    """
    connecting_lines = gen_connecting_lines(ref_json, user_json)
    _, _, _, lines_magnitudes = calculate_magnitudes(connecting_lines)

    ids = [entry["desc"] for entry in ref_json.values()]

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
        coloraxis=dict(colorscale="Bluered"),
    )

    return fig4.to_html(include_plotlyjs="cdn", full_html=False)


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
