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
        self.__name__               = 'Generic City'
        self.ocupants               = {'office':None, 
                                       'residential':None, 
                                       'retail':None}

        self.energy                 = {'office':{}, 
                                       'residential':{}, 
                                       'retail':{}}

        self.solar_production       = {'day':None,
                                       'year':None, 
                                       'efficiency': None, 
                                       'kBtu': None}

        self.kwh_to_kbtu            = None

        self.water                  = {'office':{},
                                       'residential':{}, 
                                       'retail':{},
                                       'irrigation':{}}

    def __str__(self):
        return TPL.format(self.__name__)
    
    def __repr__(self):
        return '{}()'.format(self.__name__)


    def compute_demand(self):
        self.energy['office']['25'] = self.energy['office']['2015_TPP'] * .75
        self.energy['office']['50'] = self.energy['office']['25'] * .5

        self.energy['residential']['25'] = self.energy['residential']['2015_TPP'] * .75
        self.energy['residential']['50'] = self.energy['residential']['25'] * .5

        self.energy['retail']['25'] = self.energy['retail']['2015_TPP'] * .75
        self.energy['retail']['50'] = self.energy['retail']['25'] * .5

    def compute_solar(self):
        self.solar_production['year'] = self.solar_production['day'] * 365
        self.solar_production['solar_efficiency'] = self.solar_production['year'] * .2
        self.solar_production['kbtu'] = self.solar_production['solar_efficiency'] * self.kwh_to_kbtu

class Seattle(City):
    def __init__(self):
        super().__init__()
        self.__name__                   = 'Seattle'
        self.ocupants                   = {'office':140,
                                           'residential':500, 
                                           'retail':550}
        self.energy['office']           = {'2015_TPP':40}
        self.energy['residential']      = {'2015_TPP':35}
        self.energy['retail']           = {'2015_TPP':60}
        self.solar_production['day']    = 3.456 / 10.7639  # kwh/m2/day converted to kwh/ft2/yr
        self.kwh_to_kbtu                = 3.412

        self.water['office']           = {'wui':11, 'wui_high':5.1, 
                                          'flush':1.09, 'flush_high':.57}
        self.water['residential']      = {'wui':42, 'wui_high':20.1,
                                          'flush':2.91, 'flush_high':2.}
        self.water['retail']           = {'wui':5, 'wui_high':None}
        self.water['irrigation']       = {'wui':9.8, 'wui_high':None}

        self.compute_demand()
        self.compute_solar()
