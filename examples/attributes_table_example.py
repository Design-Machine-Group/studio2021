from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"

from studio2021.datastructures import Building
from studio2021.datastructures import Seattle



for i in range(60): print()

b = Building(gsf=50e3,
            retail_percent=.2,
            office_percent=.4,
            residential_percent=.4,
            site_area=10e3,
            out_amenity_percent=.05,
            pv_percent=1.2,
            green_percent=.05)
c = Seattle()

b.compute_occupancy(c)
print(b)
print(b.occupants)