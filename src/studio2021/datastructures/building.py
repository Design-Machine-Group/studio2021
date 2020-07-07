from __future__ import print_function

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

    def __init__(self, gsf, retail_percent, office_percent, residential_percent):
        self.__name__               = 'StudioBuilding'
        self.gsf                    = gsf
        self.retail_percent         = retail_percent
        self.retail_area            = gsf * retail_percent    
        self.office_percent         = office_percent
        self.office_area            = gsf * office_percent  
        self.residential_percent    = residential_percent
        self.residential_area       = gsf * residential_percent  

        self.percentage_check()

    def __str__(self):
        return TPL.format(self.__name__,self.retail_area,self.office_area, self.residential_area)
    
    def percentage_check(self):
        tot_percent =  self.retail_percent + self.office_percent + self.residential_percent
        if tot_percent > 1.:
            raise NameError('The percentages too high')
        elif tot_percent < 1.:
            raise NameError('The percentages are too low')