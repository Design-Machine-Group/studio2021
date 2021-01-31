from __future__ import print_function

import os
import math
import json

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"

#TODO: The Building object has all the data to compute embodied and store operational data
# Write embodied using structure, envelope custom objects
# Write pareto plotting


TPL = """
#########################################
Building data structure: {}
#########################################
"""

class Building(object):

    def __init__(self):
        self.__name__   = 'Studio2021_Building'
        self.zones      = {}
        self.ceil       = {}
        self.floor      = {}
        self.zone_fa    = {}
        self.adia_w     = {}
        self.fa         = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.wa         = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.oa         = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.wwr        = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.shgc       = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.shd        = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.ew         = {'n':{}, 's':{}, 'e':{}, 'w':{}}

    def __str__(self):
        return TPL.format(self.__name__)

    def to_json(self, path, filename):
        data = self.data
        data['filename'] = filename
        filepath = os.path.join(path, filename)
        with open(filepath, 'w+') as f:
            json.dump(data, f)

    def from_json(self):
        pass
    
    @property
    def data(self):
        data = {}
        return data
