from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"

import os
import json
import matplotlib.pyplot as plt
import plotly.graph_objects as go

def plot_all_buildings_matplotlib(path):
    f1, f2, c = [], [], []
    for filename in os.listdir(path):
        if filename.endswith('json'):
            filepath = os.path.join(path, filename)
            with open(filepath, 'r') as fp:
                data = json.load(fp)
                f1.append(data['office_area'])
                f2.append(data['retail_area'])
                c.append('r')
    plt.scatter(f1, f2, c=c)
    plt.grid(True)
    plt.show()


def plot_all_buildings(path, f1, f2):
    # TODO: This could probably be better with Pandas or one single dict

    fig = go.Figure()

    x = []
    y = []
    text = []
    for filename in os.listdir(path):
        if filename.endswith('json'):
            filepath = os.path.join(path, filename)
            with open(filepath, 'r') as fp:
                data = json.load(fp)
                if type(f1) == str:
                    x.append(data[f1])
                else:
                    x.append(data[f1[0]][f1[1]])
                if type(f2) == str:
                    y.append(data[f2])
                else:
                    y.append(data[f2[0]][f2[1]])
                
                text.append('file={}'.format(data['filename']))

    fig.add_trace(go.Scatter(x=x,
                             y=y,
                             mode='markers',
                             text=text,
                            )
                )
    xaxis = go.layout.XAxis(title='{}'.format(f1))
    yaxis = go.layout.YAxis(title='{}'.format(f2))
    fig.update_layout(xaxis=xaxis,
                      yaxis=yaxis,
                      hovermode='closest')
    fig.show()



if __name__ == "__main__":
    import studio2021

    for i in range(60): print()

    path = studio2021.TEMP  
    plot_all_buildings(path, 'retail_area', ('energy_supply', 'total'))