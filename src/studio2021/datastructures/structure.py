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
    def __init__(self, span):
        self.name = 'Structure testing'
        self.span = span
    
    def __str__(self):
        return TPL.format(self.name, self.span)


if __name__ == "__main__":
    span = 10
    s = Structure(span)
    print(s)