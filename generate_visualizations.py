"""Utilities for generating AFIDs-related graphics"""

import plotly.graph_objects as go

def generate_visualizations(ref_json, user_json):
    """first argument: filename of fcsv containing "reference" AFIDs
    second argument: filename of fcsv containing "user" AFIDs for
    comparison
    """

    connecting_lines = []
    for _, entry_pair in enumerate(
            zip(ref_json.values(), user_json.values())):
        ref_entry = entry_pair[0]
        user_entry = entry_pair[1]
        connecting_lines.append(
            [{'x': float(ref_entry['x']),
              'y': float(ref_entry['y']),
              'z': float(ref_entry['z'])},
             {'x': float(user_entry['x']),
              'y': float(user_entry['y']),
              'z': float(user_entry['z'])}])

    lines_x = []
    lines_y = []
    lines_z = []
    lines_magnitudes = []
    ids = [entry['desc'] for entry in ref_json.values()]
    for line in connecting_lines:
        lines_x.append(line[0]['x'])
        lines_x.append((line[0]['x'] + line[1]['x'])/2)
        lines_x.append(line[1]['x'])
        lines_x.append(None)

        lines_y.append(line[0]['y'])
        lines_y.append((line[0]['y'] + line[1]['y'])/2)
        lines_y.append(line[1]['y'])
        lines_y.append(None)

        lines_z.append(line[0]['z'])
        lines_z.append((line[0]['z'] + line[1]['z'])/2)
        lines_z.append(line[1]['z'])
        lines_z.append(None)

        distance = ((line[0]['x']-line[1]['x'])**2
                    + (line[0]['y']-line[1]['y'])**2
                    + (line[0]['z']-line[1]['z'])**2)**0.5
        lines_magnitudes.append(distance)
        lines_magnitudes.append(distance)
        lines_magnitudes.append(distance)
        lines_magnitudes.append(0)

    dset1 = [
        go.Scatter3d(
            x=[float(i['x']) for i in ref_json.values()],
            y=[float(i['y']) for i in ref_json.values()],
            z=[float(i['z']) for i in ref_json.values()],
            showlegend=False,
            mode="markers",
            marker=dict(
                size=4,
                color='rgba(102,102,153,0.9)',
                line=dict(width=1.5, color='rgba(50,50,50,1.0)')),
            hovertemplate=("%{text}<br>x: %{x:.4f}<br>y: %{y:.4f}<br>"
                           + "z: %{z:.4f}"),
            text=['<b>{0}</b>'.format(ids[int(i)]) for i in range(len(ids))],
            name="Reference AFIDs"),
        go.Scatter3d(
            x=[float(i['x']) for i in user_json.values()],
            y=[float(i['y']) for i in user_json.values()],
            z=[float(i['z']) for i in user_json.values()],
            showlegend=False,
            mode="markers",
            marker=dict(
                size=4,
                color='rgba(102,0,51,0.9)',
                line=dict(width=1.5, color='rgba(50,50,50,1.0)')),
            hovertemplate=("%{text}<br>x: %{x:.4f}<br>y: %{y:.4f}<br>"
                           + "z: %{z:.4f}"),
            text=['<b>{0}</b>'.format(ids[int(i)]) for i in range(len(ids))],
            name="User AFIDs"),
        go.Scatter3d(
            x=lines_x,
            y=lines_y,
            z=lines_z,
            showlegend=False,
            mode="lines",
            hovertemplate='%{text}',
            text=[
                '<b>{0}</b><br>Euclidean Distance: {1:.3f} mm'.format(
                    ids[int(i/4)], lines_magnitudes[i])
                for i in range(len(lines_x))],
            line=dict(
                color=lines_magnitudes,
                colorscale="Bluered",
                width=8)),
        ]

    # next figure: histogram of distances
    lines_magnitudes_unique = [
        i for ix, i in enumerate(lines_magnitudes) if not ix % 4]

    howtosort = sorted(range(len(lines_magnitudes_unique)),
                       key=lambda k: lines_magnitudes_unique[k])
    dists_sorted = [lines_magnitudes_unique[i] for i in howtosort]
    ids_sorted = [ids[i] for i in howtosort]

    bigfig = go.Figure()
    bigfig.add_trace(dset1[0])
    bigfig.add_trace(dset1[1])
    bigfig.add_trace(dset1[2])

    fig4 = go.Figure(data=go.Bar(
        x=do_binning(dists_sorted),
        y=[1 for i in ids],
        text=[str(i) + '<br>' + str(round(dists_sorted[ix], 3)) + ' mm'
              for ix, i in enumerate(ids_sorted)],
        textposition='inside',
        marker_color=dists_sorted,
        marker_colorscale="Bluered",
        showlegend=False))

    fig4.update_layout(
        title_text="Template vs. provided AFIDs",
        autosize=True,
        barmode="stack",
        coloraxis=dict(colorscale='Bluered'))
    bigfig.update_layout(
        title_text="Euclidean distances from template",
        autosize=True,
        barmode="stack",
        coloraxis=dict(colorscale='Bluered'))

    return {
        "scatter":
            bigfig.to_html(
                include_plotlyjs="cdn",
                full_html=False),
        "histogram":
            fig4.to_html(
                include_plotlyjs="cdn",
                full_html=False)}

def do_binning(in_data, nbins=6):
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

if __name__ == "__main__":
    print(generate_visualizations(
        "./afids-templates/human/sub-MNI2009cAsym_afids.fcsv",
        "./afids-templates/human/sub-PD25_afids.fcsv"))
