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

    filename = filename.split('_')
    data['orient'] = filename[1]
    data['wwr'] = bldg.wwr['n']
    data['glazing'] = gl_dict[bldg.glazing_system]
    data['shading'] = bldg.shade_depth_h['n']
    data['shgc'] = bldg.shade_gc['n']

    data['exterior_mat'] = bldg.external_insulation
    data['exterior_t (in)'] = bldg.insulation_thickness or 0.
    data['interior_mat'] = bldg.interior_insul_mat
    interior_thick = bldg.ewall_framing or 0.
    data['interior_t (in)'] = int_dict[interior_thick]

    area = bldg.floor_area
    win  = bldg.envelope.window_embodied or 0.
    wall = bldg.envelope.wall_embodied or 0.
    win /= area
    wall/= area

    data['Embodied (kg CO2e / ft2)'] = win + wall
    data['Win Embodied (kg CO2e / ft2)'] = win
    data['Wall Embodied (kg CO2e / ft2)'] = wall

    zonek = list(bldg.eui_kgco2e.keys())[0]
    cool = bldg.eui_kgco2e[zonek]['cooling'] / area
    heat = bldg.eui_kgco2e[zonek]['heating'] / area
    light = bldg.eui_kgco2e[zonek]['lighting'] / area
    hot = bldg.eui_kgco2e[zonek]['hot_water'] / area
    eq = bldg.eui_kgco2e[zonek]['equipment'] / area

    data['Operational (kg CO2e / ft2 * year)'] = cool + heat + light + hot + eq

    data['Cooling EUI (kBtu / ft2 * year)'] = bldg.eui_kbtu_ft[zonek]['cooling']
    data['Heating EUI (kBtu / ft2 * year)'] = bldg.eui_kbtu_ft[zonek]['heating']
    data['Lighting EUI (kBtu / ft2 * year)'] = bldg.eui_kbtu_ft[zonek]['lighting']

    data['Wall R (ft2 * F * h / BTU)'] = bldg.wall_r

    data['city'] = bldg.city
    data['program'] = pdict[bldg.zone_program]

    city_gwp = city_gwp[bldg.city]
    op = cool + heat + light + hot + eq
    tot_eui_kwh = bldg.eui_kwh[zonek]['total']
    eui = tot_eui_kwh / area
    emb = win + wall

    temp = 0
    imp = .05   
    for y in list(range(1, 30)):
        n = eui * city_gwp   
        data['Total GWP non-linear (kg CO2e / ft2) {} year'.format(y)] = n + temp + emb
        # data['Total GWP linear (kg CO2e / ft2) {} year'.format(y)] = op * y
        data['Operational GWP non-linear (kg CO2e / ft2) {} year'.format(y)] = n + temp
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


def dash_pareto_pandas(frame, gheight=800, gwidth=1200):
    app = dash.Dash(__name__)
    xy_axis = ['Embodied (kg CO2e / ft2)', 'Operational (kg CO2e / ft2 * year)',
               'Win Embodied (kg CO2e / ft2)', 'Wall Embodied (kg CO2e / ft2)',
               'Cooling EUI (kBtu / ft2 * year)', 'Heating EUI (kBtu / ft2 * year)',
               'Lighting EUI (kBtu / ft2 * year)',
               'Total GWP non-linear (kg CO2e / ft2) N year',
            #    'Total GWP linear (kg CO2e / ft2) N year',
               'Operational GWP non-linear (kg CO2e / ft2) N year',
                  ]

    colors = ['None', 'city', 'orient', 'wwr', 'glazing', 'program', 'Wall R (ft2 * F * h / BTU)',
              'shgc', 'exterior_mat', 'exterior_t (in)', 'interior_mat', 'interior_t (in)']
    
    sizes = ['None', 'wwr', 'exterior_t (in)', 'interior_t (in)', 'Wall R (ft2 * F * h / BTU)', 'shading']
    
    labels = ['None', 'wwr', 'shading', 'glazing', 'shgc', 'exterior_mat', 'exterior_t (in)',
               'interior_mat', 'interior_t (in)', 'Wall R (ft2 * F * h / BTU)']

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
                    options=[{'label': i, 'value': i} for i in xy_axis],
                    clearable=False,
                    value='Embodied (kg CO2e / ft2)', ),],
                    style={'width': wset, 'display': 'inline-block',
                           'font-family':'open sans', 'font-size':'8px'}),

            html.Div([
                html.Label('Y axis'),
                dcc.Dropdown(
                    id='y_axis',
                    options=[{'label': i, 'value': i} for i in xy_axis],
                    clearable=False,
                    value='Operational (kg CO2e / ft2 * year)', ),],
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

        hd = ['city', 'program', 'orient', 'wwr', 'glazing', 'exterior_t (in)',
             'exterior_mat', 'interior_t (in)', 'interior_mat', 'shgc', 'shading'
             ]

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
            mask = (df['exterior_t (in)'] == float(ext_thick))
            df = df[mask]
        else:
            df = df

        if ext_mat != 'all':
            mask = (df['exterior_mat'] == ext_mat)
            df = df[mask]
        else:
            df = df

        if in_thick != 'all':
            mask = (df['interior_t (in)'] == int(in_thick))
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

        if y_axis == 'Total GWP non-linear (kg CO2e / ft2) N year':
            y_axis = 'Total GWP non-linear (kg CO2e / ft2) {} year'.format(year)
        if x_axis == 'Total GWP non-linear (kg CO2e / ft2) N year':
            x_axis = 'Total GWP non-linear (kg CO2e / ft2) {} year'.format(year)
        
        if y_axis == 'Operational GWP non-linear (kg CO2e / ft2) N year':
            y_axis = 'Operational GWP non-linear (kg CO2e / ft2) {} year'.format(year)
        if x_axis == 'Operational GWP non-linear (kg CO2e / ft2) N year':
            x_axis = 'Operational GWP non-linear (kg CO2e / ft2) {} year'.format(year)

        fig = px.scatter(df,
                         x=x_axis,
                         y=y_axis,
                         color=color,
                         size=size,
                         size_max=10,
                         text=lable,
                         hover_data=hd,
                         labels=None,
                         color_continuous_scale='Viridis' # 'sunsetdark'
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
    # folderpath = 'C:/IDL/StudioTool/Paper/data/all_data_/all_data_'
    # folderpath = '/Users/time/Documents/UW/03_publications/studio2021/envelope_paper/all_data_'
    folderpath = '/Users/tmendeze/Documents/UW/03_publications/studio2021/envelope_paper/all_data_'
    data, frame = load_jsons_pandas(folderpath)
    dash_pareto_pandas(frame, 800, 1300)
    # keys = list(data.keys())[9900]
    # plot_lifecycle(data, keys=[keys])

