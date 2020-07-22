from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"

import os
import json
import matplotlib.pyplot as plt

def plot_all_buildings(path):
    f1, f2 = [], []
    for filename in os.listdir(path):
        if filename.endswith('json'):
            filepath = os.path.join(path, filename)
            with open(filepath, 'r') as fp:
                data = json.load(fp)
                f1.append(data['office_area'])
                f2.append(data['retail_area'])
    plt.scatter(f1, f2)
    plt.grid(True)
    plt.show()


    # dot = ['r', 'b', 'k']
    # size = [80, 80, 80]
    
    # for i, x in enumerate(pop):
    #     f1, f2 = x[fit_indices[0]], x[fit_indices[1]]
    #     pf_index =  find_in_front(i, pf)
    #     if pf_index > 2:
    #         pf_index = 2
    #     plt.scatter(f1, f2, s=size[pf_index], c=dot[pf_index], edgecolors='k')
    # plt.grid(True)
    # plt.show()


if __name__ == "__main__":
    import studio2021

    for i in range(60): print()

    path = studio2021.TEMP  
    plot_all_buildings(path)