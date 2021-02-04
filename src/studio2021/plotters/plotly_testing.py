import plotly.express as px
import pandas as pd
import os
import studio2021


def import_data(path):
    fh = open(path, 'r')
    df = pd.read_csv(fh)
    return df


def plot_data(data):
    fig = px.scatter()
    fig.show()
    return


if __name__ == "__main__":
    folder = studio2021.DATA
    path = os.path.join(folder, 'results_example.csv')
    df = import_data(path)
