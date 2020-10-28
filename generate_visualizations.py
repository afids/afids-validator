"""Utilities for generating AFIDs-related graphics"""

import json

from plotly.subplots import make_subplots
import plotly.graph_objects as go

from model_auto import csv_to_json

def generate_visualizations(ref_fname, user_fname):
    """first argument: filename of fcsv containing "reference" AFIDs
    second argument: filename of fcsv containing "user" AFIDs for
    comparison
    """

    with open(ref_fname, "r") as ref_file, open(user_fname, "r") as user_file:
        ref_json = json.loads(csv_to_json(ref_file))
        user_json = json.loads(csv_to_json(user_file))

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
                    ids[int(i/4)],
                    lines_magnitudes[i])
                for i in range(len(lines_x))],
            line=dict(
                color=lines_magnitudes,
                colorscale="Bluered",
                width=8)),
        ]
    fig1 = go.Figure(data=dset1)
    fig1.update_layout(autosize=False, height=650, width=1250)

    # currently the renderer simply embeds the figure in an html document
    # and puts it in /iframe_figures/
    # This can be changed to make it output directly into another webpage,
    # for example. (I think.)
    # fig1.show(renderer = 'iframe')
    # fig1.write_html('fig1.html')

    ## next figure: histogram of distances
    lines_magnitudes_unique = [
        i for ix, i in enumerate(lines_magnitudes) if not ix % 4]

    howtosort = sorted(range(len(lines_magnitudes_unique)),
                       key=lambda k: lines_magnitudes_unique[k])
    dists_sorted = [lines_magnitudes_unique[i] for i in howtosort]
    ids_sorted = [ids[i] for i in howtosort]

    bigfig = make_subplots(
        rows=2,
        cols=1,
        specs=[[{"type": "scene"}], [{"type": "xy"}]],
        subplot_titles=(
            "3D Map of Placed AFIDs",
            "Histogram of Placement Error"))

    bigfig.add_trace(dset1[0], row=1, col=1)
    bigfig.add_trace(dset1[1], row=1, col=1)
    bigfig.add_trace(dset1[2], row=1, col=1)

    fig4 = go.Bar(
        x=do_binning(dists_sorted),
        y=[1 for i in ids],
        text=[str(i) + '<br>' + str(round(dists_sorted[ix], 3)) + ' mm'
              for ix, i in enumerate(ids_sorted)],
        textposition='inside',
        marker_color=dists_sorted,
        marker_colorscale="Bluered",
        showlegend=False)

    bigfig.add_trace(fig4, row=2, col=1)

    bigfig.update_layout(
        autosize=False,
        height=1600,
        width=1350,
        barmode="stack",
        coloraxis=dict(colorscale='Bluered'))

    return bigfig.to_html(include_plotlyjs="cdn")

def do_binning(in_data, nbins=6):
    # min is always 0
    output = []

    fullrange = int(max(in_data)) + 1
    interval = fullrange/nbins
    for i in in_data:
        cpy = i
        for j in range(nbins):
            cpy -= interval
            if cpy < 0:
                out = interval * j
                break
        #
        outformatted = str(round(out, 2)) + "-" + str(round(out + interval, 2))
        output.append(outformatted)
    #
    return output

if __name__ == "__main__":
    print(generate_visualizations(
        "./afids-templates/human/sub-MNI2009cAsym_afids.fcsv",
        "./afids-templates/human/sub-PD25_afids.fcsv"))
