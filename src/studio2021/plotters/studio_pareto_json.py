import os
from studio2021.datastructures import Building
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
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


def parse_building(bldg, filename):
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

    filename = filename.split('_')
    data['orient'] = filename[1]
    data['wwr'] = bldg.wwr['n']
    data['glazing'] = bldg.glazing_system
    data['shading'] = bldg.shade_depth_h['n']
    data['shgc'] = bldg.shade_gc['n']
    data['exterior_mat'] = bldg.external_insulation
    data['exterior_t'] = bldg.insulation_thickness or 0.
    data['interior_mat'] = bldg.interior_insul_mat
    data['interior_t'] = bldg.ewall_framing

    data['total_embodied'] = win + wall
    data['window_embodied'] = win
    data['wall_embodied'] = wall
    data['cooling_operational'] = cool
    data['heating_operational'] = heat
    data['lighting_operational'] = light
    data['hot_water_operational'] = hot
    data['equipment_operational'] = eq
    data['total_operational'] = cool + heat + light + hot + eq
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
    dtkey = list(data['seattle']['residential'].keys())[0]
    data_types = list(data['seattle']['residential'][dtkey].keys())
    orientations = ['n', 'w', 's', 'e', 'all']
    wwrs = ['0', '20', '40', '60', '80', 'all']

    app.layout = html.Div([
        html.Div([

            html.Div([
                dcc.Dropdown(
                    id='cities',
                    options=[{'label': i, 'value': i} for i in cities],
                    value='all'
                ),
            ],
            style={'width': '15%', 'display': 'inline-block', 'font-family':'open sans'}),

            html.Div([
                dcc.Dropdown(
                    id='programs',
                    options=[{'label': i, 'value': i} for i in programs],
                    value='all'
                ),
            ],
            style={'width': '15%', 'display': 'inline-block', 'font-family':'open sans'}),


            html.Div([
                dcc.Dropdown(
                    id='orientations',
                    options=[{'label': i, 'value': i} for i in orientations],
                    value='all'
                ),
            ],
            style={'width': '15%', 'display': 'inline-block', 'font-family':'open sans'}),

            html.Div([
                dcc.Dropdown(
                    id='wwr',
                    options=[{'label': i, 'value': i} for i in wwrs],
                    value='all'
                ),
            ],
            style={'width': '15%', 'display': 'inline-block', 'font-family':'open sans'}),


            html.Div([
                dcc.Dropdown(
                    id='xaxis',
                    options=[{'label': i, 'value': i} for i in data_types],
                    value='total_embodied'
                ),
            ],
            style={'width': '15%', 'display': 'inline-block', 'font-family':'open sans'}),

            html.Div([
                dcc.Dropdown(
                    id='yaxis',
                    options=[{'label': i, 'value': i} for i in data_types],
                    value='total_operational'
                ),
            ],style={'width': '15%', 'display': 'inline-block', 'font-family':'open sans'})
        ]),

        dcc.Graph(id='indicator-graphic'),
    ])

    @app.callback(
        Output('indicator-graphic', 'figure'),
        Input('cities', 'value'),
        Input('programs', 'value'),
        Input('orientations', 'value'),
        Input('wwr', 'value'),
        Input('xaxis', 'value'),
        Input('yaxis', 'value'))
    def update_graph(city, program, orientation, wwr, kx, ky):

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
                    text.append(string.format(wwr_, o, gl, sh, shg, em, et, im, it))

                fig.add_trace(go.Scatter(name='{}_{}'.format(city, program),
                                        x=x,
                                        y=y,
                                        mode='markers',
                                        hovertext=text),)

                xaxis = go.layout.XAxis(title='{}'.format(kx))
                yaxis = go.layout.YAxis(title='{}'.format(ky))
                fig.update_layout(title={'text': 'Pareto Front'},
                                  xaxis=xaxis,
                                  yaxis=yaxis,
                                  hovermode='closest',
                                  autosize=False,
                                  height=900,
                                  width=1900,
                                  )
        return fig
    app.run_server(debug=True)


if __name__ == '__main__':
    folderpath = '/Users/tmendeze/Documents/UW/03_publications/studio2021/envelope_paper/data'
    data = load_jsons(folderpath)
    # plot_pareto(data)
    dash_pareto(data)

