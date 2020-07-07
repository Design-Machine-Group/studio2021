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
        self.energy     = {'office':None, 'residential':None, 'retail':None}
    
    def __str__(self):
        return TPL.format(self.__name__)


class Seattle(City):
    def __init__(self):
        super().__init__()
        self.__name__   = 'Seattle'
        self.ocupants   = {'office':140, 'residential':500, 'retail':550}
