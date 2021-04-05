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
                 glazing_system,
                 height,
                 shade_depth_h,
                 shade_depth_v1,
                 shade_depth_v2,
                 wwr):
        self.name                   = 'Base envelope'
        self.opaque_areas           = opaque_areas
        self.window_areas           = window_areas
        self.external_insulation    = external_insulation
        self.insulation_thickness   = insulation_thickness
        self.facade_cladding        = facade_cladding
        self.glazing_system         = glazing_system
        self.height                 = height
        self.shade_depth_h          = shade_depth_h
        self.shade_depth_v1         = shade_depth_v1
        self.shade_depth_v2         = shade_depth_v2
        self.wwr                    = wwr

        self.wall_embodied = None
        self.window_embodied = None
    

    def compute_embodied(self):

        tot_opaque = 0.  # this should be in feet?
        tot_win = 0.     # this should be in feet?
        sides = {}
        for okey in self.opaque_areas:
            opaque_orient = 0
            win_orient = 0
            for zkey in self.opaque_areas[okey]:
                opaque_orient += self.opaque_areas[okey][zkey]
                win_orient += self.window_areas[okey][zkey]
            sides[okey] = (opaque_orient + win_orient) / self.height
            tot_opaque += opaque_orient
            tot_win += win_orient

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

        alum_emb = float(read_materials('Aluminum')['embodied_carbon']) * 27. # currently (kgCO2/yd3)

        self.shading_embodied = 0
        for okey in sides:
            side = sides[okey]
            numsec = round(side / 10., 0)
            secside = side / float(numsec)
            secarea = secside * self.height
            wwr = self.wwr[okey]
            h = self.height - 2
            x = (secarea * wwr) / h
            self.shading_embodied += (self.shade_depth_h[okey] * x * (1. /36.) * alum_emb) / 27.
        
        self.window_embodied += self.shading_embodied


if __name__ == "__main__":
    pass