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
window: {}
wall: {}
embodied: {}

"""

class Envelope(object):
    
    def __init__(self, wwr, wall, window):
        self.name = 'Base envelope'
        self.wwr = wwr
        self.wall = wall
        self.window = window
    
    def __str__(self):
        return TPL.format(self.name, self.wwr, self.window.name, self.wall.name, self.embodied)
    
    @property
    def embodied(self):
        if self.window:
            win = self.window.embodied
        else:
            win = 0
        if self.wall:
            wall = self.wall.embodied
        else:
            wall = 0
        return win + wall

TPL_wall = """
################################################################################
Wall datastructure: {}
################################################################################

area: {}
embodied: {}

"""

class BaseWall(object):
    
    def __init__(self, area):
        self.name = 'Base wall'
        self.area = area
        self.layers = {}

    
    def __str__(self):
        return TPL_wall.format(self.name, self.area, self.embodied)

    @property
    def embodied(self):
        embodied = 0
        for lay in self.layers:
            embodied += self.layers[lay]['kgco2e_ft2']
        return self.area * embodied

TPL_win = """
################################################################################
Window datastructure: {}
################################################################################

area: {}
perimeter: {}
embodied: {}

"""

class BaseWindow(object):

    def __init__(self, area, perimeter):
        self.name = 'Base window'
        self.area = area
        self.perimeter = perimeter
        self.profile_kgco2e_ft = None
        self.layers = {}

    def __str__(self):
        return TPL_win.format(self.name, self.area, self.perimeter, self.embodied)

    @property
    def embodied(self):
        embodied = 0
        for lay in self.layers:
            embodied += self.layers[lay]['kgco2e_ft2']
        return (self.area * embodied) + (self.perimeter * self.profile_kgco2e_ft)


if __name__ == "__main__":
    wwr = .8
    wall = BaseWall(10.)
    wall.layers = {'finish':{'kgco2e_ft2': 2.},
                   'insulation':{'kgco2e_ft2': .3}
                  }
    window = BaseWindow(9., 12.)
    window.layers = {'glass1': {'kgco2e_ft2': 3.},
                     'glass2': {'kgco2e_ft2': 3.}}
    window.profile_kgco2e_ft = 3.

    e = Envelope(wwr, wall, window)
    print(e)
    print(wall)
    print(window)