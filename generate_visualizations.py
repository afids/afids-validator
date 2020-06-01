import plotly.graph_objects as go
import csv
import random # remove this once we dont need "fake" user data

# INPUT:     FCSVs corresponding to (the "true" points to compare) and (the user data)
#                                          ^ "reference"                      ^ "user"

def generate_visualizations(fname1='../afids-examples/sub-MNI2009cAsym/sub-MNI2009cAsym_afids.fcsv',
    fname2=''):
    ''' first argument: filename of fcsv containing "reference" AFIDs
        second argument: filename of fcsv containing "user" AFIDs for comparison '''

    with open(fname1) as reference, open(fname2) as user:
        ref_rdr = csv.reader(reference, delimiter=',')
        user_rdr = csv.reader(user, delimiter=',')
        ref_data = []
        user_data = []
        connecting_lines = []
        for n, row in enumerate(ref_rdr):
            if n < 3: continue; # skip first three rows
            entry = {}
            entry['x']=float(row[1])
            entry['y']=float(row[2])
            entry['z']=float(row[3])
            entry['id']=row[12]
            ref_data.append(entry)
            #e2 = dict(entry)
            #e2['x'] += random.gauss(0,2)
            #e2['y'] += random.gauss(0,2)
            #e2['z'] += random.gauss(0,1)
            #user_data.append(e2)
        for n, row in enumerate(user_rdr):
            if n < 3: continue; # skip first three rows
            entry = {}
            entry['x']=float(row[1])
            entry['y']=float(row[2])
            entry['z']=float(row[3])
            entry['id']=row[12]
            user_data.append(entry)
        for i in range(len(user_data)):
            connecting_lines.append([{'x':ref_data[i]['x'],'y':ref_data[i]['y'],'z':ref_data[i]['z']},
                {'x':user_data[i]['x'],'y':user_data[i]['y'],'z':user_data[i]['z']}])

    lines_x = []
    lines_y = []
    lines_z = []
    lines_magnitudes = []
    ids = [i['id'] for i in ref_data]
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
        d = ((line[0]['x']-line[1]['x'])**2
        + (line[0]['y']-line[1]['y'])**2
        + (line[0]['z']-line[1]['z'])**2)**0.5
        lines_magnitudes.append(d)
        lines_magnitudes.append(d)
        lines_magnitudes.append(d)
        lines_magnitudes.append(0)

    fig = go.Figure(data=[
        go.Scatter3d(
            x=[i['x'] for i in ref_data],
            y=[i['y'] for i in ref_data],
            z=[i['z'] for i in ref_data],
            mode = "markers",
            marker = dict(size=4, color='rgba(102,102,153,0.9)', line=dict(width=1.5, color='rgba(50,50,50,1.0)')),
            hovertemplate = '%{text}<br>x: %{x:.4f}<br>y: %{y:.4f}<br>z: %{z:.4f}',
            text = ['<b>{0}</b>'.format( ids[int(i)] ) for i in range(len(ids))],
            name = "Reference AFIDs (__ Template)"
            ),
        go.Scatter3d(
            x=[i['x'] for i in user_data],
            y=[i['y'] for i in user_data],
            z=[i['z'] for i in user_data],
            mode = "markers",
            marker = dict(size=4, color='rgba(102,0,51,0.9)', line=dict(width=1.5, color='rgba(50,50,50,1.0)')),
            hovertemplate = '%{text}<br>x: %{x:.4f}<br>y: %{y:.4f}<br>z: %{z:.4f}',
            text = ['<b>{0}</b>'.format( ids[int(i)] ) for i in range(len(ids))],
            name = "User AFIDs"
            ),
        go.Scatter3d(
            x=lines_x,
            y=lines_y,
            z=lines_z,

            showlegend = False,
            mode = "lines",
            hovertemplate = '%{text}',
            text=['<b>{0}</b><br>Euclidean Distance: {1:.3f} mm'.format( ids[int(i/4)] ,
                lines_magnitudes[i]) for i in range(len(lines_x))],
            line=dict(color=lines_magnitudes, colorscale="Bluered", width = 8)
            ),
        ]
        )

    #
    fig.update_layout(autosize = False, height = 650, width = 1250)
    # currently the renderer simply embeds the figure in an html document and puts
    # it in /iframe_figures/
    # This can be changed to make it output directly into another webpage, for example.
    # (I think.)
    fig.show(renderer = 'iframe')
