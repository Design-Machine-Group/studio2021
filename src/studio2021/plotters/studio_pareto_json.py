import os

from studio2021.datastructures import Building
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import numpy as np


def load_jsons_pandas(folderpath):
    data = {}
    files = os.listdir(folderpath)
    for f in files[:200]:
        if f.endswith('json'):
            b = Building.from_json(os.path.join(folderpath, f))
            key = os.path.splitext(f)[0]
            data[key] = parse_building(b, f)
    frame = pd.DataFrame.from_dict(data, orient='index')
    return data, frame


def parse_building(bldg, filename):

    gl_dict = {'Aluminum Double': 'Double', 'Aluminum Triple': 'Triple'}
    # int_dict = {'2x6 Wood Studs':6, '2x8 Wood Studs':8, '2x10 Wood Studs':10, 0:0,
    #             '2x6 No Insulation':0, 'Steel 4':4, 'Steel 6':6, 'Steel 8':8,
    #             '2x4 Wood Studs':4,}
    pdict = {'2013::MidriseApartment::Apartment': 'residential',
             '2013::MediumOffice::OpenOffice': 'office'}


    city_gwp_d = {'San Antonio': 0.414311,
                'Seattle': 0.135669,
                'Milwaukee': 0.559278936,
                'New York': 0.171548494,
                'Los Angeles':0.175630822,
                'Atlanta': 0.399590512}

    data = {}

    filename = filename.split('_')
    data['orient'] = filename[1]
    data['wwr'] = bldg.wwr['n']
    data['glazing'] = gl_dict[bldg.glazing_system]
    data['shading'] = bldg.shade_depth_h['n']
    data['shgc'] = bldg.shade_gc['n']
    data['inf_rate'] = bldg.inf_rate

    data['exterior_mat'] = bldg.external_insulation
    data['exterior_t (in)'] = bldg.insulation_thickness or 0.
    data['interior_mat'] = bldg.interior_insul_mat
    data['interior_t (in)'] = bldg.int_ins_thickness or 0.

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

    data['Wall R (ft2 * F * h / BTU)'] = round(bldg.wall_r, 1)

    data['city'] = bldg.city
    data['program'] = pdict[bldg.zone_program]
    data['city_gwp'] = city_gwp_d[bldg.city]
    data['tot_eui_kwh'] = bldg.eui_kwh[zonek]['total']
    data['area'] = area

    # op = cool + heat + light + hot + eq
    tot_eui_kwh = bldg.eui_kwh[zonek]['total']
    eui = tot_eui_kwh / area
    emb = win + wall

    accl = 0
    acc2 = 0
    acc3 = 0
    acc5 = 0
    city_gwpl = data['city_gwp']
    city_gwp2 = data['city_gwp']
    city_gwp3 = data['city_gwp']
    city_gwp5 = data['city_gwp']
    delta2 = city_gwp2 * .02
    delta3 = city_gwp3 * .03
    delta5 = city_gwp5 * .05

    data['payback_linear'] = round(emb / (eui * city_gwpl), 2)

    for y in list(range(1, 51)):    
        opl_year_x = eui * city_gwpl
        op2_year_x = eui * city_gwp2
        op3_year_x = eui * city_gwp3
        op5_year_x = eui * city_gwp5

        data['Total GWP Linear (kg CO2e / ft2) {} year'.format(y)] = opl_year_x + accl + emb
        data['Op GWP Linear (kg CO2e / ft2) {} year'.format(y)] = opl_year_x + accl

        data['Total GWP non-linear 2% (kg CO2e / ft2) {} year'.format(y)] = op2_year_x + acc2 + emb
        data['Op GWP non-linear 2% (kg CO2e / ft2) {} year'.format(y)] = op2_year_x + acc2
        
        data['Total GWP non-linear 3% (kg CO2e / ft2) {} year'.format(y)] = op3_year_x + acc3 + emb
        data['Op GWP non-linear 3% (kg CO2e / ft2) {} year'.format(y)] = op3_year_x + acc3

        data['Total GWP non-linear 5% (kg CO2e / ft2) {} year'.format(y)] = op5_year_x + acc5 + emb
        data['Op GWP non-linear 5% (kg CO2e / ft2) {} year'.format(y)] = op5_year_x + acc5

        # non linear models - - - - - - -

        if city_gwp2 >= 0.:
            city_gwp2 -= delta2  # X% of initial city value, 5% gets to 0 (GWP/kWh) in 20y (Paris)

        if city_gwp3 >= 0.:
            city_gwp3 -= delta3  # X% of initial city value, 5% gets to 0 (GWP/kWh) in 20y (Paris)
        
        if city_gwp5 >= 0.:
            city_gwp5 -= delta5  # X% of initial city value, 5% gets to 0 (GWP/kWh) in 20y (Paris)
        
        accl += opl_year_x
        acc2 += op2_year_x
        acc3 += op3_year_x
        acc5 += op5_year_x

    return data


def plot_lifecycle(data, keys=None):
    ny = 50
    years = list(range(ny))
    fig = go.Figure()
    if not keys:
        keys = data.keys()
    for k in keys:
        op = data[k]['Operational (kg CO2e / ft2 * year)']
        bau = [op * i for i in years]
        eui = data[k]['tot_eui_kwh'] / data[k]['area']
        emb = [0]
        non2 = [0]
        non3 = [0]
        non5 = [0]
        acc2 = 0
        acc3 = 0
        acc5 = 0
        city_gwp2 = data[k]['city_gwp']
        city_gwp3 = data[k]['city_gwp']
        city_gwp5 = data[k]['city_gwp']
        delta2 = city_gwp2 * .02
        delta3 = city_gwp3 * .03
        delta5 = city_gwp5 * .05
        # tot = []
        for _ in years:
            op2_year_x = eui * city_gwp2
            op3_year_x = eui * city_gwp3
            op5_year_x = eui * city_gwp5

            non2.append(op2_year_x + acc2)
            non3.append(op3_year_x + acc3)
            non5.append(op2_year_x + acc5)

            emb.append(data[k]['Embodied (kg CO2e / ft2)'])
            # non linear models - - - - - - - - - - - - - - - - - - - - - - - - -

            # city_gwp *= (1 - imp)  # X% every year, never getting to 0 (GWP/kWh)

            if city_gwp2 >= 0.:
                city_gwp2 -= delta2  # X% of initial city value, 5% gets to 0 (GWP/kWh) in 20y (Paris)

            if city_gwp3 >= 0.:
                city_gwp3 -= delta3  # X% of initial city value, 5% gets to 0 (GWP/kWh) in 20y (Paris)
            
            if city_gwp5 >= 0.:
                city_gwp5 -= delta5  # X% of initial city value, 5% gets to 0 (GWP/kWh) in 20y (Paris)
            
            acc2 += op2_year_x
            acc3 += op3_year_x
            acc5 += op5_year_x


        fig.add_trace(go.Scatter(x=years, y=bau, name= 'BAU - {}'.format(k)))
        fig.add_trace(go.Scatter(x=years, y=non2, name= 'Non linear 2% - {}'.format(k)))
        fig.add_trace(go.Scatter(x=years, y=non3, name= 'Non linear 3% - {}'.format(k)))
        fig.add_trace(go.Scatter(x=years, y=non5, name= 'Non linear 5% - {}'.format(k)))
        fig.add_trace(go.Scatter(x=years, y=emb, name= 'Embodied - {}'.format(k)))


    fig.update_layout(title={'text':'Lifecycle Carbon emissions'},
                        hovermode='closest',
                        autosize=True,
                        xaxis_title="Year",
                        yaxis_title="GWP (kg CO2e / ft2)",
                    )

    fig.show()


def dash_pareto_pandas(frame, gheight=700, gwidth=1200):
    app = dash.Dash(__name__)
    xy_axis = ['Embodied (kg CO2e / ft2)', 'Operational (kg CO2e / ft2 * year)',
               'Win Embodied (kg CO2e / ft2)', 'Wall Embodied (kg CO2e / ft2)',
               'Cooling EUI (kBtu / ft2 * year)', 'Heating EUI (kBtu / ft2 * year)',
               'Lighting EUI (kBtu / ft2 * year)',
               'Op GWP Linear (kg CO2e / ft2) N year',
               'Op GWP non-linear 2% (kg CO2e / ft2) N year',
               'Op GWP non-linear 3% (kg CO2e / ft2) N year',
               'Op GWP non-linear 5% (kg CO2e / ft2) N year',
               'Total GWP Linear (kg CO2e / ft2) N year',
               'Total GWP non-linear 2% (kg CO2e / ft2) N year',
               'Total GWP non-linear 3% (kg CO2e / ft2) N year',
               'Total GWP non-linear 5% (kg CO2e / ft2) N year',
                  ]

    colors = ['None', 'city', 'orient', 'wwr', 'glazing', 'program',
              'Wall R (ft2 * F * h / BTU)', 'shgc', 'exterior_mat',
              'exterior_t (in)', 'interior_mat', 'interior_t (in)',
              'inf_rate', 'payback_linear']
    
    sizes = ['None', 'wwr', 'exterior_t (in)', 'interior_t (in)',
             'Wall R (ft2 * F * h / BTU)', 'shading', 'inf_rate',
             'payback_linear']
    
    labels = ['None', 'wwr', 'orient', 'shading', 'glazing', 'program',
              'shgc', 'exterior_mat', 'exterior_t (in)', 'interior_mat',
              'interior_t (in)', 'Wall R (ft2 * F * h / BTU)', 'inf_rate',
              'payback_linear']

    cities =        ['Seattle', 'San Antonio', 'Milwaukee',
                     'New York', 'Los Angeles', 'Atlanta']
    programs =      ['office', 'residential']
    orientations =  ['n', 'w', 's', 'e']
    wwrs =          ['0', '.2', '.4', '.6', '.8']
    glazings =      ['Double', 'Triple']
    ext_ts =        ['0', '.5', '1', '2', '3', '4', '5', '6']
    ext_ms =        ['EPS', 'Polyiso']
    int_ts =        ['0', '3.5', '5.5', '7.25', '9.25', '4', '6', '8']
    int_ms =        ['Fiberglass', 'Cellulose']
    shgcs =         ['0.25', '0.6']
    shadings =      ['0.0', '2.5']
    inf_rates =     ['0.00059', '0.0003', '0.00015']

    wset = '20%'
    wfilt = '8.33%'

    ddict1 = {'X axis': {'id': 'x_axis', 'list': xy_axis, 'value': 'Embodied (kg CO2e / ft2)', 'multi':False},
              'Y axis': {'id': 'y_axis', 'list': xy_axis, 'value': 'Operational (kg CO2e / ft2 * year)', 'multi':False},
              'Color by': {'id': 'colors', 'list': colors, 'value': 'city', 'multi':False},
              'Size by': {'id': 'sizes', 'list': sizes, 'value': 'None', 'multi':False},
              'Label by': {'id': 'labels', 'list': labels, 'value': 'None', 'multi':False},
            }

    ddict2 = {'City': {'id': 'cities', 'list': cities, 'value': cities, 'multi':True},
              'Program': {'id': 'programs', 'list': programs, 'value': programs, 'multi':True},
              'Orientation': {'id': 'orientations', 'list': orientations, 'value': orientations, 'multi':True},
              'WWR': {'id': 'wwrs', 'list': wwrs,'value': wwrs,'multi':True},
              'Glazing': {'id': 'glazings', 'list': glazings, 'value': glazings, 'multi':True},
              'Ext thick': {'id': 'ex_thicks', 'list': ext_ts, 'value': ext_ts, 'multi':True},
              'Ext Material': {'id': 'ex_mats', 'list': ext_ms, 'value': ext_ms, 'multi':True},
              'Int thick': {'id': 'in_thicks', 'list': int_ts, 'value': int_ts, 'multi':True},
              'Int Material': {'id': 'in_mats', 'list': int_ms, 'value': int_ms, 'multi':True},
              'Solar HGC': {'id': 'shgcs', 'list': shgcs, 'value': shgcs, 'multi':True},
              'Shading': {'id': 'shadings', 'list': shadings, 'value': shadings, 'multi':True},
              'Inf Rate': {'id': 'inf_rates', 'list': inf_rates, 'value': inf_rates, 'multi':True}
            }
    wlist = [wset, wfilt]
    dds = []
    for i, ddict in enumerate([ddict1, ddict2]):
        drop_width = wlist[i]
        temp = []
        for k in ddict:
            div = html.Div([html.Label(k),
                dcc.Dropdown(id=ddict[k]['id'],
                             multi=ddict[k]['multi'],
                             options=[{'label': i, 'value': i} for i in ddict[k]['list']],
                             clearable=False,
                             value=ddict[k]['value']),],
                             style={'width': drop_width, 'display': 'inline-block',
                                    'font-family':'open sans', 'font-size':'8px'})
            temp.append(div)
        dds.append(temp)

    graph = dcc.Graph(id='indicator-graphic')
    slider = dcc.Slider(id='year', min=1, max=51, step=1,value=1,
             marks={i:str(i) for i in list(range(1, 51))})
    slider_div = html.Div(id='slider-output-container')

    app.layout = html.Div([html.Div(dds[0]),
                           html.Div(dds[1]),
                           graph,
                           slider,
                           slider_div,
                           html.Button('Download CSV', id='btn_csv'),
                           dcc.Download(id='download-dataframe-csv'),
                           ]
                          )


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
        Input('inf_rates', 'value'),
        )
    def update_graph(x_axis, y_axis, color, size, lable, year,
                     city, program, orient, wwr, glazing, ext_thick, 
                     ext_mat, in_thick, in_mat, shgc, shading, inf_rate):

        hd = ['city', 'program', 'orient', 'wwr', 'glazing', 'exterior_t (in)',
             'exterior_mat', 'interior_t (in)', 'interior_mat', 'shgc', 'shading',
             'inf_rate', 'payback_linear'
             ]

        ld = {'city':{'list':city, 'name': 'city', 'float':False},
              'program':{'list':program, 'name': 'program', 'float':False},
              'orient':{'list':orient, 'name': 'orient', 'float':False},
              'glazing':{'list':glazing, 'name': 'glazing', 'float':False},
              'ext_mat':{'list':ext_mat, 'name': 'exterior_mat', 'float':False},
              'in_mat':{'list':in_mat, 'name': 'interior_mat', 'float':False},
              'shgc':{'list':shgc, 'name': 'shgc', 'float':True},
              'shading':{'list':shading, 'name': 'shading', 'float':True},
              'inf_rate':{'list':inf_rate, 'name': 'inf_rate', 'float':True},
              'wwr':{'list':wwr, 'name': 'wwr', 'float':True}, 
              'in_thick':{'list':in_thick, 'name': 'interior_t (in)', 'float':True},
              'ext_thick':{'list':ext_thick, 'name': 'exterior_t (in)', 'float':True},
              }
        
        df = frame
        for key in ld:
            masks = []
            for value in ld[key]['list']:
                if ld[key]['float']:
                    value = float(value)
                mask = df[ld[key]['name']] == value
                masks.append(mask)
            df = df[np.logical_or.reduce(masks)]

        if color == 'None':
            color = None

        if lable == 'None':
            lable = None

        if size == 'None':
            size = None

        if y_axis == 'Total GWP non-linear 2% (kg CO2e / ft2) N year':
            y_axis = 'Total GWP non-linear 2% (kg CO2e / ft2) {} year'.format(year)
        elif y_axis == 'Total GWP non-linear 3% (kg CO2e / ft2) N year':
            y_axis = 'Total GWP non-linear 3% (kg CO2e / ft2) {} year'.format(year) 
        elif y_axis == 'Total GWP non-linear 5% (kg CO2e / ft2) N year':
            y_axis = 'Total GWP non-linear 5% (kg CO2e / ft2) {} year'.format(year)        
        elif y_axis == 'Total GWP Linear (kg CO2e / ft2) N year':
            y_axis = 'Total GWP Linear (kg CO2e / ft2) {} year'.format(year)     

        if x_axis == 'Total GWP non-linear 2% (kg CO2e / ft2) N year':
            x_axis = 'Total GWP non-linear 2% (kg CO2e / ft2) {} year'.format(year)
        elif x_axis == 'Total GWP non-linear 3% (kg CO2e / ft2) N year':
            x_axis = 'Total GWP non-linear 3% (kg CO2e / ft2) {} year'.format(year) 
        elif x_axis == 'Total GWP non-linear 5% (kg CO2e / ft2) N year':
            x_axis = 'Total GWP non-linear 5% (kg CO2e / ft2) {} year'.format(year) 
        elif x_axis == 'Total GWP Linear (kg CO2e / ft2) N year':
            x_axis = 'Total GWP Linear (kg CO2e / ft2) {} year'.format(year)  
        
        if y_axis == 'Op GWP non-linear 2% (kg CO2e / ft2) N year':
            y_axis = 'Op GWP non-linear 2% (kg CO2e / ft2) {} year'.format(year)
        elif y_axis == 'Op GWP non-linear 3% (kg CO2e / ft2) N year':
            y_axis = 'Op GWP non-linear 3% (kg CO2e / ft2) {} year'.format(year) 
        elif y_axis == 'Op GWP non-linear 5% (kg CO2e / ft2) N year':
            y_axis = 'Op GWP non-linear 5% (kg CO2e / ft2) {} year'.format(year)      
        elif y_axis == 'Op GWP Linear (kg CO2e / ft2) N year':
            y_axis = 'Op GWP Linear (kg CO2e / ft2) {} year'.format(year)  

        if x_axis == 'Op GWP non-linear 2% (kg CO2e / ft2) N year':
            x_axis = 'Op GWP non-linear 2% (kg CO2e / ft2) {} year'.format(year)
        elif x_axis == 'Op GWP non-linear 3% (kg CO2e / ft2) N year':
            x_axis = 'Op GWP non-linear 3% (kg CO2e / ft2) {} year'.format(year) 
        elif x_axis == 'Op GWP non-linear 5% (kg CO2e / ft2) N year':
            x_axis = 'Op GWP non-linear 5% (kg CO2e / ft2) {} year'.format(year)    
        elif x_axis == 'Op GWP Linear (kg CO2e / ft2) N year':
            x_axis = 'Op GWP Linear (kg CO2e / ft2) {} year'.format(year)  

        fig = px.scatter(df,
                         x=x_axis,
                         y=y_axis,
                         color=color,
                         size=size,
                         size_max=12,
                         text=lable,
                         hover_data=hd,
                         labels=None,
                         color_continuous_scale='Viridis' # 'sunsetdark'
                        )
        
        string = 'Envelope carbon emissions'
        fig.update_layout(title={'text':string},
                          hovermode='closest',
                          autosize=False,
                          height=gheight,
                          width=gwidth,
                        )
        
        fig.update_traces(textposition='top right')
        fig.update_traces(marker_sizemin=3)
        return fig

    @app.callback(
        Output("download-dataframe-csv", "data"),
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
        Input('inf_rates', 'value'),
        Input('btn_csv', 'n_clicks'),
        prevent_initial_call=True,
        )
    def download_func(city, program, orient, wwr, glazing, ext_thick, ext_mat,
                      in_thick, in_mat, shgc, shading, inf_rate, n_clicks):

        ld = {'city':{'list':city, 'name': 'city', 'float':False},
              'program':{'list':program, 'name': 'program', 'float':False},
              'orient':{'list':orient, 'name': 'orient', 'float':False},
              'glazing':{'list':glazing, 'name': 'glazing', 'float':False},
              'ext_mat':{'list':ext_mat, 'name': 'exterior_mat', 'float':False},
              'in_mat':{'list':in_mat, 'name': 'interior_mat', 'float':False},
              'shgc':{'list':shgc, 'name': 'shgc', 'float':True},
              'shading':{'list':shading, 'name': 'shading', 'float':True},
              'inf_rate':{'list':inf_rate, 'name': 'inf_rate', 'float':True},
              'wwr':{'list':wwr, 'name': 'wwr', 'float':True}, 
              'in_thick':{'list':in_thick, 'name': 'interior_t (in)', 'float':True},
              'ext_thick':{'list':ext_thick, 'name': 'exterior_t (in)', 'float':True},
              }
        
        df = frame
        for key in ld:
            masks = []
            for value in ld[key]['list']:
                if ld[key]['float']:
                    value = float(value)
                mask = df[ld[key]['name']] == value
                masks.append(mask)
            df = df[np.logical_or.reduce(masks)] 
        
        changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
        if 'btn_csv' in changed_id:
            return dcc.send_data_frame(df.to_csv, 'filtered_data.csv')
    app.run_server(debug=True)


if __name__ == '__main__':
    import studio2021
    #TODO: When sizing by WWR, size can go to zero, hiding data. FIX!
    # for i in range(50): print('')
    # folderpath = 'C:/IDL/StudioTool/Paper/data/all_data_/all_data_'
    # folderpath = '/Users/time/Documents/UW/03_publications/studio2021/envelope_paper/all_data_'
    # folderpath = '/Users/tmendeze/Documents/UW/03_publications/studio2021/envelope_paper/all_data_'
    # folderpath = '/Users/tmendeze/Documents/UW/03_publications/studio2021/envelope_paper/temp_data'
    folderpath = studio2021.TEMP
    # folderpath = '/Users/tmendeze/Documents/UW/03_publications/studio2021/envelope_paper/r_data'
    data, frame = load_jsons_pandas(folderpath)
    # plot_lifecycle(data, keys=['la_w_40_1_1_office'])
    # frame.to_csv(os.path.join(studio2021.DATA, 'r_data.csv'))
    # filepath = os.path.join(studio2021.DATA, 'frames','assemblies_data.csv')
    # filepath = os.path.join(studio2021.DATA, 'frames', 'r_data.csv')
    # frame = pd.read_csv(filepath)
    dash_pareto_pandas(frame, 700, 1300)

