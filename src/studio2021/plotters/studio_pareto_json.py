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


def load_jsons_pandas(folderpath):
    data = {}
    files = os.listdir(folderpath)
    for f in files:
        if f.endswith('json'):
            b = Building.from_json(os.path.join(folderpath, f))
            key = os.path.splitext(f)[0]
            data[key] = parse_building(b, f)
    frame = pd.DataFrame.from_dict(data, orient='index')
    return data, frame


def parse_building(bldg, filename):

    gl_dict = {'Aluminum Double': 'Double', 'Aluminum Triple': 'Triple'}
    int_dict = {'2x6 Wood Studs':6, '2x8 Wood Studs':8, '2x10 Wood Studs':10, 0:0}
    pdict = {'2013::MidriseApartment::Apartment': 'residential',
             '2013::MediumOffice::OpenOffice': 'office'}


    city_gwp = {'San Antonio': 0.414311, 'Seattle': 0.135669, 'Milwaukee': 0.559278936}

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
    data['wall_r'] = bldg.wall_r

    data['city'] = bldg.city
    data['program'] = pdict[bldg.zone_program]

    data['eui_kwh'] = bldg.eui_kwh[zonek]['total']
    data['kgCo2e_kwh'] = city_gwp[bldg.city]
    data['area'] = bldg.floor_area

    ny = 30
    years = list(range(1, ny))
    imp = .05
    city_gwp = data['kgCo2e_kwh']
    op = data['total_operational']
    eui = data['eui_kwh'] / data['area']
    emb = data['total_embodied']
    temp = 0
    for y in years:
        n = eui * city_gwp   
        data['total_nonlinear{}'.format(y)] = n + temp + emb
        data['total_bau{}'.format(y)] = op * y
        data['op_nonlinear{}'.format(y)] = n + temp
        city_gwp *= (1 - imp)
        temp += n

    return data


def plot_lifecycle(data, keys=None):

    ny = 30
    years = list(range(1, ny))
    fig = go.Figure()
    imp = .05
    if not keys:
        keys = data.keys()
    for k in keys:
        city_gwp = data[k]['kgCo2e_kwh']
        op = data[k]['total_operational']
        bau = [op * i for i in years]
        eui = data[k]['eui_kwh'] / data[k]['area']
        emb = []
        non = []
        temp = 0
        tot = []
        for _ in years:
            n = eui * city_gwp
            non.append(n + temp)
            emb.append(data[k]['total_embodied'])
            tot.append(n + temp + data[k]['total_embodied'])
            city_gwp *= (1 - imp)
            temp += n

        fig.add_trace(go.Scatter(x=years, y=bau, name= 'BAU - {}'.format(k)))
        fig.add_trace(go.Scatter(x=years, y=non, name= 'Non linear - {}'.format(k)))
        fig.add_trace(go.Scatter(x=years, y=emb, name= 'Embodied - {}'.format(k)))
        fig.add_trace(go.Scatter(x=years, y=tot, name= 'Total - {}'.format(k)))
    
    fig.show()


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


def dash_pareto_pandas(frame, gheight=800, gwidth=1200):
    app = dash.Dash(__name__)
    data_types = ['total_embodied', 'total_operational', 'total_nonlinear', 'op_nonlinear',
                  'wall_embodied', 'window_embodied', 'total_cooling', 'total_heating',
                  'total_lighting','max_cooling', 'max_heating', 'max_lighting',
                  'max_solar']
    colors = ['None', 'city', 'orient', 'wwr', 'glazing', 'program', 'wall_r',
              'shgc', 'exterior_mat', 'exterior_t', 'interior_mat', 'interior_t']
    sizes = ['None', 'wwr', 'exterior_t', 'interior_t', 'wall_r', 'shading']
    labels = ['None', 'wwr', 'shading', 'glazing', 'shgc', 'exterior_mat', 'exterior_t',
               'interior_mat', 'interior_t', 'wall_r']

    cities = ['all', 'Seattle', 'San Antonio', 'Milwaukee']
    programs = ['all', 'office', 'residential']
    orientations = ['all', 'n', 'w', 's', 'e']
    wwrs = ['all', '0', '20', '40', '60', '80']
    glazings = ['all', 'Double', 'Triple']
    ext_ts = ['all', '0', '4', '8']
    ext_ms = ['all', 'EPS', 'Polyiso']
    int_ts = ['all', '6', '8', '10']
    int_ms = ['all', 'Fiberglass', 'Cellulose']
    shgcs = ['all', '0.25', '0.6']
    shadings = ['all', '0.0', '2.5']

    wset = '20%'
    wfilt = '9%'

    app.layout = html.Div([
        html.Div([

            html.Div([
                html.Label('X axis'),
                dcc.Dropdown(
                    id='x_axis',
                    options=[{'label': i, 'value': i} for i in data_types],
                    clearable=False,
                    value='total_embodied', ),],
                    style={'width': wset, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}),

            html.Div([
                html.Label('Y axis'),
                dcc.Dropdown(
                    id='y_axis',
                    options=[{'label': i, 'value': i} for i in data_types],
                    clearable=False,
                    value='total_operational', ),],
                    style={'width': wset, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}),

            html.Div([
                html.Label('Color by'),
                dcc.Dropdown(
                    id='colors',
                    options=[{'label': i, 'value': i} for i in colors],
                    clearable=False,
                    value='city'),],
                    style={'width': wset, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}),    

            html.Div([
                html.Label('Size by'),
                dcc.Dropdown(
                    id='sizes',
                    options=[{'label': i, 'value': i} for i in sizes],
                    clearable=False,
                    value='None'),],
                    style={'width': wset, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}),  

            html.Div([
                html.Label('Label by'),
                dcc.Dropdown(
                    id='labels',
                    options=[{'label': i, 'value': i} for i in labels],
                    clearable=False,
                    value='None'),],
                    style={'width': wset, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}), 

        ]),


        html.Div([

            html.Div([
                html.Label('City'),
                dcc.Dropdown(
                    id='cities',
                    options=[{'label': i, 'value': i} for i in cities],
                    clearable=False,
                    value='all', ),],
                    style={'width': wfilt, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}),

            html.Div([
                html.Label('Program'),
                dcc.Dropdown(
                    id='programs',
                    options=[{'label': i, 'value': i} for i in programs],
                    clearable=False,
                    value='all'),],
                    style={'width': wfilt, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}),


            html.Div([
                html.Label('Orientation'),
                dcc.Dropdown(
                    id='orientations',
                    options=[{'label': i, 'value': i} for i in orientations],
                    clearable=False,
                    value='all'),],
                    style={'width': wfilt, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}),    

            html.Div([
                html.Label('WWR'),
                dcc.Dropdown(
                    id='wwrs',
                    options=[{'label': i, 'value': i} for i in wwrs],
                    clearable=False,
                    value='all'),],
                    style={'width': wfilt, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}),    

            html.Div([
                html.Label('Glazing'),
                dcc.Dropdown(
                    id='glazings',
                    options=[{'label': i, 'value': i} for i in glazings],
                    clearable=False,
                    value='all'),],
                    style={'width': wfilt, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}),   

            html.Div([
                html.Label('Ext thick'),
                dcc.Dropdown(
                    id='ex_thicks',
                    options=[{'label': i, 'value': i} for i in ext_ts],
                    clearable=False,
                    value='all'),],
                    style={'width': wfilt, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}), 

            html.Div([
                html.Label('Ext Material'),
                dcc.Dropdown(
                    id='ex_mats',
                    options=[{'label': i, 'value': i} for i in ext_ms],
                    clearable=False,
                    value='all'),],
                    style={'width': wfilt, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}), 


            html.Div([
                html.Label('Int thick'),
                dcc.Dropdown(
                    id='in_thicks',
                    options=[{'label': i, 'value': i} for i in int_ts],
                    clearable=False,
                    value='all'),],
                    style={'width': wfilt, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}), 

            html.Div([
                html.Label('Int Material'),
                dcc.Dropdown(
                    id='in_mats',
                    options=[{'label': i, 'value': i} for i in int_ms],
                    clearable=False,
                    value='all'),],
                    style={'width': wfilt, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}), 

            html.Div([
                html.Label('Solar HGC'),
                dcc.Dropdown(
                    id='shgcs',
                    options=[{'label': i, 'value': i} for i in shgcs],
                    clearable=False,
                    value='all'),],
                    style={'width': wfilt, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}), 

            html.Div([
                html.Label('Shading'),
                dcc.Dropdown(
                    id='shadings',
                    options=[{'label': i, 'value': i} for i in shadings],
                    clearable=False,
                    value='all'),],
                    style={'width': wfilt, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}), 


                    ]),

        dcc.Graph(id='indicator-graphic'),

        dcc.Slider(
            id='year',
            min=1,
            max=50,
            step=1,
            value=1,
            marks={i:str(i) for i in list(range(1, 30))},
        ),
        html.Div(id='slider-output-container')
    ])

    @app.callback(
        Output('indicator-graphic', 'figure'),
        Input('x_axis', 'value'),
        Input('y_axis', 'value'),
        Input('colors', 'value'),
        Input('sizes', 'value'),
        Input('labels', 'value'),
        Input('year', 'value'),
        Input('cities', 'value'),
        Input('programs', 'value'),
        Input('orientations', 'value'),
        Input('wwrs', 'value'),
        Input('glazings', 'value'),
        Input('ex_thicks', 'value'),
        Input('ex_mats', 'value'),
        Input('in_thicks', 'value'),
        Input('in_mats', 'value'),
        Input('shgcs', 'value'),
        Input('shadings', 'value'),
        )
    def update_graph(x_axis, y_axis, color, size, lable, year,
                     city, program, orient, wwr, glazing, ext_thick, 
                     ext_mat, in_thick, in_mat, shgc, shading):
        hd = ['total_embodied','total_operational','wwr','glazing','orient']
        labdict = {'total_embodied': 'total_embodied (kg CO2e / ft^2)',
                   'total_operational': 'total_operational (kg CO2e / ft^2 year )',
                   'op_nonlinear{}'.format(year): 'operational non-linear year {} (kg CO2e / ft^2)'.format(year),
                   'total_nonlinear{}'.format(year): 'total non-linear year {} (kg CO2e / ft^2)'.format(year),
                   'window_embodied':'window_embodied (kg CO2e / ft^2)',
                   'wall_embodied':'wall_embodied (kg CO2e / ft^2)',
                   'total_cooling':'total_cooling',
                   'total_heating':'total_heating',
                   'total_lighting':'total_lighting',
                   'max_cooling':'max_cooling', 
                   'max_heating':'max_heating',
                   'max_lighting':'max_lighting',
                   'max_solar':'max_solar_gains',
                   }

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

        if glazing != 'all':
            mask = (df['glazing'] == glazing)
            df = df[mask]
        else:
            df = df

        if ext_thick != 'all':
            mask = (df['exterior_t'] == float(ext_thick))
            df = df[mask]
        else:
            df = df

        if ext_mat != 'all':
            mask = (df['exterior_mat'] == ext_mat)
            df = df[mask]
        else:
            df = df

        if in_thick != 'all':
            mask = (df['interior_t'] == int(in_thick))
            df = df[mask]
        else:
            df = df

        if in_mat != 'all':
            mask = (df['interior_mat'] == in_mat)
            df = df[mask]
        else:
            df = df

        if shgc != 'all':
            mask = (df['shgc'] == float(shgc))
            df = df[mask]
        else:
            df = df

        if shading != 'all':
            mask = (df['shading'] == float(shading))
            df = df[mask]
        else:
            df = df

        if color == 'None':
            color = None

        if lable == 'None':
            lable = None

        if size == 'None':
            size = None

        if y_axis == 'total_nonlinear':
            y_axis = 'total_nonlinear{}'.format(year)
        if x_axis == 'total_nonlinear':
            x_axis = 'total_nonlinear{}'.format(year)
        
        if y_axis == 'op_nonlinear':
            y_axis = 'op_nonlinear{}'.format(year)
        if x_axis == 'op_nonlinear':
            x_axis = 'op_nonlinear{}'.format(year)

        fig = px.scatter(df,
                         x=x_axis,
                         y=y_axis,
                         color=color,
                         size=size,
                         size_max=10,
                         text=lable,
                         hover_data=hd,
                         labels=labdict,
                        )
        
        string = 'City: {} | Program: {} | Orientation: {} | WWR: {}'
        fig.update_layout(title={'text':string.format(city, program, orient, wwr)},
                          hovermode='closest',
                          autosize=False,
                          height=gheight,
                          width=gwidth,
                        )
        
        fig.update_traces(textposition='top right')
        # fig.update_traces(marker_sizemin = 5) 
        return fig

    app.run_server(debug=True)


if __name__ == '__main__':
    #TODO: When sizing by WWR, size can go to zero, hiding data. FIX!
    for i in range(50): print('')
    folderpath = '/Users/tmendeze/Documents/UW/03_publications/studio2021/envelope_paper/all_data_'
    # folderpath = '/Users/time/Documents/UW/03_publications/studio2021/envelope_paper/all_data_'
    data, frame = load_jsons_pandas(folderpath)
    dash_pareto_pandas(frame, 800, 1300)
    # keys = list(data.keys())[9900]
    # plot_lifecycle(data, keys=[keys])

