import plotly.express as px
import pandas as pd
import os
import sys
import studio2021


def import_data(path):
    """
    Imports .csv data files for visualization.
    Currently only brings in one .csv- this will be expanded to loop, which will search directory for all .csv
    """
    fh = open(path, 'r')
    df = pd.read_csv(fh)
    return df


def plot_data(df, x_axis, y_axis, color):
    """
    Plots selected data on x and y axes from pandas dataframe.
    """
    fig = px.histogram(df, x=x_axis, y=y_axis, color=color)
    fig.show()
    return


if __name__ == "__main__":
    folder = studio2021.DATA
    path = os.path.join(folder, 'test_data.csv')
    # path = os.path.join('/Users/preston/Documents/GitHub/studio2021/data/5zone_run1.csv')
    df = import_data(path)
    plot_data(df, x_axis='Zones', y_axis='Total EUI (kBTU/sf/year)',
              color=pd.Series('Cooling EUI (kBTU/sf/year)', 'Heating EUI (kBTU/sf/year)',
                              'Lighting EUI (kBTU/sf/year)', 'Equip EUI (kBTU/sf/year)'))
