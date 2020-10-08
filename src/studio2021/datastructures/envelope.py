from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"


TPL = """
################################################################################
Envelope datastructure: {}
################################################################################

window-to-wall ratio:   {}

"""

class Envelope(object):
    def __init__(self, wwr, wall, window):
        self.name = 'Envelope testing'
        self.wwr = wwr
        self.wall = wall
        self.window = window
    
    def __str__(self):
        return TPL.format(self.name, self.wwr)

if __name__ == "__main__":
    wwr = .8
    wall = None
    window = None

    e = Envelope(wwr, wall, window)
    print(e)