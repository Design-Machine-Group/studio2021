from __future__ import print_function

__author__ = ["Tomas Mendez Echenagucia"]
__copyright__ = "Copyright 2020, Design Machine Group - University of Washington"
__license__ = "MIT License"
__email__ = "tmendeze@uw.edu"
__version__ = "0.1.0"

from ast import literal_eval

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
    
    def __init__(self):
        self.opaque_areas           = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.window_areas           = {'n':{}, 's':{}, 'e':{}, 'w':{}}
        self.external_insulation    = None
        self.insulation_thickness   = None
        self.facade_cladding        = None
        self.glazing_system         = None
        self.height                 = None
        self.shade_depth_h          = {'n':{}, 's':{}, 'e':{}, 'w':{}} 
        self.shade_depth_v1         = {'n':{}, 's':{}, 'e':{}, 'w':{}} 
        self.shade_depth_v2         = {'n':{}, 's':{}, 'e':{}, 'w':{}} 
        self.wwr                    = {'n':{}, 's':{}, 'e':{}, 'w':{}} 
        self.wall_embodied          = None
        self.window_embodied        = None
        self.shading_embodied       = None

    @classmethod
    def from_data(cls, data):
        env = cls()
        env.data = data
        return env

    @classmethod
    def from_geometry(cls,
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

        env = cls()
        env.opaque_areas           = opaque_areas
        env.window_areas           = window_areas
        env.external_insulation    = external_insulation
        env.insulation_thickness   = insulation_thickness
        env.facade_cladding        = facade_cladding
        env.glazing_system         = glazing_system
        env.height                 = height
        env.shade_depth_h          = shade_depth_h
        env.shade_depth_v1         = shade_depth_v1
        env.shade_depth_v2         = shade_depth_v2
        env.wwr                    = wwr
        return env

    @property
    def data(self):
        data = {
            'opaque_areas'              : {repr(key): {} for key in ['n', 's', 'e', 'w']},
            'window_areas'              : {repr(key): {} for key in ['n', 's', 'e', 'w']},
            'external_insulation'       : self.external_insulation,
            'insulation_thickness'      : self.insulation_thickness,
            'facade_cladding'           : self.facade_cladding,
            'glazing_system'            : self.glazing_system,
            'height'                    : self.height,
            'shade_depth_h'             : {repr(key): {} for key in ['n', 's', 'e', 'w']},
            'shade_depth_v1'            : {repr(key): {} for key in ['n', 's', 'e', 'w']},
            'shade_depth_v2'            : {repr(key): {} for key in ['n', 's', 'e', 'w']},
            'wwr'                       : {repr(key): {} for key in ['n', 's', 'e', 'w']},
            'wall_embodied'             : self.wall_embodied,
            'window_embodied'           : self.window_embodied,
            'shading_embodied'          : self.shading_embodied,
        }

        for okey in self.shade_depth_h:
            data['shade_depth_h'][repr(okey)] = self.shade_depth_h[okey]

        for okey in self.shade_depth_v1:
            data['shade_depth_v1'][repr(okey)] = self.shade_depth_v1[okey]
        
        for okey in self.shade_depth_v2:
            data['shade_depth_v2'][repr(okey)] = self.shade_depth_v2[okey]

        for okey in self.wwr:
            data['wwr'][repr(okey)] = self.wwr[okey]

        for okey in self.opaque_areas:
            for zkey in self.opaque_areas[okey]:
                data['opaque_areas'][repr(okey)][repr(zkey)] = self.opaque_areas[okey][zkey]

        for okey in self.window_areas:
            for zkey in self.window_areas[okey]:
                data['window_areas'][repr(okey)][repr(zkey)] = self.window_areas[okey][zkey]

        return data

    @data.setter
    def data(self, data):
        opaque_areas                = data.get('opaque_areas') or {}
        window_areas                = data.get('window_areas') or {}
        self.external_insulation    = data.get('external_insulation') or {}
        self.insulation_thickness   = data.get('insulation_thickness') or {}
        self.facade_cladding        = data.get('facade_cladding') or {}
        self.glazing_system         = data.get('glazing_system') or {}
        self.height                 = data.get('height') or {}
        shade_depth_h               = data.get('shade_depth_h') or {}
        shade_depth_v1              = data.get('shade_depth_v1') or {}
        shade_depth_v2              = data.get('shade_depth_v2') or {}
        wwr                         = data.get('wwr') or {} 
        self.wall_embodied          = data.get('wall_embodied') or {}
        self.window_embodied        = data.get('window_embodied') or {}
        self.shading_embodied       = data.get('shading_embodied') or {}

        for okey in opaque_areas:
            for zkey in opaque_areas[okey]:
                self.opaque_areas[literal_eval(okey)][literal_eval(zkey)] = opaque_areas[okey][zkey]

        for okey in window_areas:
            for zkey in window_areas[okey]:
                self.window_areas[literal_eval(okey)][literal_eval(zkey)] = window_areas[okey][zkey]

        for okey in wwr:
            self.wwr[literal_eval(okey)] = wwr[okey]

        for okey in shade_depth_h:
            self.shade_depth_h[literal_eval(okey)] = shade_depth_h[okey]

        for okey in shade_depth_v1:
            self.shade_depth_v1[literal_eval(okey)] = shade_depth_v1[okey]

        for okey in shade_depth_v2:
            self.shade_depth_v2[literal_eval(okey)] = shade_depth_v2[okey]

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