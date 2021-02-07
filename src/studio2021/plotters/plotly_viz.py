import plotly.express as px
import pandas as pd
import os
import studio2021


def import_data(path):
    """
    Imports .csv data files for visualization.
    Currently only brings in one .csv- this will be expanded to loop, which will search directory for all .csv
    """
    fh = open(path, 'r')
    df = pd.read_csv(fh)
    return df


def plot_data(x_axis, y_axis):
    """
    Plots selected data on x and y axes from pandas dataframe.
    """
    fig = px.scatter()
    fig.show()
    return


if __name__ == "__main__":
    folder = studio2021.DATA
    path = os.path.join(folder, 'results_example.csv')
    df = import_data(path)
