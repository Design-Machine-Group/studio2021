import plotly.graph_objects as go
import os
import studio2021


def read_data():
    """
    Imports .csv data files for visualization.
    Currently only brings in one .csv- this will be expanded to loop, which will search directory for all .csv
    """
    filepath = os.path.join(studio2021.DATA, 'test_data.csv')
    fh = open(filepath, 'r')
    lines = fh.readlines()
    fh.close()
    del(lines[0])
    dataset = {}
    for line in lines:
        zones, cooling, heating, lighting, equipment, total = line.split(',')
        for i in cooling, heating, lighting, equipment, total:
            dataset[zone] = {'cooling': cooling, 'heating': heating, 'lighting': lighting, 'equipment': equipment, 'total': total}
    return dataset


def plot_data_by_EUI_type():
    """
    Plots selected data as a bar graph grouped by EUI type.
    """
    EUI_list = ['Cooling EUI (kBTU/sf/yr)', 'Heating EUI (kBTU/sf/yr)', 'Lighting EUI (kBTU/sf/yr)',
                'Equipment EUI (kBTU/sf/yr)', 'Total EUI (kBTU/sf/yr)']

    fig = go.Figure(data=[
        go.Bar(name='zone1', x=EUI_list, y=[2.96254, 8.231524, 1.925206, 12.201885, 25.321154]),
        go.Bar(name='zone2', x=EUI_list, y=[4.748404, 8.822211, 1.925206, 12.201885, 27.697705]),
        go.Bar(name='zone3', x=EUI_list, y=[4.348246, 3.661499, 1.925206, 12.201885, 22.136836]),
        go.Bar(name='zone4', x=EUI_list, y=[4.249787, 10.875947, 1.925206, 12.201885, 27.327619]),
        go.Bar(name='zone5', x=EUI_list, y=[1.244922, 0.696244, 1.925206, 12.201885, 16.068257]),
        go.Bar(name='total', x=EUI_list, y=[3.504748, 6.134613, 1.925206, 12.201885, 23.766452])
    ])
    # Change the bar mode
    fig.update_layout(barmode='group')
    fig.show()
    return


def plot_data_by_zone():
    """
    Plots selected data as a bar graph grouped by zone.
    """
    zone_list = ['zone1', 'zone2', 'zone3', 'zone4', 'zone5', 'total']

    fig = go.Figure(data=[
        go.Bar(name='Cooling EUI (kBTU/sf/yr)', x=zone_list, y=[2.96254, 4.748404, 4.348246, 4.249787, 1.244922, 3.504748]),
        go.Bar(name='Heating EUI (kBTU/sf/yr)', x=zone_list, y=[8.231524, 8.822211, 3.661499, 10.875947, 0.696244, 0.696244]),
        go.Bar(name='Lighting EUI (kBTU/sf/yr)', x=zone_list, y=[1.925206, 1.925206, 1.925206, 1.925206, 1.925206, 1.925206]),
        go.Bar(name='Equipment EUI (kBTU/sf/yr)', x=zone_list,
               y=[12.201885, 12.201885, 12.201885, 12.201885, 12.201885, 12.201885]),
        go.Bar(name='Total EUI (kBTU/sf/yr)', x=zone_list, y=[25.321154, 27.697705, 22.136836, 27.327619, 16.068257, 23.766452])
    ])
    # Change the bar mode
    fig.update_layout(barmode='group')
    fig.show()
    return


if __name__ == "__main__":
    plot_data_by_EUI_type()
    plot_data_by_zone()
