from __future__ import print_function

import math

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"

TPL = """
################################################################################
Building data structure: {}
################################################################################

Areas
-----
Retail surface area {} sqft
Office surface area {} sqft
Residential surface area {} sqft

"""

class Building(object):

    def __init__(self,
                 gsf,
                 retail_percent,
                 office_percent,
                 residential_percent,
                 site_area,
                 out_amenity_percent,
                 pv_percent,
                 green_percent, city):
        
        self.__name__               = 'StudioBuilding'
        self.gsf                    = gsf
        self.retail_percent         = retail_percent
        self.office_percent         = office_percent
        self.residential_percent    = residential_percent
        self.site_area              = site_area
        self.out_amenity_percent    = out_amenity_percent
        self.pv_percent             = pv_percent
        self.green_percent          = green_percent
        self.city                   = city

        self.percentage_check()

    def __str__(self):
        return TPL.format(self.__name__,self.retail_area,self.office_area, self.residential_area)
    
    @property
    def office_area(self):
        return self.gsf * self.retail_percent  

    @property
    def retail_area(self):
        return self.gsf * self.office_percent  

    @property
    def residential_area(self):
        return self.gsf * self.residential_percent  

    @property
    def out_amenity_area(self):
        return self.site_area * self.out_amenity_percent  

    @property
    def pv_gross(self):
        return self.site_area * self.pv_percent  

    @property
    def pv_net(self):
        return .9 * self.pv_gross  

    @property
    def green_area(self):
        return self.site_area * self.green_percent  

    def percentage_check(self):
        tot_percent =  self.retail_percent + self.office_percent + self.residential_percent
        if tot_percent > 1.:
            raise NameError('The percentages too high')
        elif tot_percent < 1.:
            raise NameError('The percentages are too low')
    
    @property
    def occupants(self):
        occupants = {}
        occupants['office'] = math.ceil(self.office_area / float(self.city.ocupants['office']))
        occupants['residential'] = math.ceil(self.residential_area / float(self.city.ocupants['residential']))
        occupants['retail'] = math.ceil(self.retail_area / float(self.city.ocupants['retail']))
        occupants['total'] = occupants['retail'] + occupants['residential'] + occupants['office']
        return occupants

    def energy_demand(self):
        pass