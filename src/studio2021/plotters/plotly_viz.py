import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import studio2021


def read_data(filename):
    """
    Imports .csv data files for visualization.
    Currently only brings in one .csv- this will be expanded to loop, which will search directory for all .csv
    """
    filepath = os.path.join(studio2021.DATA, filename)
    fh = open(filepath, 'r')
    lines = fh.readlines()
    fh.close()
    del(lines[0])
    dataset = {'zonenames': [], 'zonedata': {}}
    for line in lines:
        zone, cooling, heating, lighting, equipment, total = line.split(',')
        dataset['zonenames'].append(zone)
        dataset['zonedata'][zone] = {'cooling': float(cooling), 'heating': float(heating), 'lighting': float(
            lighting), 'equipment': float(equipment), 'total': float(total)}
    return dataset


def data_by_EUI_type(dataset):
    """
    Plots selected data as a bar graph grouped by EUI type.
    """
    EUI_list = ['Cooling EUI (kBTU/sf/yr)', 'Heating EUI (kBTU/sf/yr)', 'Lighting EUI (kBTU/sf/yr)',
                'Equipment EUI (kBTU/sf/yr)', 'Total EUI (kBTU/sf/yr)']
    data = []
    for zone in dataset['zonenames']:
        data.append(go.Bar(name=zone, x=EUI_list, y=[dataset['zonedata'][zone]['cooling'], dataset['zonedata'][zone]['heating'],
                                                     dataset['zonedata'][zone]['lighting'], dataset['zonedata'][zone]['equipment'], dataset['zonedata'][zone]['total']]))
    return data


def data_by_zone(dataset):
    """
    Plots selected data as a bar graph grouped by zone.
    """
    eui_list = ['cooling', 'heating', 'lighting', 'equipment', 'total']
    EUI_types = ['Cooling EUI (kBTU/sf/yr)', 'Heating EUI (kBTU/sf/yr)', 'Lighting EUI (kBTU/sf/yr)',
                 'Equipment EUI (kBTU/sf/yr)', 'Total EUI (kBTU/sf/yr)']
    data = []
    for eui in eui_list:
        temp = []
        for zone in dataset['zonenames']:
            temp.append(dataset['zonedata'][zone][eui])
        data.append(go.Bar(name=eui, x=EUI_types, y=temp))
    return data


if __name__ == "__main__":
    dataset = read_data('test_data.csv')
    fig = make_subplots(rows=2, cols=5)
    fig1 = data_by_EUI_type(dataset)
    fig2 = data_by_zone(dataset)
    # by_EUI_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    fig.add_trace(fig1[0], row=1, col=1)
    fig.add_trace(fig1[1], row=1, col=2)
    fig.add_trace(fig1[2], row=1, col=3)
    fig.add_trace(fig1[3], row=1, col=4)
    fig.add_trace(fig1[4], row=1, col=5)
    fig.add_trace(fig2[0], row=2, col=1)
    fig.add_trace(fig2[1], row=2, col=2)
    fig.add_trace(fig2[2], row=2, col=3)
    fig.add_trace(fig2[3], row=2, col=4)
    fig.add_trace(fig2[4], row=2, col=5)
    fig.update_layout(autosize=True, title_text="EUI Visualizations")
    # fig.update_traces(patch={layout: {barmode: 'group'}})
    fig.update_xaxes(showgrid=False)
    fig.show()
