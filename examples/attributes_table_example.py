from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"

import os
import time
from datetime import datetime

import studio2021
from studio2021.datastructures import Building
from studio2021.datastructures import Seattle
from studio2021.plotters import plot_all_buildings

import random

for i in range(60): print()

path = studio2021.TEMP  
filename = 'seattle_{}.json'.format(datetime.now())

seattle = Seattle()

# b = Building(gsf= 60000,
#             retail_percent= .2,
#             office_percent= .6,
#             residential_percent= .2,
#             site_area= 10000,
#             out_amenity_percent=.05,
#             pv_percent=1.2,
#             green_percent=.05,
#                 city=seattle)

# filename = 'seattle_{}.json'.format(datetime.now())
# b.to_json(path, filename)
# print(b)

for i in range(100):
    x1 = random.random() + 1
    x2 = random.random()
    # x2 = (1 / 100.) * i
    b = Building(gsf= 50000,
                retail_percent= (1 - x2) / 2.,
                office_percent= x2,
                residential_percent= (1 - x2) / 2.,
                site_area= 10000,
                out_amenity_percent=.05,
                pv_percent=1.2,
                green_percent=.05,
                city=seattle)

    path = studio2021.TEMP
    filename = 'seattle_{}.json'.format(datetime.now())
    b.to_json(path, filename)

print(b)
plot_all_buildings(path, ('energy_demand', 'total'), ('economy', 'cost'))