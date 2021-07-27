import os

from pandas.core.indexes import multi
from studio2021.datastructures import Building
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px


def load_jsons(folderpath):
    cdict = {'Seattle': 'seattle', 'San Antonio': 'san_antonio',
             'Milwaukee': 'milwaukee', 'Los Angeles': 'los_angeles'}
    pdict = {'2013::MidriseApartment::Apartment': 'residential',
             '2013::MediumOffice::OpenOffice': 'office'}

    data = {'seattle':{'residential':{}, 'office':{}},
            'san_antonio':{'residential':{}, 'office':{}},
            'milwaukee':{'residential':{}, 'office':{}},
            # 'los_angeles':{'residential':{}, 'office':{}}
            }

    files = os.listdir(folderpath)
    for f in files:
        if f.endswith('json'):
            b = Building.from_json(os.path.join(folderpath, f))
            key = os.path.splitext(f)[0]
            program = pdict[b.zone_program]
            city = cdict[b.city]
            data[city][program][key] = parse_building(b, f)
    return data


def load_jsons_pandas(folderpath):
    data = {}
    files = os.listdir(folderpath)
    for f in files[:1000]:
        if f.endswith('json'):
            b = Building.from_json(os.path.join(folderpath, f))
            key = os.path.splitext(f)[0]
            data[key] = parse_building(b, f)
    data = pd.DataFrame.from_dict(data, orient='index')
    return data


def parse_building(bldg, filename):

    gl_dict = {'Aluminum Double': 2, 'Aluminum Triple': 3}
    int_dict = {'2x6 Wood Studs':6, '2x8 Wood Studs':8, '2x10 Wood Studs':10, 0:0}
    pdict = {'2013::MidriseApartment::Apartment': 'residential',
             '2013::MediumOffice::OpenOffice': 'office'}
    data = {}
    area = bldg.floor_area
    win  = bldg.envelope.window_embodied or 0.
    wall = bldg.envelope.wall_embodied or 0.
    win /= area
    wall/= area

    zonek = list(bldg.eui_kgco2e.keys())[0]
    cool = bldg.eui_kgco2e[zonek]['cooling'] / area
    heat = bldg.eui_kgco2e[zonek]['heating'] / area
    light = bldg.eui_kgco2e[zonek]['lighting'] / area
    hot = bldg.eui_kgco2e[zonek]['hot_water'] / area
    eq = bldg.eui_kgco2e[zonek]['equipment'] / area

    data['max_cooling'] = bldg.max_cooling[zonek]['max']
    data['max_heating'] = bldg.max_heating[zonek]['max']
    data['max_lighting'] = bldg.max_lighting[zonek]['max']
    data['max_solar'] = bldg.max_solar[zonek]['max']

    filename = filename.split('_')
    data['orient'] = filename[1]
    data['wwr'] = bldg.wwr['n']
    data['glazing'] = gl_dict[bldg.glazing_system]
    data['shading'] = bldg.shade_depth_h['n']
    data['shgc'] = bldg.shade_gc['n']
    data['exterior_mat'] = bldg.external_insulation
    data['exterior_t'] = bldg.insulation_thickness or 0.
    data['interior_mat'] = bldg.interior_insul_mat
    interior_thick = bldg.ewall_framing or 0.
    data['interior_t'] = int_dict[interior_thick]

    data['total_embodied'] = win + wall
    data['window_embodied'] = win
    data['wall_embodied'] = wall
    data['total_cooling'] = cool
    data['total_heating'] = heat
    data['total_lighting'] = light
    data['hot_water_operational'] = hot
    data['equipment_operational'] = eq
    data['total_operational'] = cool + heat + light + hot + eq

    data['city'] = bldg.city
    data['program'] = pdict[bldg.zone_program]

    return data


def plot_pareto(data):
    city = 'seattle'
    program = 'office'
    xk = 'total_embodied'
    yk = 'total_operational'

    x = []
    y = []
    text = []
    for k in data[city][program]:
        x.append(data[city][program][k][xk])
        y.append(data[city][program][k][yk])
        text.append(k)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(name=city,
                            x=x,
                            y=y,
                            mode='markers',
                            hovertext=text,
                            marker=dict(color=[],
                                        size=12,
                                        line=dict(color='black',
                                                width=1))))

    xaxis = go.layout.XAxis(title='{}'.format(xk))
    yaxis = go.layout.YAxis(title='{}'.format(yk))
    fig.update_layout(title={'text': 'Pareto Front'},
                      xaxis=xaxis,
                      yaxis=yaxis,
                      hovermode='closest')

    # Add dropdowns
    button_layer_1_height = 1.08
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=list([
                    dict(
                        args=["city", "seattle"],
                        label="Seattle",
                        method="update"),
                    dict(
                        args=["city", "milwaukee"],
                        label="Milwaukee",
                        method="update"),

                ]),
                direction="left",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.1,
                xanchor="left",
                y=button_layer_1_height,
                yanchor="top"
            ),

        ]
    )

    fig.show()


def dash_pareto(data):
    app = dash.Dash(__name__)
    cities = list(data.keys())
    cities.append('all')
    programs = list(data['seattle'].keys())
    programs.append('all')
    
    data_types = ['total_embodied', 'window_embodied', 'wall_embodied',
                  'total_operational', 'total_cooling', 'total_heating','total_lighting',
                  'max_cooling', 'max_heating', 'max_lighting', 'max_solar']
    
    orientations = ['n', 'w', 's', 'e', 'all']
    
    wwrs = ['0', '20', '40', '60', '80', 'all']
    
    labels = ['wwr', 'shading', 'glazing', 'shgc', 'exterior_mat', 'exterior_t',
               'interior_mat', 'interior_t', 'None']

    app.layout = html.Div([
        html.Div([

            html.Div([
                dcc.Dropdown(
                    id='cities',
                    options=[{'label': i, 'value': i} for i in cities],
                    value='all'),],
                    style={'width': '14%', 'display': 'inline-block', 'font-family':'open sans', 'font-size':'12px'}),

            html.Div([
                dcc.Dropdown(
                    id='programs',
                    options=[{'label': i, 'value': i} for i in programs],
                    value='all'),],
                    style={'width': '14%', 'display': 'inline-block', 'font-family':'open sans', 'font-size':'12px'}),


            html.Div([
                dcc.Dropdown(
                    id='orientations',
                    options=[{'label': i, 'value': i} for i in orientations],
                    value='all'),],
                    style={'width': '14%', 'display': 'inline-block', 'font-family':'open sans', 'font-size':'12px'}),

            html.Div([
                dcc.Dropdown(
                    id='wwr',
                    options=[{'label': i, 'value': i} for i in wwrs],
                    value='all'),],
                    style={'width': '14%', 'display': 'inline-block', 'font-family':'open sans', 'font-size':'12px'}),

            html.Div([
                dcc.Dropdown(
                    id='labels',
                    options=[{'label': i, 'value': i} for i in labels],
                    value='None'),],
                    style={'width': '14%', 'display': 'inline-block', 'font-family':'open sans', 'font-size':'12px'}),


            html.Div([
                dcc.Dropdown(
                    id='xaxis',
                    options=[{'label': i, 'value': i} for i in data_types],
                    value='total_embodied'),],
                    style={'width': '14%', 'display': 'inline-block', 'font-family':'open sans', 'font-size':'12px'}),


            html.Div([
                dcc.Dropdown(
                    id='yaxis',
                    options=[{'label': i, 'value': i} for i in data_types],
                    value='total_operational'),],
                    style={'width': '12%', 'display': 'inline-block', 'font-family':'open sans', 'font-size':'12px'}),
                    ]),

        dcc.Graph(id='indicator-graphic'),
    ])

    @app.callback(
        Output('indicator-graphic', 'figure'),
        Input('cities', 'value'),
        Input('programs', 'value'),
        Input('orientations', 'value'),
        Input('wwr', 'value'),
        Input('labels', 'value'),
        Input('xaxis', 'value'),
        Input('yaxis', 'value'))
    def update_graph(city, program, orientation, wwr, label, kx, ky):

        if city == 'all':
            cities = ['seattle', 'san_antonio', 'milwaukee']
        else:
            cities = [city]

        if program == 'all':
            programs = ['residential', 'office']
        else:
            programs = [program]

        if orientation == 'all':
            orientation = ['n', 'w', 's', 'e']
        else:
            orientation = [orientation]

        if wwr == 'all':
            wwr = [0., 0.2, 0.4, 0.6, 0.8]
        else:
            wwr = [float(wwr) / 100.]

        fig = go.Figure()
        # fig.update_layout(height = '1000px')
        string = 'wwr = {}<br>orientation = {}<br>glazing = {}<br>shading = {}<br>'
        string += 'shgc = {}<br>exterior mat = {}<br>exterior thick = {}<br>'
        string += 'interior mat = {}<br>interior_ thick = {}'

        for city in cities:
            for program in programs:
                x = []
                y = []
                text = []
                hover = []
                for k in data[city][program]:
                    o = data[city][program][k]['orient']
                    wwr_ = data[city][program][k]['wwr']
                    gl = data[city][program][k]['glazing']
                    sh = data[city][program][k]['shading']
                    shg = data[city][program][k]['shgc']
                    em = data[city][program][k]['exterior_mat']
                    et = data[city][program][k]['exterior_t']
                    im = data[city][program][k]['interior_mat']
                    it = data[city][program][k]['interior_t']

                    if o not in orientation:
                        continue
                    if wwr_ not in wwr:
                        continue
                    x.append(data[city][program][k][kx])
                    y.append(data[city][program][k][ky])
                    hover.append(string.format(wwr_, o, gl, sh, shg, em, et, im, it))
                    if label != 'None':
                        text.append(data[city][program][k][label])

                fig.add_trace(go.Scatter(name='{}_{}'.format(city, program),
                                        x=x,
                                        y=y,
                                        mode='markers+text',
                                        text=text,
                                        textposition="bottom center",
                                        hovertext=hover),)

                xaxis = go.layout.XAxis(title='{}'.format(kx))
                yaxis = go.layout.YAxis(title='{}'.format(ky))

                fig.update_layout(title={'text': 'Pareto Front'},
                                  xaxis=xaxis,
                                  yaxis=yaxis,
                                  hovermode='closest',
                                  autosize=False,
                                  height=600,
                                  width=1300,
                                  )
        # Add annotation
        # fig.update_layout(annotations=[
        # dict(text="City", yref="paper", xref='paper',        x=-.04, y=1.14, showarrow=False),
        # dict(text="Program", yref="paper", xref='paper',     x=.07,  y=1.14, showarrow=False),
        # dict(text="Orientation", yref="paper", xref='paper', x=.19,  y=1.14, showarrow=False),
        # dict(text="WWR", yref="paper", xref='paper',         x=.31,  y=1.14, showarrow=False),
        # dict(text="Label", yref="paper", xref='paper',       x=.44,  y=1.14, showarrow=False),
        # dict(text="X axix", yref="paper", xref='paper',      x=.56,  y=1.14, showarrow=False),
        # dict(text="Y Axis", yref="paper", xref='paper',      x=.69,  y=1.14, showarrow=False),])
        return fig
    app.run_server(debug=True)


def dash_pareto_pandas(frame):
    app = dash.Dash(__name__)
    cities = ['Seattle', 'San Antonio', 'Milwaukee', 'all']
    programs = ['office', 'residential', 'all']
    orientations = ['n', 'w', 's', 'e', 'all']
    wwrs = ['0', '20', '40', '60', '80', 'all']
    colors = ['None', 'city', 'orient', 'wwr', 'glazing', 'program']
    sizes = ['wwr', 'glazing']
    labels = ['wwr', 'shading', 'glazing', 'shgc', 'exterior_mat', 'exterior_t',
               'interior_mat', 'interior_t', 'None']

    app.layout = html.Div([
        html.Div([

            html.Div([
                html.Label('City'),
                dcc.Dropdown(
                    id='cities',
                    options=[{'label': i, 'value': i} for i in cities],
                    clearable=False,
                    value='all', ),],
                    style={'width': '14%', 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'12px'}),

            html.Div([
                html.Label('Program'),
                dcc.Dropdown(
                    id='programs',
                    options=[{'label': i, 'value': i} for i in programs],
                    clearable=False,
                    value='all'),],
                    style={'width': '14%', 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'12px'}),                    

            html.Div([
                html.Label('Orientation'),
                dcc.Dropdown(
                    id='orientations',
                    options=[{'label': i, 'value': i} for i in orientations],
                    clearable=False,
                    value='all'),],
                    style={'width': '14%', 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'12px'}),    

            html.Div([
                html.Label('WWR'),
                dcc.Dropdown(
                    id='wwrs',
                    options=[{'label': i, 'value': i} for i in wwrs],
                    clearable=False,
                    value='all'),],
                    style={'width': '14%', 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'12px'}),    

            html.Div([
                html.Label('Color by'),
                dcc.Dropdown(
                    id='colors',
                    options=[{'label': i, 'value': i} for i in colors],
                    clearable=False,
                    value='city'),],
                    style={'width': '14%', 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'12px'}),    

            html.Div([
                html.Label('Size by'),
                dcc.Dropdown(
                    id='sizes',
                    options=[{'label': i, 'value': i} for i in sizes],
                    clearable=False,
                    value='wwr'),],
                    style={'width': '14%', 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'12px'}),  

            html.Div([
                html.Label('Label by'),
                dcc.Dropdown(
                    id='labels',
                    options=[{'label': i, 'value': i} for i in labels],
                    clearable=False,
                    value='None'),],
                    style={'width': '14%', 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'12px'}), 



                    ]),

        dcc.Graph(id='indicator-graphic'),
    ])



    @app.callback(
        Output('indicator-graphic', 'figure'),
        Input('cities', 'value'),
        Input('programs', 'value'),
        Input('orientations', 'value'),
        Input('wwrs', 'value'),
        Input('colors', 'value'),
        Input('sizes', 'value'),
        Input('labels', 'value'),
        )
    def update_graph(city, program, orient, wwr, color, size, lable):
        hd = ['total_embodied','total_operational','wwr','glazing','orient']

        if city != 'all':
            mask = (frame['city'] == city)
            df = frame[mask]
        else:
            df = frame

        if program != 'all':
            mask = (df['program'] == program)
            df = df[mask]
        else:
            df = df

        if orient != 'all':
            mask = (df['orient'] == orient)
            df = df[mask]
        else:
            df = df

        if wwr != 'all':
            mask = (df['wwr'] == float(wwr) / 100.)
            df = df[mask]
        else:
            df = df

        if color == 'None':
            color = None

        if lable == 'None':
            lable = None

        fig = px.scatter(df,
                         x='total_embodied',
                         y='total_operational',
                         color=color,
                         size=size,
                         text=lable,
                         hover_data=hd,
                        )

        fig.update_layout(title={'text': 'Pareto Front'},
                        #   xaxis=xaxis,
                        #   yaxis=yaxis,
                          hovermode='closest',
                          autosize=False,
                          height=900,
                          width=1200,
                        )
        return fig

    app.run_server(debug=True)


if __name__ == '__main__':
    #TODO: When sizing by WWR, size can go to zero, hiding data. FIX!
    for i in range(50): print('')
    folderpath = '/Users/tmendeze/Documents/UW/03_publications/studio2021/envelope_paper/all_data'
    # folderpath = '/Users/time/Documents/UW/03_publications/studio2021/envelope_paper/data_072021'
    frame = load_jsons_pandas(folderpath)
    dash_pareto_pandas(frame)

