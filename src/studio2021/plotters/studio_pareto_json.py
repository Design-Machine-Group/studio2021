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
            data[city][program][key] = parse_building(b)
    return data


def parse_building(bldg):
    data = {}
    win  = bldg.envelope.window_embodied or 0.
    wall = bldg.envelope.wall_embodied or 0.
    zonek = list(bldg.eui_kgco2e.keys())[0]
    cool = bldg.eui_kgco2e[zonek]['cooling']
    heat = bldg.eui_kgco2e[zonek]['heating']
    light = bldg.eui_kgco2e[zonek]['lighting']
    hot = bldg.eui_kgco2e[zonek]['hot_water']
    eq = bldg.eui_kgco2e[zonek]['equipment']

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
    programs = list(data['seattle'].keys())
    dtkey = list(data['seattle']['residential'].keys())[0]
    data_types = list(data['seattle']['residential'][dtkey].keys())

    app.layout = html.Div([
        html.Div([

            html.Div([
                dcc.Dropdown(
                    id='cities',
                    options=[{'label': i, 'value': i} for i in cities],
                    value='seattle'
                ),
            ],
            style={'width': '25%', 'display': 'inline-block', 'font-family':'open sans'}),

            html.Div([
                dcc.Dropdown(
                    id='programs',
                    options=[{'label': i, 'value': i} for i in programs],
                    value='residential'
                ),
            ],
            style={'width': '25%', 'display': 'inline-block', 'font-family':'open sans'}),


            html.Div([
                dcc.Dropdown(
                    id='xaxis',
                    options=[{'label': i, 'value': i} for i in data_types],
                    value='total_embodied'
                ),
            ],
            style={'width': '25%', 'display': 'inline-block', 'font-family':'open sans'}),

            html.Div([
                dcc.Dropdown(
                    id='yaxis',
                    options=[{'label': i, 'value': i} for i in data_types],
                    value='total_operational'
                ),
            ],style={'width': '25%', 'display': 'inline-block', 'font-family':'open sans'})
        ]),

        dcc.Graph(id='indicator-graphic'),
    ])

    @app.callback(
        Output('indicator-graphic', 'figure'),
        Input('cities', 'value'),
        Input('programs', 'value'),
        Input('xaxis', 'value'),
        Input('yaxis', 'value'))
    def update_graph(city, program, kx, ky):

        # city = 'seattle'
        # program = 'office'
        x = []
        y = []
        text = []
        for k in data[city][program]:
            x.append(data[city][program][k][kx])
            y.append(data[city][program][k][ky])
            text.append(k)

        fig = px.scatter(x=x, y=y, hover_name=text, )
        fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest', )
        return fig
    app.run_server(debug=True)


if __name__ == '__main__':
    for i in range(50): print('')

    folderpath = '/Users/tmendeze/Documents/UW/03_publications/studio2021/envelope_paper/data'
    data = load_jsons(folderpath)
    # plot_pareto(data)
    dash_pareto(data)

