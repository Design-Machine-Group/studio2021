from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"


TPL = """
################################################################################
Structure datastructure: {}
################################################################################

span:   {}

"""

class Structure(object):
    def __init__(self, area, span):
        self.name = 'Structure testing'
        self.area = area
        self.span = span
    
    def __str__(self):
        return TPL.format(self.name, self.span)

    def embodied(self):
        return 30

if __name__ == "__main__":
    span = 10
    area = 20
    s = Structure(area, span)
    print(s)