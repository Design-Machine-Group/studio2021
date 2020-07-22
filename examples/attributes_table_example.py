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

import random

for i in range(60): print()

seattle = Seattle()
for i in range(100):
    x1 = random.random()
    x2 = random.random()
    b = Building(gsf= x1 * 100000,
                retail_percent= x2,
                office_percent= (1 - x2) / 2.,
                residential_percent= (1 - x2) / 2.,
                site_area= x1 * 10000,
                out_amenity_percent=.05,
                pv_percent=1.2,
                green_percent=.05,
                city=seattle)

    path = studio2021.TEMP
    filename = 'seattle_{}.json'.format(datetime.now())
    b.to_json(path, filename)