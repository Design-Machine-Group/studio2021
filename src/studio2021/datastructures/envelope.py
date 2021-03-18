from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"

from studio2021.functions import read_materials
from studio2021.functions import read_glazing


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
    
    def __init__(self, 
                 opaque_areas,
                 window_areas,
                 external_insulation,
                 insulation_thickness,
                 facade_cladding,
                 glazing_system):
        self.name                   = 'Base envelope'
        self.opaque_areas           = opaque_areas
        self.window_areas           = window_areas
        self.external_insulation    = external_insulation
        self.insulation_thickness   = insulation_thickness
        self.facade_cladding        = facade_cladding
        self.glazing_system         = glazing_system

        self.wall_embodied = None
        self.window_embodied = None
    

    def compute_embodied(self):

        tot_opaque = 0.  # this should be in feet?
        tot_win = 0.     # this should be in feet?
        for okey in self.opaque_areas:
            for zkey in self.opaque_areas[okey]:
                tot_opaque += self.opaque_areas[okey][zkey]
                tot_win += self.window_areas[okey][zkey]

        ins_mat = self.external_insulation
        ins_thick = float(self.insulation_thickness) / 12. # currently in inches
        ins_emb = float(read_materials(ins_mat)['embodied_carbon']) * 27.  # currently (kgCO2/yd3)
        ins_emb = tot_opaque * ins_thick * ins_emb 

        fac_mat = self.facade_cladding
        fac_thick = float(read_materials(fac_mat)['thickness_in']) / 12. # currently (kgCO2/yd3)
        fac_emb = float(read_materials(fac_mat)['embodied_carbon']) * 27. # currently (kgCO2/yd3)
        fac_emb = tot_opaque * fac_thick * fac_emb 

        int_mat = self.facade_cladding
        int_thick = float(read_materials(int_mat)['thickness_in']) # currently (kgCO2/yd3)
        int_emb = float(read_materials(int_mat)['embodied_carbon']) # currently (kgCO2/yd3)
        int_emb = tot_opaque * int_thick * int_emb 
        
        win_sys = self.glazing_system
        win_emb = float(read_glazing(win_sys)['embodied_carbon_imperial']) # currently (KgCO2/ft2)
        win_emb = tot_win * win_emb

        self.wall_embodied =  int_emb + fac_emb + int_emb
        self.window_embodied = win_emb



if __name__ == "__main__":
    pass