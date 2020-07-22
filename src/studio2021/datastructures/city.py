from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"

TPL = """
################################################################################
City datastructure: {}
################################################################################

"""

class City(object):
    def __init__(self):
        self.__name__   = 'Generic City'
        self.ocupants   = {'office':None, 'residential':None, 'retail':None}
        self.energy     = {'office':{}, 'residential':{}, 'retail':{}}
    
    def __str__(self):
        return TPL.format(self.__name__)

    def compute_demand(self):
        self.energy['office']['25'] = self.energy['office']['2015_TPP'] * .75
        self.energy['office']['50'] = self.energy['office']['25'] * .5

        self.energy['residential']['25'] = self.energy['residential']['2015_TPP'] * .75
        self.energy['residential']['50'] = self.energy['residential']['25'] * .5

        self.energy['retail']['25'] = self.energy['retail']['2015_TPP'] * .75
        self.energy['retail']['50'] = self.energy['retail']['25'] * .5

class Seattle(City):
    def __init__(self):
        super().__init__()
        self.__name__   = 'Seattle'
        self.ocupants   = {'office':140, 'residential':500, 'retail':550}
        self.energy['office'] = {'2015_TPP':40}
        self.energy['residential'] = {'2015_TPP':35}
        self.energy['retail'] = {'2015_TPP':60}

        self.compute_demand()
