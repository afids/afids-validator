from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import csv

# INPUT:     FCSVs corresponding to (the "true" points to compare) and (the user data)
#                                          ^ "reference"                      ^ "user"

def generate_visualizations(fname1='.\\afids-templates\\human\\sub-MNI2009cAsym_afids.fcsv',
    fname2='.\\afids-sampledata\\MNI2009b_T1_JKai_1_20170530.fcsv'):
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

    dset1 = [
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
    fig1 = go.Figure(data=dset1)

    #
    fig1.update_layout(autosize = False, height = 650, width = 1250)
    # currently the renderer simply embeds the figure in an html document and puts
    # it in /iframe_figures/
    # This can be changed to make it output directly into another webpage, for example.
    # (I think.)
    #fig1.show(renderer = 'iframe')
    #fig1.write_html('fig1.html')

    ## next figure: histogram of distances
    lines_magnitudes_unique = [i for ix, i in enumerate(lines_magnitudes) if not ix%4]
    #dset2 = go.Histogram(x=lines_magnitudes_unique, showlegend=False,
    #nbinsx = 10)

    xvals = ['a','b']
    dset2 = [go.Bar(x=xvals,y=[12,45]),
    go.Bar(x=xvals, y=[22, 33])
    ]

    #fig2 = go.Figure(data = [dset2])
    #fig2.update_layout(autosize = False, height = 650, width = 1250)
    #fig2.write_html('fig2.html')
    howtosort = sorted(range(len(lines_magnitudes_unique)), key = lambda k:lines_magnitudes_unique[k])
    dists_sorted = [lines_magnitudes_unique[i] for i in howtosort]
    ids_sorted = [ids[i] for i in howtosort]

    '''
    ourdf = pd.DataFrame(data={'ids':ids,'Distance':lines_magnitudes_unique,
        'Distance (Binned)':do_binning(lines_magnitudes_unique), 'Height':[1 for i in ids]})
    fig3 = px.bar( ourdf , x='Distance (Binned)', y='Height', color = 'Distance',
        text = "ids", hover_data = ['ids', 'Distance'],
        color_continuous_scale=px.colors.sequential.Bluered,
        labels={"Distance":"Euclidean Distance", "ids":"ID"})
    '''

    bigfig = make_subplots(rows=2, cols=1, specs=[[{"type": "scene"}], [{"type": "xy"}]],
        subplot_titles=("3D Map of Placed AFIDs", "Histogram of Placement Error") )

    bigfig.add_trace(dset1[0], row=1,col=1)
    bigfig.add_trace(dset1[1], row=1,col=1)
    bigfig.add_trace(dset1[2], row=1,col=1)

    #bigfig.add_trace(dset2[0], row=2,col=1)
    #bigfig.add_trace(dset2[1], row=2,col=1)

    fig4 = go.Bar(x=do_binning(dists_sorted), y=[1 for i in ids],
        text = [str(i)+'<br>'+str(round(dists_sorted[ix],3))+' mm' for ix, i in enumerate(ids_sorted)],
        textposition='inside',
        #hovertemplate = '%{text}<br>x: %{x:.4f}<br>y: %{y:.4f}<br>z: %{z:.4f}',
        marker_color = dists_sorted, marker_colorscale="Bluered", showlegend=False)

    #bigfig.add_trace(fig3['data'][0], row=2,col=1)
    bigfig.add_trace(fig4, row=2,col=1)

    bigfig.update_layout(autosize = False, height=1600, width=1350, barmode = "stack",
        coloraxis = dict(colorscale='Bluered'))

    #pdb.set_trace()

    bigfig.write_html('twofigs.html')

def do_binning(input, nbins=6):
    # min is always 0
    output = []

    fullrange = int(max(input)) + 1
    interval = fullrange/nbins
    for i in input:
        cpy = i
        for j in range(nbins):
            cpy -= interval
            if cpy < 0:
                out = interval * j
                break
        #
        outformatted = str(round(out,2)) + "-" + str(round(out + interval,2))
        output.append(outformatted)
    #
    return output

generate_visualizations()
