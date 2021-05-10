import os
import json
from ast import literal_eval

from studio2021.datastructures import Building
from studio2021.datastructures import CSV_Result

import matplotlib.pyplot as plt
import plotly.graph_objects as go

TPL = """
Wall R = {}<br>
Win  U = {}<br>
WWR  N = {}<br>
WWR  S = {}<br>
WWR  E = {}<br>
WWR  W = {}
"""


def read_jsons(jsons):
    buildings = [Building.from_json(j) for j in jsons]
    return buildings

def read_csvs(csvs):
    buildings = [CSV_Result(j) for j in csvs]
    return buildings

def plotly_pareto_csvs(buildings):
    color = {'Seattle': 'red', 'San Antonio': 'blue', 'Milwaukee': 'yellow'}
    data = {'Milwaukee':{'x':[], 'y':[], 'text':[]},
            'San Antonio':{'x':[], 'y':[], 'text':[]},
            'Seattle':{'x':[], 'y':[], 'text':[]}}
    

    for b in buildings:
        area = b.floor_area
        x = b.emb_tot / area
        y = b.op_tot / area
        if b.wall_r:
            text = b.wall_r
            data[b.city]['x'].append(x)
            data[b.city]['y'].append(y)
            data[b.city]['text'].append(TPL.format(round(b.wall_r, 2),
                                                   round(b.win_u, 3),
                                                   b.wwr_n,
                                                   b.wwr_s,
                                                   b.wwr_e,
                                                   b.wwr_w))
    
    fig = go.Figure()
    for city in data:
        x = data[city]['x']
        y = data[city]['y']
        text = data[city]['text']
        fig.add_trace(go.Scatter(name=city,
                                 x=x,
                                 y=y,
                                 mode='markers',
                                 hovertext=text,
                                 marker=dict(color=color[city],
                                             size=12,
                                             line=dict(color='black',
                                                    width=1))))

    xaxis = go.layout.XAxis(title='{}'.format('Embodied (kg Co2 / ft2)'))
    yaxis = go.layout.YAxis(title='{}'.format('Operational (kg Co2 / year x ft2)'))
    fig.update_layout(title={'text': 'Design Technology Studio 2021 - Pareto Front'},
                      xaxis=xaxis,
                      yaxis=yaxis,
                      hovermode='closest')
    fig.show()

if __name__ == '__main__':
    for i in range(50): print('')

    studio_out = '/Users/tmendeze/Documents/UW/02_teaching/00_courses/mendez_meek_2021/05_output'
    folders = next(os.walk(studio_out))[1]

    csvs = []
    jsons = []
    for folder in folders:
        path = os.path.join(studio_out, folder)
        files = folders = next(os.walk(path))[2]
        for f in files:
            if f.endswith('.json'):
                jsons.append(os.path.join(path, f))
            elif f.endswith('.csv'):
                csvs.append(os.path.join(path, f))

    # jbldgs = read_jsons(jsons)
    cbldgs = read_csvs(csvs)
    plotly_pareto_csvs(cbldgs)