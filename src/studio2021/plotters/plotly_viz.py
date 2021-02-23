import plotly.graph_objects as go
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


def plot_data_by_EUI_type(dataset):
    """
    Plots selected data as a bar graph grouped by EUI type.
    """
    EUI_list = ['Cooling EUI (kBTU/sf/yr)', 'Heating EUI (kBTU/sf/yr)', 'Lighting EUI (kBTU/sf/yr)',
                'Equipment EUI (kBTU/sf/yr)', 'Total EUI (kBTU/sf/yr)']
    data = []
    for zone in dataset['zonenames']:
        data.append(go.Bar(name=zone, x=EUI_list, y=[dataset['zonedata'][zone]['cooling'], dataset['zonedata'][zone]['heating'],
                                                     dataset['zonedata'][zone]['lighting'], dataset['zonedata'][zone]['equipment'], dataset['zonedata'][zone]['total']]))
    fig = go.Figure(data=data)
    # Change the bar mode
    fig.update_layout(barmode='group')
    fig.show()
    return fig


def plot_data_by_zone(dataset):
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
    fig = go.Figure(data=data)
    # Change the bar mode
    fig.update_layout(barmode='group')
    fig.show()
    return fig


if __name__ == "__main__":
    dataset = read_data('test_data.csv')
    plot_data_by_EUI_type(dataset)
    plot_data_by_zone(dataset)
    # print(dataset)
